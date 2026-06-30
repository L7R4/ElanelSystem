import os
import re
import datetime as dt
import pandas as pd

def clean_col_name(col):
    return str(col).strip().upper().replace(' ', '_').replace('-', '_').replace('.', '_')

def main():
    folder = r"C:\Users\Administrador\Desktop\liquidaciones\liquidaciones\SISTEMAS"
    files = [f for f in os.listdir(folder) if f.endswith(('.xls', '.xlsx', '.xlsm')) and not f.startswith('~')]
    
    now_dt = dt.datetime.now()
    all_eligible = []
    order_counts = {}
    
    print(f"Analyzing {len(files)} branch files...")
    
    for file in files:
        path = os.path.join(folder, file)
        # Determine branch name
        branch_name = file.split('.')[0].strip().upper()
        if '-' in file:
            branch_name = file.split('-')[0].strip()
            branch_name = branch_name.replace('AGENCIA', '').strip().upper()
        if len(branch_name) > 31:
            branch_name = branch_name[:31]
            
        try:
            xl = pd.ExcelFile(path)
        except Exception as e:
            print(f"Error opening {file}: {e}")
            continue
            
        # Find sheet names
        res_sheet = next((s for s in xl.sheet_names if s.upper() in ["RESUMEN", "RESÚMEN"]), None)
        est_sheet = next((s for s in xl.sheet_names if s.upper() in ["ESTADO", "ESTADOS"]), None)
        
        if not res_sheet or not est_sheet:
            print(f"Missing RESUMEN or ESTADOS in {file}")
            continue
            
        # 1. Parse RESUMEN to find header and data
        df_res_temp = xl.parse(res_sheet, nrows=20, header=None)
        res_header_idx = None
        for idx, row in df_res_temp.iterrows():
            row_str = " ".join([str(x).upper() for x in row.values if pd.notna(x)])
            if 'ID VENTA' in row_str or 'FECHA INCRIPCION' in row_str or 'NRO DE ORDEN' in row_str or 'CONTRATO' in row_str:
                res_header_idx = idx
                break
                
        if res_header_idx is None:
            print(f"Could not find header in RESUMEN for {file}")
            continue
            
        df_res = xl.parse(res_sheet, header=res_header_idx)
        df_res.columns = [clean_col_name(c) for c in df_res.columns]
        
        # 2. Parse ESTADOS to find header and data
        df_est_temp = xl.parse(est_sheet, nrows=20, header=None)
        est_header_idx = None
        for idx, row in df_est_temp.iterrows():
            row_str = " ".join([str(x).upper() for x in row.values if pd.notna(x)])
            if 'CUOTAS' in row_str or 'FECHA-VENC' in row_str or 'IMPORTE CUOTAS' in row_str:
                est_header_idx = idx
                break
                
        if est_header_idx is None:
            print(f"Could not find header in ESTADOS for {file}")
            continue
            
        df_est = xl.parse(est_sheet, header=est_header_idx)
        df_est.columns = [clean_col_name(c) for c in df_est.columns]
        
        # Check necessary columns
        res_id_col = next((c for c in df_res.columns if 'ID_VENTA' in c or 'IDVENTA' in c), None)
        res_orden_col = next((c for c in df_res.columns if 'NRO_DE_ORDEN' in c or 'NRO_ORDEN' in c or 'NROORDEN' in c or 'ORDEN' in c), None)
        res_nombre_col = next((c for c in df_res.columns if 'NOMBRE' in c or 'APELL' in c), None)
        res_dni_col = next((c for c in df_res.columns if 'DNI' in c), None)
        res_estado_col = next((c for c in df_res.columns if 'ESTADO' in c), None)
        
        est_id_col = next((c for c in df_est.columns if 'ID_VENTA' in c or 'IDVENTA' in c), None)
        est_cuota_col = next((c for c in df_est.columns if 'CUOTA' in c), None)
        est_estado_col = next((c for c in df_est.columns if 'ESTADO' in c), None)
        est_venc_col = next((c for c in df_est.columns if 'FECHA_VENC' in c or 'VENC' in c), None)
        
        if not res_id_col or not res_orden_col or not est_id_col or not est_cuota_col or not est_estado_col:
            print(f"Missing required columns in {file}")
            print(f"  RESUMEN columns: {list(df_res.columns)}")
            print(f"  ESTADOS columns: {list(df_est.columns)}")
            continue
            
        # Clean data types
        df_res[res_id_col] = pd.to_numeric(df_res[res_id_col], errors='coerce')
        df_res = df_res.dropna(subset=[res_id_col])
        df_res[res_id_col] = df_res[res_id_col].astype(int)
        
        df_est[est_id_col] = pd.to_numeric(df_est[est_id_col], errors='coerce')
        df_est = df_est.dropna(subset=[est_id_col])
        df_est[est_id_col] = df_est[est_id_col].astype(int)
        
        # Build map of sale ID to cuotas
        sales_cuotas = {}
        for idx, row in df_est.iterrows():
            sale_id = int(row[est_id_col])
            cuota_name = str(row[est_cuota_col]).strip()
            state = str(row[est_estado_col]).strip().title()
            due_str = str(row[est_venc_col]).strip() if est_venc_col and pd.notna(row[est_venc_col]) else ''
            
            due_date = pd.to_datetime(due_str, errors='coerce', dayfirst=True)
            
            cuota_dict = {
                'cuota': cuota_name,
                'status': state,
                'due_date': due_date
            }
            sales_cuotas.setdefault(sale_id, []).append(cuota_dict)
            
        # Analyze each sale in RESUMEN
        # A sale can have multiple rows (multiple contracts/chances)
        grouped = df_res.groupby(res_id_col)
        
        for sale_id, group in grouped:
            # Check if Baja
            is_baja_res = False
            if res_estado_col:
                res_states = group[res_estado_col].dropna().astype(str).str.upper().str.strip().values
                if any(s in ['BAJA', 'RECUPERO BAJA', 'RECUPERO_BAJA'] for s in res_states):
                    is_baja_res = True
                    
            if is_baja_res:
                continue
                
            cuotas = sales_cuotas.get(int(sale_id), [])
            if not cuotas:
                continue
                
            # Descartar planes ya finalizados (donde no queden cuotas normales pendientes de pago)
            tiene_cuotas_pendientes = any(
                c['status'] != 'Pagado'
                for c in cuotas
                if c['cuota'] not in ['Cuota 0', 'Cuota 1']
            )
            if not tiene_cuotas_pendientes:
                continue
                
            # Verificar si la venta está al día
            al_dia = True
            cuotas_dict = {c['cuota']: c for c in cuotas}
            
            for c in cuotas:
                status = c['status']
                
                if status == 'Vencido' or status == 'Atrasado':
                    al_dia = False
                    break
                    
                if status == 'Pagado':
                    continue
                    
                due_date = c['due_date']
                if pd.isna(due_date):
                    continue
                    
                if due_date < now_dt:
                    cuota_name = c['cuota']
                    if cuota_name in ['Cuota 0', 'Cuota 1']:
                        try:
                            num = int(re.search(r'\d+', cuota_name).group())
                        except:
                            num = -1
                            
                        has_posterior_pagada = False
                        for name, cu_obj in cuotas_dict.items():
                            try:
                                cu_num = int(re.search(r'\d+', name).group())
                                if cu_num > num and cu_obj['status'] == 'Pagado':
                                    has_posterior_pagada = True
                                    break
                            except:
                                continue
                                
                        if has_posterior_pagada:
                            continue
                            
                    al_dia = False
                    break
                    
            # Check if suspended rule (3 or more vencidos)
            # Actually, in Excel, if a cuota is overdue it might already be marked Vencido or Atrasado.
            # Let's count how many cuotas are overdue.
            cont_atrasados = 0
            for c in cuotas:
                status = c['status']
                due_date = c['due_date']
                is_venc = False
                if status in ['Vencido', 'Atrasado']:
                    is_venc = True
                elif status != 'Pagado' and pd.notna(due_date) and due_date < now_dt:
                    cuota_name = c['cuota']
                    if cuota_name in ['Cuota 0', 'Cuota 1']:
                        try:
                            num = int(re.search(r'\d+', cuota_name).group())
                        except:
                            num = -1
                        has_posterior_pagada = False
                        for name, cu_obj in cuotas_dict.items():
                            try:
                                cu_num = int(re.search(r'\d+', name).group())
                                if cu_num > num and cu_obj['status'] == 'Pagado':
                                    has_posterior_pagada = True
                                    break
                            except:
                                continue
                        if not has_posterior_pagada:
                            is_venc = True
                    else:
                        is_venc = True
                if is_venc:
                    cont_atrasados += 1
                    
            if cont_atrasados >= 3:
                al_dia = False
                
            if not al_dia:
                continue
                
            # If eligible, record details of each contract in this sale
            for idx, row in group.iterrows():
                nro_orden = row[res_orden_col]
                nombre = str(row[res_nombre_col]).strip() if res_nombre_col and pd.notna(row[res_nombre_col]) else 'N/A'
                dni = str(row[res_dni_col]).strip() if res_dni_col and pd.notna(row[res_dni_col]) else 'N/A'
                
                try:
                    if isinstance(dni, (int, float)) or (isinstance(dni, str) and dni.strip().replace('.0', '').isdigit()):
                        dni = str(int(float(dni)))
                except:
                    pass
                    
                try:
                    nro_orden_int = int(float(nro_orden))
                    all_eligible.append({
                        'id_venta': int(sale_id),
                        'nro_orden': nro_orden_int,
                        'nombre': nombre,
                        'dni': dni,
                        'sucursal': branch_name
                    })
                    order_counts[nro_orden_int] = order_counts.get(nro_orden_int, 0) + 1
                except:
                    pass
                    
    # Filter by frequency < 3 (1 or 2)
    final_eligible = []
    allowed_numbers = []
    
    for item in all_eligible:
        freq = order_counts[item['nro_orden']]
        if freq < 3:
            final_eligible.append(item)
            if item['nro_orden'] not in allowed_numbers:
                allowed_numbers.append(item['nro_orden'])
                
    allowed_numbers.sort()
    
    print(f"\nFound {len(final_eligible)} eligible contracts corresponding to {len(allowed_numbers)} unique order numbers.")
    print("Allowed order numbers:", allowed_numbers)
    
    # Save results to CSV
    df_out = pd.DataFrame(final_eligible)
    df_out.to_csv("C:/Users/Administrador/Desktop/liquidaciones/liquidaciones/SISTEMAS/clientes_sorteo_sistemas.csv", index=False, encoding='utf-8-sig')
    print("CSV saved to C:/Users/Administrador/Desktop/liquidaciones/liquidaciones/SISTEMAS/clientes_sorteo_sistemas.csv")
    
if __name__ == '__main__':
    main()
