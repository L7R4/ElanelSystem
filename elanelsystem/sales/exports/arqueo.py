# sales/exports/arqueo.py
from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from django.db.models import CharField
from django.db.models.functions import Concat, Substr

from elanelsystem.services.exports_pdfs import ColumnSpec, ExportSpec, export_response

from sales.models import ArqueoCaja, PagoCannon, MovimientoExterno
from sales.views import _format_money
from sales.services.caja_query import _build_resumen_metodos


# ---------------------------
# Helpers visuales (PDF)
# ---------------------------

def _safe_str(v) -> str:
    return ("" if v is None else str(v)).strip()

def _ellipsize(s: str, max_len: int = 64) -> str:
    s = _safe_str(s)
    if len(s) <= max_len:
        return s
    return s[: max(0, max_len - 1)].rstrip() + "…"

def _hora_from_fecha(fecha: str) -> str:
    """
    fecha suele venir como "dd/mm/yyyy HH:MM" o "dd/mm/yyyy"
    en el PDF del arqueo (mismo día), conviene mostrar solo la hora.
    """
    s = _safe_str(fecha)
    if not s:
        return "-"
    parts = s.split()
    if len(parts) >= 2:
        return parts[1][:5] or "-"
    return s[:10]  # fallback

def _annotate_fecha_key(qs):
    # asume string "dd/mm/yyyy ..." (dd/mm/yyyy siempre arranca al inicio)
    return qs.annotate(
        fecha_key=Concat(
            Substr("fecha", 7, 4),  # yyyy
            Substr("fecha", 4, 2),  # mm
            Substr("fecha", 1, 2),  # dd
            output_field=CharField(),
        )
    )


# ---------------------------
# Rows (compactos para portrait)
# ---------------------------

def _iter_caja_rows(pagos_qs, externos_qs) -> Iterable[Dict[str, object]]:
    pagos_qs = _annotate_fecha_key(pagos_qs)
    externos_qs = _annotate_fecha_key(externos_qs)

    p_iter = (
        pagos_qs.values(
            "id",
            "fecha_key",
            "fecha",
            "nro_cuota",
            "nro_recibo",
            "monto",
            "venta__nro_cliente__nombre",
            "metodo_pago__alias",
        )
        .order_by("-fecha_key", "-id")
        .iterator(chunk_size=2000)
    )

    e_iter = (
        externos_qs.values(
            "id",
            "fecha_key",
            "fecha",
            "movimiento",
            "dinero",
            "concepto",
            "nroComprobante",
            "metodoPago__alias",
        )
        .order_by("-fecha_key", "-id")
        .iterator(chunk_size=2000)
    )

    p = next(p_iter, None)
    e = next(e_iter, None)

    def k(x):
        if not x:
            return ("", -1)
        return (str(x.get("fecha_key") or ""), int(x.get("id") or 0))

    while p is not None or e is not None:
        kp = k(p)
        ke = k(e)

        take_pago = False
        if e is None:
            take_pago = True
        elif p is None:
            take_pago = False
        else:
            take_pago = kp >= ke  # DESC

        if take_pago:
            nombre = _safe_str(p.get("venta__nro_cliente__nombre") or "Pago")
            nro_recibo = _safe_str(p.get("nro_recibo"))
            metodo = _safe_str(p.get("metodo_pago__alias") or "")

            # Concepto compacto (incluye método y recibo)
            # Ej: "Juan Perez · Efectivo · R123"
            parts = [nombre]
            if metodo:
                parts.append(metodo)
            if nro_recibo:
                parts.append(f"R{nro_recibo}")
            concepto_pdf = _ellipsize(" · ".join(parts), 70)

            nro_cuota_val = p.get("nro_cuota") if p.get("nro_cuota") is not None else "-"

            yield {
                "hora": _hora_from_fecha(p.get("fecha") or ""),
                "mov": "Ing",
                "concepto_pdf": concepto_pdf,
                "nro_cuota": nro_cuota_val,
                "ingreso": _format_money(p.get("monto") or 0),
                "egreso": "-",
            }
            p = next(p_iter, None)

        else:
            mov_raw = _safe_str(e.get("movimiento") or "")
            mov = mov_raw.capitalize() if mov_raw else "-"
            is_ing = mov.lower() == "ingreso"
            monto = e.get("dinero") or 0

            concepto = _safe_str(e.get("concepto") or "Movimiento externo")
            metodo = _safe_str(e.get("metodoPago__alias") or "")
            comp = _safe_str(e.get("nroComprobante") or "")

            # Ej: "Compra insumos · Efectivo · C123"
            parts = [concepto]
            if metodo:
                parts.append(metodo)
            if comp:
                parts.append(f"C{comp}")
            concepto_pdf = _ellipsize(" · ".join(parts), 70)

            yield {
                "hora": _hora_from_fecha(e.get("fecha") or ""),
                "mov": "Ing" if is_ing else "Egr",
                "concepto_pdf": concepto_pdf,
                "nro_cuota": "-",
                "ingreso": _format_money(monto) if is_ing else "-",
                "egreso": _format_money(monto) if not is_ing else "-",
            }
            e = next(e_iter, None)


# ---------------------------
# Querysets del día
# ---------------------------

