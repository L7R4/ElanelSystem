"""Busca nros de orden sin clientes en condiciones de adjudicar (todos deudores),
o con como mucho 1 cliente al día. Lee los Excel de Desktop/SISTEMAS.
Guarda un pickle con los contratos para poder re-analizar con distintos umbrales."""
import os, re, sys, pickle
import datetime as dt
import pandas as pd

FOLDER = r"C:\Users\Administrador\Desktop\SISTEMAS"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contratos_octubre_2026.pkl")

def clean_col_name(col):
    return str(col).strip().upper().replace(' ', '_').replace('-', '_').replace('.', '_')

def find_header(xl, sheet, keys):
    tmp = xl.parse(sheet, nrows=20, header=None)
    for idx, row in tmp.iterrows():
        s = " ".join(str(x).upper() for x in row.values if pd.notna(x))
        if any(k in s for k in keys):
            return idx
    return None

def load_contracts():
    now_dt = dt.datetime.now()
    contracts = []
    files = [f for f in os.listdir(FOLDER) if f.endswith(('.xls', '.xlsx', '.xlsm')) and not f.startswith('~')]
    for file in files:
        path = os.path.join(FOLDER, file)
        branch = file.split('.')[0].strip().upper()
        if '-' in file:
            branch = file.split('-')[0].strip().replace('AGENCIA', '').strip().upper()
        if 'POSADAS' in branch:
            branch = 'POSADAS VIEJO' if 'VIEJO' in file.upper() else 'POSADAS NVO'
        print(f"Leyendo {file}...", flush=True)
        xl = pd.ExcelFile(path)
        res_sheet = next((s for s in xl.sheet_names if s.strip().upper() in ["RESUMEN", "RESÚMEN"]), None)
        est_sheet = next((s for s in xl.sheet_names if s.strip().upper() in ["ESTADO", "ESTADOS"]), None)
        if not res_sheet or not est_sheet:
            print(f"  Falta RESUMEN/ESTADOS: {xl.sheet_names}"); continue
        rh = find_header(xl, res_sheet, ['ID VENTA', 'FECHA INCRIPCION', 'NRO DE ORDEN', 'CONTRATO'])
        eh = find_header(xl, est_sheet, ['CUOTAS', 'FECHA-VENC', 'IMPORTE CUOTAS'])
        if rh is None or eh is None:
            print("  Sin encabezado"); continue
        df_res = xl.parse(res_sheet, header=rh); df_res.columns = [clean_col_name(c) for c in df_res.columns]
        df_est = xl.parse(est_sheet, header=eh); df_est.columns = [clean_col_name(c) for c in df_est.columns]

        r_id = next((c for c in df_res.columns if 'ID_VENTA' in c or 'IDVENTA' in c), None)
        r_ord = next((c for c in df_res.columns if 'NRO_DE_ORDEN' in c or 'NRO_ORDEN' in c or 'NROORDEN' in c or 'ORDEN' in c), None)
        r_nom = next((c for c in df_res.columns if 'NOMBRE' in c or 'APELL' in c), None)
        r_dni = next((c for c in df_res.columns if 'DNI' in c), None)
        r_est = next((c for c in df_res.columns if 'ESTADO' in c), None)
        e_id = next((c for c in df_est.columns if 'ID_VENTA' in c or 'IDVENTA' in c), None)
        e_cuo = next((c for c in df_est.columns if 'CUOTA' in c), None)
        # Columna de estado POR CUOTA: la que más valores PAGADO/PENDIENTE/VENCIDO tenga
        # (en Chaco se llama 'BAJA'; 'Estado Plan' NO es el estado de la cuota).
        def score(c):
            v = df_est[c].astype(str).str.strip().str.upper()
            return v.isin(['PAGADO', 'PENDIENTE', 'VENCIDO', 'ATRASADO']).sum()
        e_est = max(df_est.columns, key=score)
        if score(e_est) == 0:
            e_est = None
        e_pago = next((c for c in df_est.columns if 'FECHA' in c and 'PAGO' in c), None)
        print(f"  estado cuota: {e_est} | fecha pago: {e_pago}")
        e_venc = next((c for c in df_est.columns if 'FECHA_VENC' in c or 'VENC' in c), None)
        if not all([r_id, r_ord, e_id, e_cuo, e_est]):
            print(f"  Columnas faltantes. RES={list(df_res.columns)} EST={list(df_est.columns)}"); continue

        df_res[r_id] = pd.to_numeric(df_res[r_id], errors='coerce'); df_res = df_res.dropna(subset=[r_id])
        df_est[e_id] = pd.to_numeric(df_est[e_id], errors='coerce'); df_est = df_est.dropna(subset=[e_id])

        sales_cuotas = {}
        for _, row in df_est.iterrows():
            due = pd.to_datetime(str(row[e_venc]).strip(), errors='coerce', dayfirst=True) if e_venc and pd.notna(row[e_venc]) else pd.NaT
            status = str(row[e_est]).strip().title()
            # Si tiene fecha de pago cargada, la cuota está paga aunque el estado no lo diga
            if e_pago and pd.notna(pd.to_datetime(row[e_pago], errors='coerce', dayfirst=True)):
                status = 'Pagado'
            sales_cuotas.setdefault(int(row[e_id]), []).append(
                {'cuota': str(row[e_cuo]).strip(), 'status': status, 'due_date': due})

        for sale_id, group in df_res.groupby(r_id):
            sale_id = int(sale_id)
            estados = group[r_est].dropna().astype(str).str.upper().str.strip().tolist() if r_est else []
            baja = any(s in ['BAJA', 'RECUPERO BAJA', 'RECUPERO_BAJA'] for s in estados)
            cuotas = sales_cuotas.get(sale_id, [])
            cd = {c['cuota']: c for c in cuotas}
            atr = 0
            for c in cuotas:
                st, due = c['status'], c['due_date']
                venc = False
                if st in ['Vencido', 'Atrasado']:
                    venc = True
                elif st != 'Pagado' and pd.notna(due) and due < now_dt:
                    if c['cuota'] in ['Cuota 0', 'Cuota 1']:
                        num = int(re.search(r'\d+', c['cuota']).group())
                        post = any(o['status'] == 'Pagado' and re.search(r'\d+', n) and int(re.search(r'\d+', n).group()) > num
                                   for n, o in cd.items())
                        venc = not post
                    else:
                        venc = True
                if venc:
                    atr += 1
            pagadas = sum(1 for c in cuotas if c['status'] == 'Pagado')
            for _, row in group.iterrows():
                try:
                    nro = int(float(row[r_ord]))
                except Exception:
                    continue
                dni = row[r_dni] if r_dni and pd.notna(row[r_dni]) else 'N/A'
                try: dni = str(int(float(dni)))
                except Exception: dni = str(dni).strip()
                contracts.append({'id_venta': sale_id, 'nro_orden': nro,
                    'nombre': str(row[r_nom]).strip() if r_nom and pd.notna(row[r_nom]) else 'N/A',
                    'dni': dni, 'sucursal': branch, 'baja': baja, 'sin_cuotas': not cuotas,
                    'cuotas_total': len(cuotas), 'pagadas': pagadas, 'atrasadas': atr})
    return contracts

if __name__ == '__main__':
    if os.path.exists(CACHE) and '--reload' not in sys.argv:
        contracts = pickle.load(open(CACHE, 'rb'))
    else:
        contracts = load_contracts()
        pickle.dump(contracts, open(CACHE, 'wb'))
    print(f"Contratos: {len(contracts)}")
