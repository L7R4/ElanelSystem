import pandas as pd
import os
import re
import sys

def normalize_sheet_name(name):
    # Remove leading/trailing spaces and make uppercase
    return name.strip().upper()

def main():
    folder = r"C:\Users\Administrador\Desktop\SISTEMAS"
    output_file = r"c:\Users\Administrador\Documents\ElanelSystem\pagos_sorteo_septiembre_2026.xlsx"

    if len(sys.argv) > 1:
        # User provided file names as arguments
        files = sys.argv[1:]
    else:
        # Process all files in folder
        files = [f for f in os.listdir(folder) if f.endswith(('.xls', '.xlsx', '.xlsm')) and not f.startswith('~')]

    all_branches_data = {}

    for file in files:
        path = os.path.join(folder, file)
        try:
            xl = pd.ExcelFile(path)
        except Exception as e:
            print(f"Error al abrir {file}: {e}")
            continue

        sheet_names = xl.sheet_names
        target_sheet = None
        for sheet in sheet_names:
            norm_name = normalize_sheet_name(sheet)
            # Match ESTADO or ESTADOS
            if norm_name == "ESTADO" or norm_name == "ESTADOS":
                target_sheet = sheet
                break

        if not target_sheet:
            print(f"No se encontró hoja de ESTADO/ESTADOS en {file}")
            continue

        print(f"Procesando {file} (hoja: '{target_sheet}')...")
        try:
            df_temp = xl.parse(target_sheet, nrows=20, header=None)
            header_row_idx = None
            for idx, row in df_temp.iterrows():
                row_str = " ".join([str(x).upper() for x in row.values if pd.notna(x)])
                if 'NOMBRE Y APELL' in row_str or 'NOMBRE Y APELLIDO' in row_str or 'FECHA DE PAGO' in row_str:
                    header_row_idx = idx
                    break

            if header_row_idx is None:
                print(f"No se encontraron los encabezados esperados en {file}.")
                continue

            # Now read with the correct header
            df = xl.parse(target_sheet, header=header_row_idx)

            # Clean column names
            df.columns = [str(col).strip() for col in df.columns]

            # Find required columns
            nombre_col = None
            fecha_col = None
            dni_col = None

            for col in df.columns:
                col_up = str(col).upper().strip()
                if 'NOMBRE Y APELL' in col_up or 'APELLIDO Y NOMBRE' in col_up:
                    nombre_col = col
                if 'FECHA DE PAGO' in col_up or 'FECHA PAGO' in col_up:
                    fecha_col = col
                if 'DNI' in col_up:
                    dni_col = col

            # Robust fallback for fecha_col
            if not fecha_col and len(df.columns) > 7:
                col_5 = str(df.columns[5]).upper()
                col_6 = str(df.columns[6]).upper()
                if 'VENC' in col_5 and ('IMPORTE' in col_6 or 'CUOTA' in col_6):
                    fecha_col = df.columns[7]
                    print(f"  -> Usando columna fallback en índice 7 para fecha de pago: '{fecha_col}'")

            if not nombre_col or fecha_col is None:
                print(f"Falta columna de Nombre o Fecha en {file}.")
                continue

            # Filter valid dates (coerce errors to NaT)
            df['Fecha Parseada'] = pd.to_datetime(df[fecha_col], errors='coerce', dayfirst=True)

            # Extract date range exactly from 2026-09-01 to 2026-09-10
            start_date = pd.to_datetime('2026-09-01')
            end_date = pd.to_datetime('2026-09-10')

            mask = (df['Fecha Parseada'] >= start_date) & (df['Fecha Parseada'] <= end_date)
            df_filtered = df[mask].copy()

            if df_filtered.empty:
                print(f"No hay pagos entre el 01/09/2026 y 10/09/2026 en {file}.")
                continue

            # Extract branch name from file
            branch_name = file.split('.')[0].strip().upper()
            if '-' in file:
                branch_name = file.split('-')[0].strip()
                branch_name = branch_name.replace('AGENCIA', '').strip().upper()
            if len(branch_name) > 31:
                branch_name = branch_name[:31]

            # Select required columns
            cols_to_select = [nombre_col, fecha_col]
            if dni_col:
                cols_to_select.append(dni_col)

            result_df = df_filtered[cols_to_select].copy()
            # Nombres uniformes (en Posadas Viejo la columna de fecha no tiene título)
            result_df.columns = ['Nombre y Apellido', 'Fecha de Pago'] + (['DNI'] if dni_col else [])
            result_df['Fecha de Pago'] = df_filtered['Fecha Parseada'].dt.date
            result_df['Sucursal'] = branch_name
            result_df['Archivo Origen'] = file

            if branch_name in all_branches_data:
                all_branches_data[branch_name] = pd.concat(
                    [all_branches_data[branch_name], result_df], ignore_index=True
                )
            else:
                all_branches_data[branch_name] = result_df
            print(f"  -> Encontrados {len(result_df)} registros en {branch_name}")

        except Exception as e:
            print(f"Error procesando los datos de {file}: {e}")
            continue

    if all_branches_data:
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                for branch, b_df in all_branches_data.items():
                    b_df.to_excel(writer, sheet_name=branch, index=False)
            print(f"\n¡Éxito! Archivo guardado en: {output_file}")
        except Exception as e:
            print(f"Error al guardar el archivo de Excel: {e}")
    else:
        print("\nNo se encontraron registros para la fecha solicitada en ningún archivo.")

if __name__ == '__main__':
    main()