def _qs_movs_del_dia(agencia_id: int, fecha_fragment_ddmmyyyy: str):
    pagos_qs = (
        PagoCannon.objects.select_related(
            "venta", "venta__nro_cliente", "venta__agencia", "metodo_pago", "cobrador"
        )
        .filter(
            venta__agencia_id=agencia_id,
            fecha__icontains=fecha_fragment_ddmmyyyy,
        )
    )

    externos_qs = (
        MovimientoExterno.objects.select_related("metodoPago", "agencia", "ente")
        .filter(
            agencia_id=agencia_id,
            fecha__icontains=fecha_fragment_ddmmyyyy,
        )
    )

    return pagos_qs, externos_qs


# ---------------------------
# Summary (más “lindo”)
# ---------------------------

def _detalle_billetes_to_summary(detalle: dict) -> List[Tuple[str, str]]:
    if not isinstance(detalle, dict):
        return []

    denoms: List[int] = []
    for k in detalle.keys():
        if isinstance(k, str) and k.startswith("p"):
            try:
                denoms.append(int(k[1:]))
            except Exception:
                pass

    out: List[Tuple[str, str]] = []
    for d in sorted(set(denoms), reverse=True):
        item = detalle.get(f"p{d}") or {}
        cant = int(item.get("cantidad", 0) or 0)
        imp = item.get("importeTotal", 0) or 0
        if cant == 0 and (imp == 0 or imp == "0"):
            continue
        # izquierda: denominación, derecha: "cant x denom = total"
        out.append((f"$ {d}", f"{cant}  ×  {d}  =  {_format_money(imp)}"))
    return out


def _resumen_metodos_to_summary(pagos_qs, externos_qs) -> List[Tuple[str, str]]:
    """
    Usa tu helper existente (mismo que caja) y lo pega como sección.
    """
    rows = _build_resumen_metodos(pagos_qs, externos_qs) or []
    out: List[Tuple[str, str]] = []
    for r in rows:
        vn = _safe_str(r.get("verbose_name"))
        money = _safe_str(r.get("money"))
        if not vn:
            continue
        out.append((vn, f"$ {money}" if money and not str(money).strip().startswith("$") else money))
    return out


def arqueo_export_spec(arqueo: ArqueoCaja, pagos_qs, externos_qs) -> ExportSpec:
    summary: List[Tuple[str, str]] = [
        ("ARQUEO", ""),
        ("Agencia", str(arqueo.agencia) if arqueo.agencia else "-"),
        ("Fecha", arqueo.fecha or "-"),
        ("Admin", arqueo.admin or "-"),
        ("Responsable", arqueo.responsable or "-"),
        ("", ""),
        ("TOTALES", ""),
        ("Total Planilla de Efectivo", _format_money(arqueo.totalPlanilla or 0)),
        ("Saldo según diario de caja", _format_money(arqueo.totalSegunDiarioCaja or 0)),
        ("Diferencia", _format_money(arqueo.diferencia or 0)),
    ]

    obs = _safe_str(arqueo.observaciones or "")
    if obs:
        summary.extend([("", ""), ("Observaciones", _ellipsize(obs, 120))])

    # Detalle efectivo
    detalle_rows = _detalle_billetes_to_summary(arqueo.detalle or {})
    summary.extend([("", ""), ("DETALLE EFECTIVO", "")])
    summary.extend(detalle_rows if detalle_rows else [("—", "Sin detalle")])

    # Resumen por método (del día)
    resumen_metodos = _resumen_metodos_to_summary(pagos_qs, externos_qs)
    summary.extend([("", ""), ("RESUMEN POR MÉTODO", "")])
    summary.extend(resumen_metodos if resumen_metodos else [("—", "Sin movimientos")])

    # ✅ columnas compactas para A4 portrait (evita landscape)
    cols = [
        ColumnSpec("hora", "Hora"),
        ColumnSpec("mov", "Mov."),
        ColumnSpec("concepto_pdf", "Concepto"),
        ColumnSpec("nro_cuota", "Cuota"),
        ColumnSpec("ingreso", "Ingreso"),
        ColumnSpec("egreso", "Egreso"),
    ]

    return ExportSpec(
        title="Arqueo de Caja",
        columns=cols,
        summary=summary,
    )


# ---------------------------
# Export
# ---------------------------

def export_arqueo_pdf(request, arqueo: ArqueoCaja, timeout_sec: int = 300):
    fecha_fragment = (arqueo.fecha or "")[:10]  # dd/mm/yyyy
    agencia_id = int(arqueo.agencia_id or 0)

    pagos_qs, externos_qs = _qs_movs_del_dia(agencia_id, fecha_fragment)

    spec = arqueo_export_spec(arqueo, pagos_qs, externos_qs)
    rows = _iter_caja_rows(pagos_qs, externos_qs)

    filename_base = f"Arqueo_Caja_{fecha_fragment.replace('/','-')}_Ag{agencia_id}"

    resp = export_response("pdf", spec, rows, filename_base=filename_base, timeout_sec=timeout_sec)

    # Nombre visible en visor / pestaña (según viewer)
    resp["Content-Disposition"] = f'inline; filename="{filename_base}.pdf"'
    return resp
