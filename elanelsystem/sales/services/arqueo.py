from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

from django.db.models import Q, Sum, FloatField, Value
from django.db.models.functions import Coalesce

from sales.models import PagoCannon, MovimientoExterno, Sucursal


BILLETES: List[int] = [20000, 10000, 2000, 1000, 500, 200, 100, 50, 20, 10]

# Métodos que consideramos "caja efectivo"
CASH_METHOD_ALIASES = ("efectivo", "contado")


def today_fragment_ddmmyyyy() -> str:
    # dd/mm/yyyy (para buscar en CharField fecha)
    return datetime.now().strftime("%d/%m/%Y")


def _q_cash_metodo(field_prefix: str) -> Q:
    """
    Construye Q(... OR ...) para metodo alias efectivo/contado.
    field_prefix: "metodo_pago" o "metodoPago"
    """
    q = Q()
    for a in CASH_METHOD_ALIASES:
        q |= Q(**{f"{field_prefix}__alias__iexact": a})
    return q


def get_allowed_agencias(request) -> List[Sucursal]:
    try:
        if getattr(request.user, "is_superuser", False):
            return list(Sucursal.objects.all())
        return list(request.user.sucursales.all())
    except Exception:
        return []


def validate_agencia_allowed(request, agencia_id: int) -> Optional[Sucursal]:
    allowed = get_allowed_agencias(request)
    for s in allowed:
        if int(s.id) == int(agencia_id):
            return s
    return None


def movs_del_dia_qs(agencia_id: int, fecha_ddmmyyyy: str):
    """Pagos de cuotas cobrados en la sucursal y movimientos externos de la sucursal en ese día."""
    pagos_qs = (
        PagoCannon.objects
        .select_related("venta", "venta__nro_cliente", "venta__agencia", "metodo_pago", "cobrador", "responsable_pago")
        .filter(sucursal_cobro_id=agencia_id, fecha__startswith=fecha_ddmmyyyy)
    )
    externos_qs = (
        MovimientoExterno.objects
        .select_related("metodoPago", "agencia", "ente")
        .filter(agencia_id=agencia_id, fecha__startswith=fecha_ddmmyyyy)
    )
    return pagos_qs, externos_qs


def _es_efectivo(alias: Optional[str]) -> bool:
    return (alias or "").strip().lower() in CASH_METHOD_ALIASES


def get_diario_caja(agencia_id: int, fecha_ddmmyyyy: Optional[str] = None) -> Dict[str, Any]:
    """
    Diario de caja del día: cada pago impactado y cada movimiento externo, sin carga manual.
    Devuelve los movimientos ordenados por hora y los totales (general, por método y en efectivo).
    """
    dia = (fecha_ddmmyyyy or "").strip() or today_fragment_ddmmyyyy()
    pagos_qs, externos_qs = movs_del_dia_qs(agencia_id, dia)

    movimientos: List[Dict[str, Any]] = []
    for p in pagos_qs:
        venta = p.venta
        cliente = getattr(venta, "nro_cliente", None)
        movimientos.append({
            "origen": "pago",
            "id": p.id,
            "fecha": p.fecha,
            "hora": (p.fecha or "")[11:16],
            "concepto": f"Cuota {p.nro_cuota}" if p.nro_cuota else "Inscripción",
            "nro_recibo": p.nro_recibo,
            "venta_id": venta.id,
            "nro_operacion": venta.nro_operacion,
            "cliente": getattr(cliente, "nombre", "") or "",
            "nro_cuota": p.nro_cuota,
            "metodo_pago": p.metodo_pago.alias if p.metodo_pago else "",
            "cobrador": p.cobrador.alias if p.cobrador else "",
            "responsable": p.responsable_pago.nombre if p.responsable_pago else "",
            "moneda": p.moneda,
            "monto_usd": p.monto_usd,
            "ingreso": float(p.monto or 0),
            "egreso": 0.0,
        })

    for e in externos_qs:
        es_ingreso = (e.movimiento or "").strip().lower() == "ingreso"
        monto = float(e.dinero or 0)
        movimientos.append({
            "origen": "externo",
            "id": e.id,
            "fecha": e.fecha,
            "hora": (e.fecha or "")[11:16],
            "concepto": e.concepto or "",
            "nro_recibo": e.nroComprobante or "",
            "venta_id": None,
            "nro_operacion": None,
            "cliente": e.denominacion or (e.ente.alias if e.ente else ""),
            "nro_cuota": None,
            "metodo_pago": e.metodoPago.alias if e.metodoPago else "",
            "cobrador": e.ente.alias if e.ente else "",
            "responsable": "",
            "moneda": e.tipoMoneda or "ARS",
            "monto_usd": None,
            "ingreso": monto if es_ingreso else 0.0,
            "egreso": 0.0 if es_ingreso else monto,
        })

    movimientos.sort(key=lambda m: (m["hora"], m["origen"], m["id"]))

    por_metodo: Dict[str, Dict[str, float]] = {}
    for m in movimientos:
        t = por_metodo.setdefault(m["metodo_pago"] or "Sin método", {"ingresos": 0.0, "egresos": 0.0, "neto": 0.0})
        t["ingresos"] += m["ingreso"]
        t["egresos"] += m["egreso"]
        t["neto"] += m["ingreso"] - m["egreso"]

    ingresos = sum(m["ingreso"] for m in movimientos)
    egresos = sum(m["egreso"] for m in movimientos)
    efectivo = sum(m["ingreso"] - m["egreso"] for m in movimientos if _es_efectivo(m["metodo_pago"]))

    return {
        "agencia_id": agencia_id,
        "fecha": dia,
        "movimientos": movimientos,
        "totales": {
            "ingresos": ingresos,
            "egresos": egresos,
            "neto": ingresos - egresos,
            "efectivo": efectivo,
            "por_metodo": por_metodo,
        },
    }


def compute_saldo_diario_caja(agencia_id: int, fecha_ddmmyyyy: Optional[str] = None) -> float:
    """Efectivo neto del día según el diario de caja (ingresos - egresos en efectivo/contado)."""
    dia = (fecha_ddmmyyyy or today_fragment_ddmmyyyy()).strip() or today_fragment_ddmmyyyy()

    pagos_qs, externos_qs = movs_del_dia_qs(agencia_id, dia)
    pagos_qs = pagos_qs.filter(_q_cash_metodo("metodo_pago"))
    externos_qs = externos_qs.filter(_q_cash_metodo("metodoPago"))

    pagos_total = float(
        pagos_qs.aggregate(
            total=Coalesce(
                Sum("monto", output_field=FloatField()),
                Value(0.0),
                output_field=FloatField(),
            )
        )["total"] or 0.0
    )

    ext_ing = float(
        externos_qs.filter(movimiento__iexact="ingreso").aggregate(
            total=Coalesce(
                Sum("dinero", output_field=FloatField()),
                Value(0.0),
                output_field=FloatField(),
            )
        )["total"] or 0.0
    )

    ext_egr = float(
        externos_qs.filter(movimiento__iexact="egreso").aggregate(
            total=Coalesce(
                Sum("dinero", output_field=FloatField()),
                Value(0.0),
                output_field=FloatField(),
            )
        )["total"] or 0.0
    )

    return pagos_total + ext_ing - ext_egr
