from typing import Dict, Iterable, List, Tuple
from django.db.models import CharField
from django.db.models.functions import Substr, Concat

from elanelsystem.services.exports_excels import (
    ColumnSpec as cp_excel,
    ExportSpec as es_excel,
    export_response as er_excel,
)

from elanelsystem.services.exports_pdfs import (
    ColumnSpec as cp_pdf,
    ExportSpec as es_pdf,
    export_response as er_pdf,
)

from sales.services.caja_query import _movs_pagos_filtered_qs, _build_resumen_metodos, _format_money


def _annotate_fecha_key(qs):
    return qs.annotate(
        fecha_key=Concat(
            Substr("fecha", 7, 4),
            Substr("fecha", 4, 2),
            Substr("fecha", 1, 2),
            output_field=CharField(),
        )
    )


def iter_caja_rows_base(pagos_qs, externos_qs) -> Iterable[Dict[str, object]]:
    pagos_qs = _annotate_fecha_key(pagos_qs)
    externos_qs = _annotate_fecha_key(externos_qs)

    p_iter = (
        pagos_qs.values(
            "id", "fecha_key", "fecha", "nro_cuota", "nro_recibo", "monto",
            "venta__nro_cliente__nombre",
            "venta__agencia__pseudonimo",
            "metodo_pago__alias",
            "cobrador__alias",
        )
        .order_by("-fecha_key", "-id")
        .iterator(chunk_size=2000)
    )

    e_iter = (
        externos_qs.values(
            "id", "fecha_key", "fecha", "movimiento", "dinero", "concepto", "nroComprobante",
            "metodoPago__alias",
            "agencia__pseudonimo",
            "ente__alias",
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

        if e is None:
            take_pago = True
        elif p is None:
            take_pago = False
        else:
            take_pago = kp >= ke

        if take_pago:
            nombre = (p.get("venta__nro_cliente__nombre") or "Pago").strip()
            nro_recibo = p.get("nro_recibo")
            concepto = f"{nombre} (Recibo {nro_recibo})" if nro_recibo else nombre

            # OJO: acá todavía dejamos nro_cuota raw, se ajusta en cada iter (pdf/xlsx)
            nro_cuota_raw = p.get("nro_cuota")

            yield {
                "fecha": p.get("fecha") or "",
                "origen": "Pago Cannon",
                "movimiento": "Ingreso",
                "concepto": concepto,
                "nro_cuota_raw": nro_cuota_raw,
                "ingreso": _format_money(p.get("monto") or 0),
                "egreso": "-",
                "metodo": p.get("metodo_pago__alias") or "-",
                "tipo_caja": p.get("venta__agencia__pseudonimo") or "-",
                "ente": p.get("cobrador__alias") or "-",
                "comprobante": nro_recibo or "-",
            }
            p = next(p_iter, None)
        else:
            mov = (e.get("movimiento") or "").strip().capitalize() or "-"
            is_ing = mov.lower() == "ingreso"
            monto = e.get("dinero") or 0

            yield {
                "fecha": e.get("fecha") or "",
                "origen": "Movimiento externo",
                "movimiento": mov,
                "concepto": e.get("concepto") or "-",
                "nro_cuota_raw": None,
                "ingreso": _format_money(monto) if is_ing else "-",
                "egreso": _format_money(monto) if not is_ing else "-",
                "metodo": e.get("metodoPago__alias") or "-",
                "tipo_caja": e.get("agencia__pseudonimo") or "-",
                "ente": e.get("ente__alias") or "-",
                "comprobante": e.get("nroComprobante") or "-",
            }
            e = next(e_iter, None)


def _summary_pairs(pagos_qs, externos_qs) -> List[Tuple[str, str]]:
    resumen = _build_resumen_metodos(pagos_qs, externos_qs) or []
    return [(r.get("verbose_name", ""), r.get("money", "")) for r in resumen]


# ---------------------------
# PDF: diseño “que entre”
# ---------------------------

def _pdf_wrap(s: str) -> str:
    s = (s or "").strip()
    return s

def _break_comma(s: str) -> str:
    s = (s or "").strip()
    return s.replace(", ", "\n") if s else s

def _break_first_space(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return s
    if " " in s:
        a, b = s.split(" ", 1)
        return f"{a}\n{b}"
    return s

def _wrap_recibo(concepto: str) -> str:
    concepto = (concepto or "").strip()
    if " (Recibo " in concepto:
        return concepto.replace(" (Recibo ", "\n(Recibo ")
    return concepto

def iter_caja_rows_pdf(pagos_qs, externos_qs) -> Iterable[Dict[str, object]]:
    for r in iter_caja_rows_base(pagos_qs, externos_qs):
        nro = r.get("nro_cuota_raw")

        # ✅ IMPORTANTÍSIMO: si es 0, mandalo como "0" (string) para que no desaparezca
        nro_cuota = "-" if nro is None else str(nro)

        fecha = _pdf_wrap(r.get("fecha", ""))
        # reduce ancho: fecha en 2 líneas si tiene hora
        if " " in fecha:
            fecha = fecha.replace(" ", "\n", 1)

        out = {
            "fecha": fecha,
            # más corto para que entre
            "origen": "Cannon" if r.get("origen") == "Pago Cannon" else "Externo",
            "movimiento": r.get("movimiento") or "-",
            "concepto": _wrap_recibo(r.get("concepto") or "-"),
            "nro_cuota": nro_cuota,
            "ingreso": r.get("ingreso") or "-",
            "egreso": r.get("egreso") or "-",
            # métodos largos en 2 líneas (Mercado pago)
            "metodo": _break_first_space(r.get("metodo") or "-"),
            # tipo_caja con coma en 2 líneas (Corrientes\nCorrientes)
            "tipo_caja": _break_comma(r.get("tipo_caja") or "-"),
            # ente en 2 líneas si es largo
            "ente": _break_first_space(r.get("ente") or "-"),
            # NO mandamos comprobante al PDF (se cortaba y es redundante)
        }
        yield out


def caja_export_spec_pdf(pagos_qs, externos_qs) -> es_pdf:
    cols = [
        cp_pdf("fecha", "Fecha"),
        cp_pdf("origen", "Origen"),
        cp_pdf("movimiento", "Mov."),
        cp_pdf("concepto", "Concepto"),
        cp_pdf("nro_cuota", "Cuota"),
        cp_pdf("ingreso", "Ingreso"),
        cp_pdf("egreso", "Egreso"),
        cp_pdf("metodo", "Método"),
        cp_pdf("tipo_caja", "Caja"),
        cp_pdf("ente", "Ente"),
    ]

    return es_pdf(
        title="Informe de Caja",
        columns=cols,
        summary=_summary_pairs(pagos_qs, externos_qs),
    )


# ---------------------------
# XLSX: completo (con comprobante)
# ---------------------------

def iter_caja_rows_xlsx(pagos_qs, externos_qs) -> Iterable[Dict[str, object]]:
    for r in iter_caja_rows_base(pagos_qs, externos_qs):
        nro = r.get("nro_cuota_raw")
        # en excel podés dejar número o string; si querés número real, dejá nro tal cual
        nro_cuota = "-" if nro is None else nro

        yield {
            "fecha": r.get("fecha") or "",
            "origen": r.get("origen") or "-",
            "movimiento": r.get("movimiento") or "-",
            "concepto": r.get("concepto") or "-",
            "nro_cuota": nro_cuota,
            "ingreso": r.get("ingreso") or "-",
            "egreso": r.get("egreso") or "-",
            "metodo": r.get("metodo") or "-",
            "tipo_caja": r.get("tipo_caja") or "-",
            "ente": r.get("ente") or "-",
            "comprobante": r.get("comprobante") or "-",
        }


def caja_export_spec_xlsx(pagos_qs, externos_qs) -> es_excel:
    cols = [
        cp_excel("fecha", "Fecha"),
        cp_excel("origen", "Origen"),
        cp_excel("movimiento", "Movimiento"),
        cp_excel("concepto", "Concepto"),
        cp_excel("nro_cuota", "N° Cuota"),
        cp_excel("ingreso", "Ingreso"),
        cp_excel("egreso", "Egreso"),
        cp_excel("metodo", "Método"),
        cp_excel("tipo_caja", "Tipo de caja"),
        cp_excel("ente", "Ente recaud."),
        cp_excel("comprobante", "Comprobante"),
    ]

    return es_excel(
        title="Informe de Caja",
        columns=cols,
        summary=_summary_pairs(pagos_qs, externos_qs),
    )


def export_caja(request, fmt: str, timeout_sec: int = 300):
    pagos_qs, externos_qs = _movs_pagos_filtered_qs(request)

    f = (fmt or "").strip().lower()
    filename_base = "Informe de Caja"

    if f in ("xlsx", "excel"):
        spec = caja_export_spec_xlsx(pagos_qs, externos_qs)
        rows = iter_caja_rows_xlsx(pagos_qs, externos_qs)
        return er_excel(
            "xlsx",
            spec,
            rows,
            filename_base=filename_base,
            timeout_sec=timeout_sec,
        )

    # default PDF
    spec = caja_export_spec_pdf(pagos_qs, externos_qs)
    rows = iter_caja_rows_pdf(pagos_qs, externos_qs)
    return er_pdf(
        "pdf",
        spec,
        rows,
        filename_base=filename_base,
        timeout_sec=timeout_sec,
    )
