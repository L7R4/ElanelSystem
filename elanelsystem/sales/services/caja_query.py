from datetime import datetime
import re
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce

from sales.models import PagoCannon, MovimientoExterno, Sucursal
from sales.utils import formatear_moneda_sin_centavos  # ajustá esta ruta

def _parse_int(value, default=None):
    try:
        return int(value)
    except Exception:
        return default


def _parse_int_list(value: str):
    if not value:
        return []
    out = []
    for part in re.split(r"[,\-]", str(value)):
        part = part.strip()
        if not part:
            continue
        try:
            out.append(int(part))
        except Exception:
            pass
    return out


def _normalize_fecha_fragment(fecha_raw: str) -> str:
    """Devuelve un fragmento comparable con los campos CharField fecha (dd/mm/yyyy...).

    - Si viene YYYY-MM-DD -> DD/MM/YYYY
    - Si viene DD/MM/YYYY o DD/MM/YYYY HH:MM -> usa DD/MM/YYYY
    - Si viene vacío -> ""
    """
    if not fecha_raw:
        return ""
    s = str(fecha_raw).strip()
    if not s:
        return ""

    # YYYY-MM-DD
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", s)
    if m:
        y, mo, d = m.group(1), m.group(2), m.group(3)
        return f"{d}/{mo}/{y}"

    # DD/MM/YYYY ...
    m = re.match(r"^(\d{2})/(\d{2})/(\d{4})", s)
    if m:
        return f"{m.group(1)}/{m.group(2)}/{m.group(3)}"

    return s


def _parse_fecha_to_dt(fecha_str: str):
    """Parsea fechas que suelen venir como string: dd/mm/yyyy hh:mm o dd/mm/yyyy.
    Devuelve datetime (naive). Si falla, datetime.min.
    """
    if not fecha_str:
        return datetime.min
    s = str(fecha_str).strip()
    for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    return datetime.min


def _get_allowed_agencia_ids(request):
    """IDs de sucursales permitidas para el usuario."""
    try:
        if getattr(request.user, "is_superuser", False):
            return list(Sucursal.objects.values_list("id", flat=True))
        return list(request.user.sucursales.values_list("id", flat=True))
    except Exception:
        return []


def _format_money(v):
    try:
        return f"${formatear_moneda_sin_centavos(v)}"
    except Exception:
        try:
            return f"${v}"
        except Exception:
            return "-"

def _build_resumen_metodos(pagos_qs, externos_qs):
    resumen_map = {}

    for r in pagos_qs.values("metodo_pago_id", "metodo_pago__alias").annotate(
        ingreso=Coalesce(Sum("monto"), 0)
    ):
        mid = r.get("metodo_pago_id")
        alias = r.get("metodo_pago__alias") or "Sin método"
        key = f"mp-{mid}" if mid else "mp-none"
        resumen_map[key] = {
            "verbose_name": alias,
            "name_clean": alias.replace(" ", "_").lower() + "_total_money",
            "ingreso_value": float(r.get("ingreso") or 0),
            "egreso_value": 0.0,
        }

    for r in externos_qs.values("metodoPago_id", "metodoPago__alias").annotate(
        ingreso=Coalesce(Sum("dinero", filter=Q(movimiento__iexact="ingreso")), 0.0),
        egreso=Coalesce(Sum("dinero", filter=Q(movimiento__iexact="egreso")), 0.0),
    ):
        mid = r.get("metodoPago_id")
        alias = r.get("metodoPago__alias") or "Sin método"
        key = f"mp-{mid}" if mid else "mp-none"
        if key not in resumen_map:
            resumen_map[key] = {
                "verbose_name": alias,
                "name_clean": alias.replace(" ", "_").lower() + "_total_money",
                "ingreso_value": 0.0,
                "egreso_value": 0.0,
            }
        resumen_map[key]["ingreso_value"] += float(r.get("ingreso") or 0)
        resumen_map[key]["egreso_value"] += float(r.get("egreso") or 0)

    metodos = []
    total = 0.0
    for item in sorted(resumen_map.values(), key=lambda x: (x.get("verbose_name") or "")):
        neto = float(item["ingreso_value"]) - float(item["egreso_value"])
        total += neto
        metodos.append({
            "verbose_name": item["verbose_name"],
            "name_clean": item["name_clean"],
            "money": formatear_moneda_sin_centavos(neto),
        })

    metodos.append({
        "verbose_name": "Total",
        "name_clean": "total_money",
        "money": formatear_moneda_sin_centavos(total),
    })
    return metodos


