import pickle, collections, sys
contracts = pickle.load(open('contratos_octubre_2026.pkl', 'rb'))
# Bajas no pueden adjudicar -> no cuentan. Ventas sin cuotas en ESTADOS se tratan como "al día" (riesgo).
activos = [c for c in contracts if not c['baja']]
por_orden = collections.defaultdict(list)
for c in activos:
    por_orden[c['nro_orden']].append(c)

def analizar(umbral_desc, es_deudor, max_al_dia):
    res = []
    for nro, cs in por_orden.items():
        al_dia = [c for c in cs if not es_deudor(c)]
        if len(al_dia) <= max_al_dia:
            res.append((nro, cs, al_dia))
    res.sort(key=lambda x: (len(x[2]), -len(x[1]), x[0]))
    print(f"\n=== {umbral_desc} | max clientes al día: {max_al_dia} -> {len(res)} números ===")
    for nro, cs, al_dia in res[:40]:
        print(f"Nro {nro}: {len(cs)} contratos activos, {len(al_dia)} en condiciones")
        for c in cs:
            flag = 'PUEDE GANAR' if c in al_dia else 'deudor'
            print(f"   [{flag}] {c['sucursal']} | {c['nombre']} | DNI {c['dni']} | venta {c['id_venta']} | atrasadas {c['atrasadas']} | pagadas {c['pagadas']}/{c['cuotas_total']}")
    return res

print("Total contratos:", len(contracts), "activos:", len(activos), "nros de orden:", len(por_orden))
r = analizar(">2 cuotas adeudadas", lambda c: c['atrasadas'] > 2, 0)
if not r:
    r = analizar(">2 cuotas adeudadas", lambda c: c['atrasadas'] > 2, 1)
if not r or '--todo' in sys.argv:
    analizar(">=2 cuotas adeudadas", lambda c: c['atrasadas'] >= 2, 0)
    analizar(">=2 cuotas adeudadas", lambda c: c['atrasadas'] >= 2, 1)
