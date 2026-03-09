#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
excel_clean_per_file.py

- Recorre carpetas que empiezan con "a_"
- Dentro busca archivos Excel que empiezan con "sistema_" y terminan en .xls/.xlsx/.xlsm
- Extrae SOLO: ESTADO (o ESTADOS), RESUMEN, CLIENTES
- Por cada archivo "sistema_*" genera un ÚNICO Excel limpio con 3 hojas
  y lo guarda en la misma carpeta como:
    clean_<nombre_archivo>_<YYYY-MM-DD_HH-MM-SS>.xlsx

Uso (scan automático):
  python excel_clean_per_file.py --root .

Uso (un archivo puntual):
  python excel_clean_per_file.py ./a_posadas/sistema_algo.xlsm
"""

import argparse
import os
import re
import sys
import tempfile
import warnings
from datetime import datetime
from pathlib import Path

import pandas as pd
"""
Uso (scan automático):
  python excel_clean_per_file.py --root .

Uso (un archivo puntual):
  python excel_clean_per_file.py ./a_resistencia/sistema_resistencia.xlsm
"""


# Siempre generar estas 3 hojas (en este orden)
OUTPUT_SHEETS = ("ESTADO", "RESUMEN", "CLIENTES")

# Variantes aceptadas en el Excel fuente (ESTADOS -> ESTADO)
INPUT_SHEET_VARIANTS = {
    "ESTADO": ("ESTADO", "ESTADOS"),
    "RESUMEN": ("RESUMEN",),
    "CLIENTES": ("CLIENTES","CLIENTE"),
}


def scan_inputs(root: Path) -> list[Path]:
    """Busca carpetas a_* y dentro archivos sistema_*.xls/xlsx/xlsm (recursivo)."""
    inputs: list[Path] = []

    for d in sorted(root.iterdir()):
        if not (d.is_dir() and d.name.lower().startswith("a_")):
            continue

        for p in d.rglob("*"):
            if not p.is_file():
                continue
            low = p.name.lower()
            if low.startswith("sistema_") and low.endswith((".xlsx", ".xlsm", ".xls")):
                inputs.append(p)

    # dedupe
    uniq = []
    seen = set()
    for p in inputs:
        rp = str(p.resolve())
        if rp not in seen:
            seen.add(rp)
            uniq.append(p)

    return uniq


def _convert_xls_to_xlsx_if_possible(xls_path: Path) -> Path | None:
    """
    Convierte .xls -> .xlsx SOLO si estás en Windows con Excel instalado (COM) + pywin32.
    Si no se puede, devuelve None y se omite el archivo.
    """
    if os.name != "nt":
        return None

    try:
        import win32com.client  # pip install pywin32
    except Exception:
        return None

    tmp_dir = Path(tempfile.mkdtemp(prefix="xls_to_xlsx_"))
    out_xlsx = tmp_dir / (xls_path.stem + ".xlsx")

    excel = None
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        wb = excel.Workbooks.Open(str(xls_path))
        # 51 = xlOpenXMLWorkbook (.xlsx)
        wb.SaveAs(str(out_xlsx), FileFormat=51)
        wb.Close(False)
        return out_xlsx
    except Exception:
        return None
    finally:
        try:
            if excel is not None:
                excel.Quit()
        except Exception:
            pass


def _get_real_sheet_name(xl: pd.ExcelFile, variants: tuple[str, ...]) -> str | None:
    """Devuelve el nombre real de la hoja en el archivo (case-insensitive) según variantes."""
    available = {s.upper(): s for s in xl.sheet_names}
    for v in variants:
        if v.upper() in available:
            return available[v.upper()]
    return None


def _read_sheet_as_df(excel_path: Path, sheet_name: str) -> pd.DataFrame:
    """Lee hoja como texto y normaliza NaN a vacío."""
    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

    df = pd.read_excel(
        excel_path,
        sheet_name=sheet_name,
        dtype=str,
        engine="openpyxl",
        engine_kwargs={"data_only": True},  # intenta traer valores calculados
    )

    return df.fillna("")


def process_one_file(src: Path) -> Path | None:
    """
    Procesa 1 archivo sistema_* y genera clean_...xlsx en la misma carpeta.
    Devuelve la ruta de salida o None si se omitió.
    """
    src_to_read = src

    # Manejo .xls (opcional)
    if src.suffix.lower() == ".xls":
        converted = _convert_xls_to_xlsx_if_possible(src)
        if converted is None:
            print(f"⚠️  Omitido .xls (no pude convertir): {src}")
            return None
        src_to_read = converted

    try:
        xl = pd.ExcelFile(src_to_read, engine="openpyxl")
    except Exception as e:
        print(f"❌  No pude abrir {src}: {e}")
        return None

    # Nombre salida: clean_<archivo>_<fechahora>.xlsx (misma carpeta)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_path = src.parent / f"clean_{src.stem}_{timestamp}.xlsx"

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for out_sheet in OUTPUT_SHEETS:
            real_name = _get_real_sheet_name(xl, INPUT_SHEET_VARIANTS[out_sheet])

            if real_name is None:
                # Igual creamos la hoja vacía para que el output tenga SIEMPRE 3 hojas
                print(f"⚠️  {src.name}: no existe hoja {INPUT_SHEET_VARIANTS[out_sheet]} -> creo '{out_sheet}' vacía.")
                df = pd.DataFrame()
            else:
                try:
                    df = _read_sheet_as_df(src_to_read, real_name)
                except Exception as e:
                    print(f"❌  {src.name}: error leyendo '{real_name}': {e} -> creo '{out_sheet}' vacía.")
                    df = pd.DataFrame()

            df.to_excel(writer, sheet_name=out_sheet, index=False)

    print(f"✅  Generado: {out_path}")
    return out_path


def main():
    parser = argparse.ArgumentParser(
        description="Genera por cada sistema_* un Excel limpio (3 hojas) en la misma carpeta."
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Ruta a un archivo Excel. Si no se pasa, hace scan de carpetas a_* desde --root.",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Directorio raíz para buscar carpetas a_* (por defecto: .)",
    )
    args = parser.parse_args()

    if args.input:
        src = Path(args.input)
        if not src.exists():
            sys.exit(f"❌  No existe: {src}")
        process_one_file(src)
        return

    root = Path(args.root)
    files = scan_inputs(root)
    if not files:
        sys.exit("⚠️  No encontré archivos sistema_*.xls/xlsx/xlsm dentro de carpetas a_*.")

    print(f"🔎 Encontré {len(files)} archivo(s). Procesando...\n")
    for f in files:
        process_one_file(f)


if __name__ == "__main__":
    main()
