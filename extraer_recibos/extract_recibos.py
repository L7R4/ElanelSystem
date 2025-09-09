import re
import sys
import argparse
from pathlib import Path
from PyPDF2 import PdfReader
import pandas as pd
from openpyxl import load_workbook

def clean_amount(text: str) -> str:
    if text is None:
        return ""
    return re.sub(r'[^0-9]', '', text)

def extract_page_fields(text: str):
    norm = re.sub(r"[ \t]+", " ", text)
    m_role = re.search(r"\b(Vendedor|Supervisor)\s+([A-ZÁÉÍÓÚÜÑa-záéíóúüñ\'\.\- ]+)", norm)
    role = m_role.group(1) if m_role else ""
    name = m_role.group(2).strip() if m_role else ""
    if name:
        name = re.split(r"\s+Concepto\b", name)[0].strip()

    m_total = re.search(r"TOTAL\s+COMISIONADO\s*\$?\s*([0-9\.\s]+)", norm, re.IGNORECASE)
    total_raw = m_total.group(1).strip() if m_total else ""
    total_clean = clean_amount(total_raw)

    finiquito = ""
    if re.search(r"\bFiniquito\s+Total\b", norm, re.IGNORECASE):
        finiquito = "Total"
    elif re.search(r"\bFiniquito\s+Parcial\b", norm, re.IGNORECASE):
        finiquito = "Parcial"

    return {
        "Página": None,  # se completa luego
        "Nombre": name,
        "Rol": role,
        "Total Comisionado": total_clean,
        "Finiquito": finiquito,
    }

def auto_adjust_excel(path: Path):
    """Ajusta el ancho de las columnas al contenido."""
    wb = load_workbook(path)
    ws = wb.active
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        ws.column_dimensions[col_letter].width = max_length + 2
    wb.save(path)

def main():
    parser = argparse.ArgumentParser(description="Extraer datos de recibos PDF a Excel (.xlsx)")
    parser.add_argument("pdf_path", help="Ruta al archivo PDF de recibos.")
    parser.add_argument("--dedupe", action="store_true", help="Deduplicar por (Nombre, Rol).")
    args = parser.parse_args()

    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"ERROR: No se encontró el archivo: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    reader = PdfReader(str(pdf_path))
    rows = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        fields = extract_page_fields(text)
        fields["Página"] = i
        rows.append(fields)

    if args.dedupe:
        seen = set()
        deduped = []
        for r in rows:
            key = (r.get("Nombre",""), r.get("Rol",""))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(r)
        rows = deduped

    # DataFrame con columnas en español
    df = pd.DataFrame(rows, columns=["Página","Nombre","Rol","Total Comisionado","Finiquito"])

    # Nombre de salida igual al PDF pero con .xlsx
    out_path = pdf_path.with_suffix(".xlsx")
    df.to_excel(out_path, index=False)

    # Ajustar columnas automáticamente
    auto_adjust_excel(out_path)

    print(f"✅ Se extrajeron {len(rows)} filas a {out_path}")

if __name__ == '__main__':
    main()
