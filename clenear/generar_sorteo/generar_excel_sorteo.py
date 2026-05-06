import pandas as pd
import os
import re

def normalize_sheet_name(name):
    # Remove leading/trailing spaces and make uppercase
    return name.strip().upper()

def main():
    folder = r"c:\Users\Administrador\Documents\ElanelSystem\sorteo"
    output_file = r"c:\Users\Administrador\Documents\ElanelSystem\pagos_sorteo_abril_2026.xlsx"
    
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
            
            for col in df.columns:
                col_up = col.upper()
                if 'NOMBRE Y APELL' in col_up or 'APELLIDO Y NOMBRE' in col_up:
                    nombre_col = col
                if 'FECHA DE PAGO' in col_up:
                    fecha_col = col
                    
            if not nombre_col or not fecha_col:
                print(f"Falta columna de Nombre o Fecha en {file}.")
                continue
                
            # Filter valid dates (coerce errors to NaT)
            # Remove anything not looking like a date, e.g. "PENDIENTE", " "
            df['Fecha Parseada'] = pd.to_datetime(df[fecha_col], errors='coerce', dayfirst=True)
            
            # Extract date range exactly from 2026-04-01 to 2026-04-10
            start_date = pd.to_datetime('2026-04-01')
            end_date = pd.to_datetime('2026-04-10')
            
            mask = (df['Fecha Parseada'] >= start_date) & (df['Fecha Parseada'] <= end_date)
            df_filtered = df[mask].copy()
            
            if df_filtered.empty:
                print(f"No hay pagos entre el 01/04/2026 y 10/04/2026 en {file}.")
                continue
                
            # Select required columns
            result_df = df_filtered[[nombre_col, fecha_col]].copy()
            
            # Extract branch name from file
            # E.g. "AGENCIA CHACO - ELANEL SRL..." -> "CHACO"
            # Attempt to split by "-"
            branch_name = file.split('-')[0].strip()
            # Clean up known prefixes like "AGENCIA"
            branch_name = branch_name.replace('AGENCIA', '').strip()
            # If the name is too long, crop to 31 chars
            # But branch names should be short
            if len(branch_name) > 31:
                branch_name = branch_name[:31]
                
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
