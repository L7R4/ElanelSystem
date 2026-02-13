import io
import os
import time
import signal
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from django.http import HttpResponse, JsonResponse

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib import colors

from openpyxl import Workbook


class ExportTimeout(Exception):
    pass


@dataclass(frozen=True)
class ColumnSpec:
    key: str
    label: str


@dataclass(frozen=True)
class ExportSpec:
    title: str
    columns: List[ColumnSpec]
    summary: Optional[List[Tuple[str, str]]] = None  # [(label, value)]


def _deadline(seconds: int) -> float:
    return time.monotonic() + seconds


def _check_deadline(deadline_ts: float):
    if time.monotonic() > deadline_ts:
        raise ExportTimeout("Timeout generando archivo (5 min). Ajustá filtros.")


def _sigalrm_handler(signum, frame):
    raise ExportTimeout("Timeout generando archivo (5 min). Ajustá filtros.")


def _with_timeout(seconds: int, fn: Callable[[], bytes]) -> bytes:
    deadline_ts = _deadline(seconds)

    use_alarm = (os.name == "posix") and hasattr(signal, "SIGALRM")
    old_handler = None

    if use_alarm:
        old_handler = signal.getsignal(signal.SIGALRM)
        signal.signal(signal.SIGALRM, _sigalrm_handler)
        signal.alarm(seconds)

    try:
        _check_deadline(deadline_ts)
        return fn()
    finally:
        if use_alarm:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)


def export_pdf_reportlab(
    spec: ExportSpec,
    rows_iter: Iterable[Dict[str, object]],
    timeout_sec: int = 300,
    chunk_size: int = 500,
) -> bytes:
    def _run() -> bytes:
        deadline_ts = _deadline(timeout_sec)

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=landscape(A4),
            leftMargin=10 * mm,
            rightMargin=10 * mm,
            topMargin=10 * mm,
            bottomMargin=10 * mm,
        )

        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph(spec.title, styles["Title"]))
        story.append(Spacer(1, 6))
        _check_deadline(deadline_ts)

        if spec.summary:
            summary_data = [["Concepto", "Valor"]]
            for k, v in spec.summary:
                summary_data.append([str(k), str(v)])

            t = Table(summary_data, hAlign="LEFT")
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]))
            story.append(t)
            story.append(Spacer(1, 10))

        headers = [c.label for c in spec.columns]
        keys = [c.key for c in spec.columns]

        chunk = [headers]
        i = 0

        for row in rows_iter:
            i += 1
            if i % 200 == 0:
                _check_deadline(deadline_ts)

            chunk.append([str(row.get(k, "") or "") for k in keys])

            if len(chunk) >= chunk_size + 1:
                _check_deadline(deadline_ts)
                table = Table(chunk, repeatRows=1)
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))
                story.append(table)
                story.append(PageBreak())
                chunk = [headers]

        if len(chunk) > 1:
            _check_deadline(deadline_ts)
            table = Table(chunk, repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(table)

        _check_deadline(deadline_ts)
        doc.build(story)
        return buf.getvalue()

    return _with_timeout(timeout_sec, _run)


def export_xlsx_openpyxl(
    spec: ExportSpec,
    rows_iter: Iterable[Dict[str, object]],
    timeout_sec: int = 300,
) -> bytes:
    def _run() -> bytes:
        deadline_ts = _deadline(timeout_sec)

        wb = Workbook(write_only=True)
        ws = wb.create_sheet(title="Informe")

        headers = [c.label for c in spec.columns]
        keys = [c.key for c in spec.columns]

        ws.append(headers)

        i = 0
        for row in rows_iter:
            i += 1
            if i % 500 == 0:
                _check_deadline(deadline_ts)

            ws.append([row.get(k, "") for k in keys])

        out = io.BytesIO()
        wb.save(out)
        return out.getvalue()

    return _with_timeout(timeout_sec, _run)


def export_response(
    fmt: str,
    spec: ExportSpec,
    rows_iter: Iterable[Dict[str, object]],
    filename_base: str = "Informe",
    timeout_sec: int = 300,
):
    f = (fmt or "").strip().lower()

    try:
        if f in ("pdf",):
            data = export_pdf_reportlab(spec, rows_iter, timeout_sec=timeout_sec)
            resp = HttpResponse(data, content_type="application/pdf")
            resp["Content-Disposition"] = f'inline; filename="{filename_base}.pdf"'
            return resp

        if f in ("xlsx", "excel"):
            data = export_xlsx_openpyxl(spec, rows_iter, timeout_sec=timeout_sec)
            resp = HttpResponse(
                data,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            resp["Content-Disposition"] = f'attachment; filename="{filename_base}.xlsx"'
            return resp

        return JsonResponse({"error": "Formato no soportado"}, status=400)

    except ExportTimeout as e:
        return JsonResponse({"error": str(e)}, status=504)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