def _row_from_pago(p: PagoCannon):
    cliente_nombre = ""
    nro_cliente = ""
    nro_operacion = ""
    agencia = ""
    campania = ""
    try:
        if p.venta_id and p.venta:
            nro_operacion = getattr(p.venta, "nro_operacion", "")
            agencia = getattr(getattr(p.venta, "agencia", None), "pseudonimo", "")
            campania = getattr(p.venta, "campania", "")
            if getattr(p.venta, "nro_cliente", None):
                cliente_nombre = getattr(p.venta.nro_cliente, "nombre", "")
                nro_cliente = getattr(p.venta.nro_cliente, "nro_cliente", "")
    except Exception:
        pass

    # ✅ Concepto SOLO: Nombre + (Recibo ...)
    concepto = (cliente_nombre or "Pago").strip()
    if p.nro_recibo:
        concepto = f"{concepto} (Recibo {p.nro_recibo})"

    # ✅ cuota 0 NO se convierte en "-"
    nro_cuota_val = p.nro_cuota if p.nro_cuota is not None else "-"

    dt = _parse_fecha_to_dt(p.fecha)
    monto = int(p.monto or 0)

    return dt, {
        "id": f"pago-{p.id}",
        "kind": "pago",
        "pk": p.id,
        "fecha": p.fecha or "",
        "concepto": concepto,
        "nro_cuota": nro_cuota_val,
        "ingreso": _format_money(monto),
        "egreso": "-",
        "ingreso_value": monto,
        "egreso_value": 0,
        "metodo_pago": getattr(getattr(p, "metodo_pago", None), "alias", "") or "",
        "metodo_pago_id": getattr(p, "metodo_pago_id", None),
        "cobrador": getattr(getattr(p, "cobrador", None), "alias", "") or "",
        "cobrador_id": getattr(p, "cobrador_id", None),
        "agencia": agencia,
        "campania": campania,
        "nro_operacion": nro_operacion,
        "nro_cliente": nro_cliente,
        "cliente": cliente_nombre,
    }

def _row_from_externo(m: MovimientoExterno):
    tipo = (m.movimiento or "").strip().lower()
    monto = float(m.dinero or 0)
    is_ingreso = tipo == "ingreso"

    dt = _parse_fecha_to_dt(m.fecha)
    return dt, {
        "id": f"externo-{m.id}",
        "kind": "externo",
        "pk": m.id,
        "fecha": m.fecha or "",
        "concepto": m.concepto or "",
        "nro_cuota": "-",
        "ingreso": _format_money(monto) if is_ingreso else "-",
        "egreso": _format_money(monto) if not is_ingreso else "-",
        "ingreso_value": monto if is_ingreso else 0,
        "egreso_value": monto if not is_ingreso else 0,
        "tipo_mov": tipo,
        "metodo_pago": getattr(getattr(m, "metodoPago", None), "alias", "") or "",
        "metodo_pago_id": getattr(m, "metodoPago_id", None),
        "cobrador": getattr(getattr(m, "ente", None), "alias", "") or "",
        "agencia": getattr(getattr(m, "agencia", None), "pseudonimo", "") or "",
        "campania": getattr(m, "campania", "") or "",
    }

