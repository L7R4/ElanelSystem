import pandas as pd

def main():
    df = pd.read_csv('C:/Users/Administrador/Desktop/liquidaciones/liquidaciones/SISTEMAS/clientes_sorteo_sistemas.csv')

    # Group and count by branch
    counts = df.groupby('sucursal').size().reset_index(name='count')
    unique_orders = df.groupby('sucursal')['nro_orden'].nunique().reset_index(name='unique')

    # Sort by name
    df_sorted = df.sort_values(by=['sucursal', 'nombre'])

    md_content = '# Sorteo - Clientes y Órdenes al Día (SISTEMAS)\n\n'
    md_content += 'Reporte de clientes y números de orden que cumplen con las condiciones del sorteo, a partir de las planillas de la carpeta `SISTEMAS`.\n\n'

    md_content += '## Resumen por Sucursal\n\n'
    md_content += '| Sucursal | Total Contratos Habilitados | Números de Orden Habilitados |\n'
    md_content += '| --- | :---: | :---: |\n'
    for idx, row in counts.iterrows():
        branch = row['sucursal']
        unique_cnt = unique_orders[unique_orders['sucursal'] == branch]['unique'].values[0]
        md_content += f'| {branch} | {row["count"]} | {unique_cnt} |\n'
    md_content += f'| **TOTAL** | **{len(df)}** | **{df["nro_orden"].nunique()}** |\n\n'

    md_content += '## Listado de Contratos Habilitados (Total: ' + str(len(df)) + ')\n\n'
    md_content += '| # | Nombre y Apellido | DNI | Número de Orden | Sucursal |\n'
    md_content += '| --- | --- | --- | :---: | --- |\n'

    for idx, row in enumerate(df_sorted.itertuples(), 1):
        md_content += f'| {idx} | {row.nombre} | {row.dni} | {row.nro_orden} | {row.sucursal} |\n'

    with open('C:/Users/Administrador/.gemini/antigravity/brain/2997dc0e-f80a-459f-9c72-7becc00f642a/raffle_sistemas_candidates.md', 'w', encoding='utf-8') as f:
        f.write(md_content)

    print('Markdown generated successfully.')

if __name__ == '__main__':
    main()
