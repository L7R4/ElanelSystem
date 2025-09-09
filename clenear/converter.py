#!/usr/bin/env python3
"""
xlsm_to_csv.py

Uso:
    python xlsm_to_csv.py  ruta/al/archivo.xlsm   --out ./carpeta_salida
"""

import argparse
import os
import sys
import warnings

import pandas as pd
from openpyxl.utils.exceptions import InvalidFileException

# ————————————————————————————————————————————————————————————————
SHEETS_TO_EXPORT = {"RESUMEN", "ESTADOS", "CLIENTES"}      # puedes cambiarlo aquí
# ————————————————————————————————————————————————————————————————

def export_sheets(xlsm_path: str, out_dir: str) -> None:
    """Convierte las hojas definidas en SHEETS_TO_EXPORT a CSV."""
    # Silenciar avisos de Data Validation de openpyxl
    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

    try:
        xl = pd.ExcelFile(xlsm_path, engine="openpyxl")
    except (FileNotFoundError, InvalidFileException) as exc:
        sys.exit(f"❌  No pude abrir el archivo: {exc}")

    # Normalizar nombres a mayúsculas para comparación
    available = {s.upper(): s for s in xl.sheet_names}

    for target in SHEETS_TO_EXPORT:
        if target.upper() not in available:
            print(f"⚠️  La hoja «{target}» no existe en el libro, se omite.")
            continue

        df = xl.parse(available[target.upper()], dtype=str)  # leer como texto para no perder formatos
        # Construir nombre de salida: <nombre_libro>_<hoja>.csv
        book_name = os.path.splitext(os.path.basename(xlsm_path))[0]
        csv_name = f"{book_name}_{target}.csv"
        csv_path = os.path.join(out_dir, csv_name)
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"✅  Hoja «{target}» exportada a → {csv_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convierte hojas específicas de un XLSM a archivos CSV."
    )
    parser.add_argument("xlsm", help="Ruta al archivo .xlsm de origen")
    parser.add_argument(
        "--out",
        "-o",
        default=".",
        help="Directorio de salida (por defecto, la carpeta actual)",
    )
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    export_sheets(args.xlsm, args.out)