def _movs_pagos_filtered_qs(request):
    search = (request.GET.get("search") or "").strip()
    fecha = _normalize_fecha_fragment(request.GET.get("fecha") or "")
    concepto = (request.GET.get("concepto") or "").strip()
    tipo_mov = (request.GET.get("tipo_mov") or "").strip().lower()
    nro_cuota = _parse_int(request.GET.get("nro_cuota"), None)
    monto_min = request.GET.get("monto_min")
    monto_max = request.GET.get("monto_max")
    metodo_pago_ids = _parse_int_list(request.GET.get("metodo_pago") or "")
    cobrador_ids = _parse_int_list(request.GET.get("cobrador") or "")

    allowed_agencias = set(_get_allowed_agencia_ids(request))
    requested_agencias = set(_parse_int_list(request.GET.get("agencia") or ""))
    agencia_ids = (
        list(requested_agencias.intersection(allowed_agencias))
        if requested_agencias
        else list(allowed_agencias)
    )

    origen = (request.GET.get("origen") or "").strip().lower()

    pagos_qs = PagoCannon.objects.none()
    externos_qs = MovimientoExterno.objects.none()

    # Base querysets reales
    base_pagos = (
        PagoCannon.objects
        .select_related(
            "venta",
            "venta__nro_cliente",
            "venta__agencia",
            "metodo_pago",
            "cobrador",
            "responsable_pago",
        )
        .filter(venta__agencia__id__in=agencia_ids)
    )

    base_externos = (
        MovimientoExterno.objects
        .select_related("metodoPago", "agencia", "ente")
        .filter(agencia__id__in=agencia_ids)
    )

    # ✅ Origen: "" => todos
    if not origen or origen in ("todos", "all", "todas"):
        pagos_qs = base_pagos
        externos_qs = base_externos
    elif origen in ("cannon", "cannons", "pago", "pagos"):
        pagos_qs = base_pagos
        externos_qs = MovimientoExterno.objects.none()
    elif origen in ("externo", "externos"):
        pagos_qs = PagoCannon.objects.none()
        externos_qs = base_externos
    else:
        # si viene algo raro, por seguridad tratamos como "todos"
        pagos_qs = base_pagos
        externos_qs = base_externos

    # --- tipo_mov (ingreso/egreso)
    if tipo_mov == "egreso":
        pagos_qs = pagos_qs.none()  # PagoCannon es ingreso
        externos_qs = externos_qs.filter(movimiento__iexact="egreso")
    elif tipo_mov == "ingreso":
        externos_qs = externos_qs.filter(movimiento__iexact="ingreso")

    # --- fecha
    if fecha:
        pagos_qs = pagos_qs.filter(fecha__icontains=fecha)
        externos_qs = externos_qs.filter(fecha__icontains=fecha)

    # --- nro_cuota (solo pagos)
    if nro_cuota is not None:
        pagos_qs = pagos_qs.filter(nro_cuota=nro_cuota)

    # --- concepto
    if concepto:
        pagos_qs = pagos_qs.filter(
            Q(venta__nro_cliente__nombre__icontains=concepto)
            | Q(nro_recibo__icontains=concepto)
            | Q(venta__nro_operacion__icontains=concepto)
        )
        externos_qs = externos_qs.filter(
            Q(concepto__icontains=concepto)
            | Q(denominacion__icontains=concepto)
            | Q(nroComprobante__icontains=concepto)
            | Q(nroIdentificacion__icontains=concepto)
        )

    # --- search global
    if search:
        pagos_qs = pagos_qs.filter(
            Q(venta__nro_cliente__nombre__icontains=search)
            | Q(venta__nro_operacion__icontains=search)
            | Q(nro_recibo__icontains=search)
        )
        externos_qs = externos_qs.filter(
            Q(concepto__icontains=search)
            | Q(denominacion__icontains=search)
            | Q(nroComprobante__icontains=search)
            | Q(nroIdentificacion__icontains=search)
        )

    # --- método de pago
    if metodo_pago_ids:
        pagos_qs = pagos_qs.filter(metodo_pago_id__in=metodo_pago_ids)
        externos_qs = externos_qs.filter(metodoPago_id__in=metodo_pago_ids)

    # --- cobrador / ente
    if cobrador_ids:
        pagos_qs = pagos_qs.filter(cobrador_id__in=cobrador_ids)
        externos_qs = externos_qs.filter(ente_id__in=cobrador_ids)

    # --- monto min/max
    try:
        if monto_min not in (None, ""):
            vmin = float(monto_min)
            pagos_qs = pagos_qs.filter(monto__gte=vmin)
            externos_qs = externos_qs.filter(dinero__gte=vmin)
    except Exception:
        pass

    try:
        if monto_max not in (None, ""):
            vmax = float(monto_max)
            pagos_qs = pagos_qs.filter(monto__lte=vmax)
            externos_qs = externos_qs.filter(dinero__lte=vmax)
    except Exception:
        pass

    return pagos_qs, externos_qs
