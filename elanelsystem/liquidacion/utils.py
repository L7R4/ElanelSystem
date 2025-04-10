from datetime import timedelta
from elanelsystem.utils import parse_fecha
from sales.models import Ventas,MovimientoExterno
from .models import *
from sales.utils import searchSucursalFromStrings, obtener_ultima_campania
from django.db.models import Q

def liquidaciones_countFaltas(colaborador):
    data = colaborador.faltas_tardanzas
    tardanzas = sum(1 for elemento in data if elemento["tipoEvento"] == "Tardanza")

    # Cada 3 tardanzas se cuenta 1 falta mas
    faltas = sum(1 for elemento in data if elemento["tipoEvento"] == "Falta") + int(tardanzas/3)
    return faltas

def liquidaciones_countTardanzas(colaborador):
    data = colaborador.faltas_tardanzas
    tardanzas = sum(1 for elemento in data if elemento["tipoEvento"] == "Tardanza")
    return tardanzas

#region Funciones enfocadas a los vendedores
def calcular_cantidad_ventasPropias(usuario,campania,agencia):
    """
    Retorna la cantidad de ventas (según chances) propias de un usuario
    en una campaña y agencia dadas.
    """
    ventas_query = Ventas.objects.filter(
        vendedor=usuario,
        campania=campania,
        agencia=agencia,
        adjudicado__status=False,
        deBaja__status=False
    )

    ventas_auditadas = [
        v for v in ventas_query
        if v.auditoria and len(v.auditoria) > 0 and v.auditoria[-1].get("grade") is True
    ]
    return sum(len(v.cantidadContratos) for v in ventas_auditadas)

def calcular_productividad_ventasPropias(usuario,campania,agencia):

    """
    Retorna la 'productividad' total de las ventas propias (sum of total_a_pagar).
    """
    ventas_query = Ventas.objects.filter(
        vendedor=usuario,
        campania=campania,
        agencia=agencia,
        adjudicado__status=False,
        deBaja__status=False
    )

    ventas_auditadas = [
        v for v in ventas_query
        if v.auditoria and len(v.auditoria) > 0 and v.auditoria[-1].get("grade") is True
    ]

    # Sumar los importes de los productos asociados a cada venta
    return sum(venta.importe for venta in ventas_auditadas)

# def get_detalle_comision_x_cantidad_ventasPropias(usuario,campania,agencia):
#     detalleDict = {"planes":{}}
#     comisionTotal = 0
#     ventas_qs_2 = Ventas.objects.filter(
#                 vendedor=usuario,
#                 campania=campania,
#                 agencia=agencia,
#                 adjudicado__status=False,
#                 deBaja__status=False
#             )
#     ventas_auditadas2 = [
#             v for v in ventas_qs_2
#             if v.auditoria and len(v.auditoria) > 0 and v.auditoria[-1].get("grade") is True
#     ]

#     cantVentas2 = sum(len(v.cantidadContratos) for v in ventas_auditadas2)
#     comisionSubTotal = 0
#     bandas=[]
#     for venta in ventas_auditadas2:
#         if(venta.nro_cuotas in [24,30] and venta.producto.tipo_de_producto="Moto"):
#             bandas = [
#                 (0, 9, 0.0240),
#                 (9, 20, 0.0250),
#                 (20, 30, 0.0260),
#                 (30, float("inf"), 0.0270),
#             ]
#         elif(venta.nro_cuotas in [24,30] and (venta.producto.tipo_de_producto="Prestamo" or venta.producto.tipo_de_producto="Combo")):
#             bandas = [
#                 (0, 9, 0.0270),
#                 (9, 20, 0.0280),
#                 (20, 30, 0.0290),
#                 (30, float("inf"), 0.0310),
#             ]
#         elif(venta.nro_cuotas in [30,48] and venta.producto.tipo_de_producto="Moto"):
#             bandas = [
#                 (0, 9, 0.0135),
#                 (9, 20, 0.0140),
#                 (20, 30, 0.0145),
#                 (30, float("inf"), 0.0155),
#             ]

#         coeficienteSelected = 0
#         for low, high, coef in bandas:
#             if low <= cantVentas2 < high:
#                 coeficienteSelected = coef
#                 break

#         comisionSubTotal += venta.importe * coeficienteSelected
       
#         # Se arma la sub-seccion
#         detalleDict["planes"][typePlan] = {
#             "cantidad_ventas": cantVentas,
#             "comision": comision,
#             "ventas": [{
#                 "pk": v.pk,
#                 "importe": v.importe,
#                 "nro_cuotas": v.nro_cuotas,
#                 "producto": v.producto.nombre,
#                 "fecha": v.fecha,
#                 "cantidadContratos": v.cantidadContratos,
#                 "nro_operacion": v.nro_operacion,
#                 "nro_cliente": v.nro_cliente.nro_cliente,
#                 "nombre_cliente": v.nro_cliente.nombre
#             } for v in ventas_auditadas]
#         }

#         comisionTotal += comision 

#     detalleDict["comision"] = comisionTotal
#     return detalleDict

def get_detalle_comision_x_cantidad_ventasPropias(usuario, campania, agencia):
    """
    - Recorre todas las ventas (auditadas) de un usuario en cierta campaña y agencia.
    - Para cada venta, determina el plan (com_24_30_motos, com_24_30_prestamo_combo, com_30_48_motos) 
      según cuotas y tipo_de_producto.
    - Usa la cantidad total de ventas (cantVentas2) para seleccionar el coeficiente en la banda.
    - Retorna un dict con la misma estructura que tu código original: 
        {
          "planes": {
            "com_24_30_motos": {
                "cantidad_ventas": X,
                "comision": Y,
                "ventas": [ ... ]
            },
            "com_24_30_prestamo_combo": { ... },
            "com_30_48_motos": { ... }
          },
          "comision": TOTAL_DE_COMISION
        }
    """

    detalleDict = {"planes": {}}
    # Inicializamos las "buckets" para cada categoría posible:
    detalleDict["planes"]["com_24_30_motos"] = {
        "cantidad_ventas": 0,
        "comision": 0.0,
        "ventas": []
    }
    detalleDict["planes"]["com_24_30_prestamo_combo"] = {
        "cantidad_ventas": 0,
        "comision": 0.0,
        "ventas": []
    }
    detalleDict["planes"]["com_30_48_motos"] = {
        "cantidad_ventas": 0,
        "comision": 0.0,
        "ventas": []
    }

    # Consulta de todas las ventas no adjudicadas / no dadas de baja
    ventas_qs_2 = Ventas.objects.filter(
        vendedor=usuario,
        campania=campania,
        agencia=agencia,
        adjudicado__status=False,
        deBaja__status=False
    )

    # Filtramos sólo las que pasen la auditoría con grade=True
    ventas_auditadas2 = [
        v for v in ventas_qs_2
        if v.auditoria and len(v.auditoria) > 0 and v.auditoria[-1].get("grade") is True
    ]

    # Cantidad total de ventas (sumando los contratos) para calcular la banda
    cantVentas2 = sum(len(v.cantidadContratos) for v in ventas_auditadas2)

    # Recorremos cada venta y decidimos qué bandas usar
    for venta in ventas_auditadas2:
        # Determinamos a qué 'typePlan' pertenece
        if (venta.nro_cuotas in [24, 30] and venta.producto.tipo_de_producto == "Moto"):
            typePlan = "com_24_30_motos"
            bandas = [
                (0, 9, 0.0240),
                (9, 20, 0.0250),
                (20, 30, 0.0260),
                (30, float("inf"), 0.0270),
            ]
        elif (venta.nro_cuotas in [24, 30] and 
             (venta.producto.tipo_de_producto == "Prestamo" or venta.producto.tipo_de_producto == "Combo")):
            typePlan = "com_24_30_prestamo_combo"
            bandas = [
                (0, 9, 0.0270),
                (9, 20, 0.0280),
                (20, 30, 0.0290),
                (30, float("inf"), 0.0310),
            ]
        elif (venta.nro_cuotas in [48, 60]):
            # Ojo: aquí asumes un plan "30 a 48" para motos. 
            # Si querías [48,60], ajústalo a tu necesidad:
            typePlan = "com_30_48_motos"
            bandas = [
                (0, 9, 0.0135),
                (9, 20, 0.0140),
                (20, 30, 0.0145),
                (30, float("inf"), 0.0155),
            ]
        else:
            # Si no coincide con ninguno, puedes saltarlo o crear otra categoría
            # Por ahora saltamos:
            continue

        # Elegimos el coeficiente con base en cantVentas2 (ventas totales de este usuario)
        coeficienteSelected = 0
        for (low, high, coef) in bandas:
            if low <= cantVentas2 < high:
                coeficienteSelected = coef
                break

        # Calculamos la comisión de esta venta
        comision_venta = venta.importe * coeficienteSelected

        # Agregamos la venta al array de "ventas" del bucket correspondiente
        detalleDict["planes"][typePlan]["ventas"].append({
            "pk": venta.pk,
            "importe": venta.importe,
            "nro_cuotas": venta.nro_cuotas,
            "producto": venta.producto.nombre,
            "fecha": venta.fecha,
            "cantidadContratos": venta.cantidadContratos,
            "nro_operacion": venta.nro_operacion,
            "nro_cliente": venta.nro_cliente.nro_cliente,
            "nombre_cliente": venta.nro_cliente.nombre
        })

        # Sumamos comision y también incrementamos su "cantidad_ventas"
        detalleDict["planes"][typePlan]["comision"] += comision_venta
        detalleDict["planes"][typePlan]["cantidad_ventas"] += len(venta.cantidadContratos)

    # Al terminar de procesar todas las ventas, sumamos la comision total
    comisionTotal = 0.0
    for keyPlan in detalleDict["planes"]:
        comisionTotal += detalleDict["planes"][keyPlan]["comision"]

    detalleDict["comision"] = comisionTotal
    return detalleDict


def get_premio_x_productividad_ventasPropias(usuario,campania,agencia):
    """
    Devuelve un premio fijo según la productividad (sum(venta.importe)).
    """

    ventas_qs = Ventas.objects.filter(
        vendedor=usuario,
        campania=campania,
        agencia=agencia,
        adjudicado__status=False,
        deBaja__status=False
    )
    ventas_auditadas = [
        v for v in ventas_qs
        if v.auditoria and len(v.auditoria) > 0 and v.auditoria[-1].get("grade") is True
    ]
    productividad = sum(v.importe for v in ventas_auditadas)

    # Bandas fijas
    bandas = [
        (0, 6000000, 0),
        (6000000, 8000000, 10000),
        (8000000, 10000000, 15000),
        (10000000, float("inf"), 20000),
    ]
    premio = 0
    for low, high, dinero in bandas:
        if low <= productividad < high:
            premio = dinero
            break

    return premio


def get_detalle_cuotas1(usuario, campania, agencia):
    """
    Retorna las cuotas 1 que se pagaron dentro de 15 días de alta,
    y la comision que se le da: 10% de la cuota comercial (es decir, de la 2 para adelante)
    """
    from elanelsystem.utils import parse_fecha

    ventas_qs = Ventas.objects.filter(
        vendedor=usuario,
        # campania=campania,
        agencia=agencia,
        adjudicado__status=False,
        deBaja__status=False
    )
    ventas_auditadas = [
        v for v in ventas_qs
        if v.auditoria and len(v.auditoria) > 0 and v.auditoria[-1].get("grade") is True
    ]
    cuotas1Adelantadas = []
    total_comision_x_cuota1 = 0
    cant_cuotas_1 = 0
    print(f"\n\n VENTAS AUDITAS\n\n{ventas_auditadas}")
    for venta in ventas_auditadas:
        # Chequear si la cuota 1 está pagada
        if venta.cuotas[1]["status"] == "Pagado" and venta.cuotas[1]["pagos"][0]["campaniaPago"]==campania:
            fechaPagoC1 = parse_fecha(venta.cuotas[1]["pagos"][0]["fecha"])
            fechaAltaVenta = parse_fecha(venta.fecha)
            dias_dif = (fechaPagoC1 - fechaAltaVenta).days
            if dias_dif <= 15:
                cuotas1Adelantadas.append(venta.cuotas[1])
                # sumamos 10% de la cuota 2
                cant_cuotas_1 += len(venta.cantidadContratos)
                total_comision_x_cuota1 += venta.cuotas[2]["total"] * 0.10

    return {
        "comision_total": total_comision_x_cuota1,
        "detalle": cuotas1Adelantadas,
        "cantidadCuotas1": cant_cuotas_1
    }

#endregion


#region Funciones enfocadas a los  supervisores   
def calcular_ventas_supervisor(usuario, campania, agencia):
    """
    Retorna la cantidad de ventas totales (según chances) 
    de un supervisor (todas las ventas donde sea supervisor).
    """
    ventas_qs = Ventas.objects.filter(
        supervisor=usuario,
        campania=campania,
        agencia=agencia,
        adjudicado__status=False,
        deBaja__status=False
    )
    ventas_auditadas = [
        v for v in ventas_qs
        if v.auditoria and len(v.auditoria) > 0 and v.auditoria[-1].get("grade") is True
    ]
    return sum(len(v.cantidadContratos) for v in ventas_auditadas)


def calcular_productividad_supervisor(usuario, campania, agencia):
    """
    Retorna la productividad total de un supervisor 
    (sum of total_a_pagar de las ventas bajo su supervisión).
    """
    ventas_qs = Ventas.objects.filter(
        supervisor=usuario,
        campania=campania,
        agencia=agencia,
        adjudicado__status=False,
        deBaja__status=False
    )
    ventas_filtradas = [
        v for v in ventas_qs
        if v.auditoria and len(v.auditoria) > 0 and v.auditoria[-1].get("grade") is True
    ]
    return sum(v.importe for v in ventas_filtradas)


def get_premio_x_productividad_supervisor(usuario, campania, agencia):
    total_prod = calcular_productividad_supervisor(usuario, campania, agencia)
    premio = 0
    bandas = [
        (0, 16000000, 0),
        (16000000, 18000000, 0.00020),
        (18000000, 22000000, 0.00030),
        (22000000, 26000000, 0.00050),
        (26000000, 30000000, 0.00075),
        (30000000, float("inf"), 0.001),
    ]
    for low, high, coef in bandas:
        if low <= total_prod < high:
            premio = total_prod * coef
            break
    return premio


def get_premio_x_cantidad_ventas_equipo(usuario, campania, agencia):
    asegurado = Asegurado.objects.get(dirigido="Supervisor")
    dineroAsegurado = asegurado.dinero
    cantidad_ventas_x_equipo = calcular_ventas_supervisor(usuario,campania,agencia)
    
    # Si la suma de ventas del equipo supera 80, se le suma el asegurado como premio
    if cantidad_ventas_x_equipo > 80:
        return dineroAsegurado
    return 0


def get_comision_x_cantidad_ventas_equipo(usuario, campania, agencia):
    """
    Retorna la comision total del supervisor segun la cantidad de ventas (bandas).
    """
    ventas_qs = Ventas.objects.filter(
        supervisor=usuario,
        campania=campania,
        agencia=agencia,
        adjudicado__status=False,
        deBaja__status=False
    )
    ventas_auditadas = [
        v for v in ventas_qs
        if v.auditoria and len(v.auditoria) > 0 and v.auditoria[-1].get("grade") is True
    ]
    cantVentas =  sum(len(v.cantidadContratos) for v in ventas_auditadas)

    bandas = [
        (0, 30, 0),
        (30, 40, 0.0027),
        (40, 50, 0.0029),
        (50, 60, 0.0031),
        (60, 70, 0.0033),
        (70, 80, 0.0035),
        (80, 90, 0.0037),
        (90, float("inf"), 0.0039),
    ]

    coef = 0
    for low, high, c in bandas:
        if low <= cantVentas < high:
            coef = c
            break

    total = 0

    for venta in ventas_auditadas:
        total += venta.importe * coef

    return total


def detalle_de_equipo_x_supervisor(usuario, campania, agencia):
    """
    Retorna una lista con [ {nombre, cantidad_ventas, productividad}, ... ]
    de todos los vendedores supervisados.
    """
    ventas_qs = Ventas.objects.filter(
        supervisor=usuario,
        campania=campania,
        agencia=agencia,
        adjudicado__status=False,
        deBaja__status=False
    )
    ventas_auditadas = [
        v for v in ventas_qs
        if v.auditoria and len(v.auditoria) > 0 and v.auditoria[-1].get("grade") is True
    ]
    detalle_vendedores = []
    for v in ventas_auditadas:
        vend = v.vendedor
        item = {
            "nombre": vend.nombre,
            "cantidad_ventas": calcular_cantidad_ventasPropias(vend, campania, agencia),
            "productividad": calcular_productividad_ventasPropias(vend, campania, agencia)
        }
        detalle_vendedores.append(item)

    return detalle_vendedores
#endregion


#region Funciones enfocadas a los gerentes de sucursal

def get_detalle_cuotas_x(campania, agencia, porcetage_x_cuota=0):
    """
    Retorna un dict con la comision generada por las cuotas 0,1,2,3,4.
    """
    cuotasDict = {"porcetage_x_cuota": porcetage_x_cuota, "detalleCuota": {}}
    porcetage_x_cuota = 0.08
    cantidadTotalCuotas = 0
    dineroTotalCuotas = 0
    comisionTotalCuotas = 0

    ventas_qs = Ventas.objects.filter(
        agencia=agencia,
        campania=campania,
        adjudicado__status=False,
        deBaja__status=False
    )
    ventas_auditadas = [
        v for v in ventas_qs
        if v.auditoria and len(v.auditoria) > 0 and v.auditoria[-1].get("grade") is True
    ]

    # Otras cuotas => 1,2,3,4
    cuotasToFilter = ['1','2','3','4']
    for number in cuotasToFilter:
        cnt = 0
        dineroTotalX = 0
        for vent in ventas_auditadas:
            if vent.cuotas[int(number)]["status"] == "Pagado":
                cnt += len(vent.cantidadContratos)
                dineroTotalX += vent.cuotas[int(number)]["total"]

        comisionX = dineroTotalX * porcetage_x_cuota
        cantidadTotalCuotas += cnt
        dineroTotalCuotas += dineroTotalX
        comisionTotalCuotas += comisionX

        cuotasDict["detalleCuota"][f"cuotas{number}"] = {
            "cantidad": cnt,
            "dinero_x_cuota": dineroTotalX,
            "comision": comisionX
        }

    cuotasDict["cantidad_total_cuotas"] = cantidadTotalCuotas
    cuotasDict["dinero_total_cuotas"] = dineroTotalCuotas
    cuotasDict["comision_total_cuotas"] = comisionTotalCuotas
    return cuotasDict


def get_detalle_cuotas_0(campania, agencia):
    """
    Retorna un dict con la comision generada por las cuotas 0.
    """

    ventas_qs = Ventas.objects.filter(
        agencia=agencia,
        campania=campania,
        adjudicado__status=False,
        deBaja__status=False
    )
    ventas_auditadas = [
        v for v in ventas_qs
        if v.auditoria and len(v.auditoria) > 0 and v.auditoria[-1].get("grade") is True
    ]

    ventas_segun_chances = sum(len(v.cantidadContratos) for v in ventas_auditadas)
    cantidad_cuotas_0 = ventas_segun_chances

    dinero_recadudado_cuotas_0 = 0
    for vent in ventas_auditadas:
        if vent.cuotas[0]["status"] == "Pagado":
            dinero_recadudado_cuotas_0 += vent.cuotas[0]["total"]

    return {
        "cantidad_cuotas_0": cantidad_cuotas_0,
        "dinero_recadudado_cuotas_0": dinero_recadudado_cuotas_0
    }


def get_premio_x_cantidad_ventas_sucursal(campania, agencia,objetivo_gerente=0):
    
    objetivo_gerente = 200
    cantidad_cuotas_0 = get_detalle_cuotas_0(campania, agencia)["cantidad_cuotas_0"]

    return 1000 * cantidad_cuotas_0 if cantidad_cuotas_0 >= objetivo_gerente else 0

#endregion


#region Funciones para obtener y calcular el asegurado de los usuarios

def get_asegurado(usuario):
    dineroAsegurado = 0

    rango = usuario.rango.lower()
    if rango == "vendedor":
        asegurado = Asegurado.objects.get(dirigido="Vendedor")
        dineroAsegurado = asegurado.dinero
        return calcular_asegurado_segun_dias_trabajados(dineroAsegurado, usuario)

    elif rango == "supervisor":
        asegurado = Asegurado.objects.get(dirigido="Supervisor")
        dineroAsegurado = asegurado.dinero
        return calcular_asegurado_segun_dias_trabajados(dineroAsegurado, usuario)

    elif rango == "gerente de sucursal":
        asegurado = Asegurado.objects.get(dirigido="Gerente de sucursal")
        return asegurado.dinero

    else:
        raise ValueError("Error al obtener el asegurado: rango de usuario no reconocido.")



def calcular_asegurado_segun_dias_trabajados(dinero, usuario):
    """
    Calcula cuánto asegurado le corresponde a un colaborador según sus días trabajados.
    Si trabajó 26 días o más (sin contar domingos), cobra el asegurado completo.
    Si trabajó menos, cobra proporcional.
    """
    # Parseamos fecha_ingreso si viene como string
    fecha_ingreso = usuario.fec_ingreso
    if isinstance(fecha_ingreso, str):
        fecha_ingreso = datetime.strptime(fecha_ingreso, "%d/%m/%Y")

    fecha_egreso = ""

    print(f"FEcha de egreso: \n{fecha_egreso}")
    if fecha_egreso != "":
        fecha_egreso = datetime.strptime(fecha_egreso, "%d/%m/%Y")
    else:
        fecha_egreso = datetime.now()

    print(f"[DEBUG] Fechas parsed: ingreso={fecha_ingreso}, egreso={fecha_egreso}")

    dias_trabajados = (fecha_egreso - fecha_ingreso).days + 1  # +1 para incluir el día de ingreso

    print(f"[DEBUG] {usuario.nombre} trabajó {dias_trabajados} días hábiles entre {fecha_ingreso.date()} y {fecha_egreso.date()}")

    if dias_trabajados >= 30:
        return dinero
    else:
        proporcional = (dinero / 30) * dias_trabajados
        return int(proporcional)
#endregion


#region Funciones enfocadas en los descuentos

def get_ausencias_tardanzas(usuario, campania):
    """
    Retorna un dict con 'total_descuentos' y un detalle de cuántas faltas/tardanzas
    están registradas para cierto usuario en una campaña dada.
    """

    if not usuario.faltas_tardanzas:
        return {
            "total_descuentos": 0,
            "detalle": {
                "faltas": {"cantidad": 0, "dinero": 0,"detalle":{}},
                "tardanzas": {"cantidad": 0, "dinero": 0,"detalle":{}}
            }
        }

    data_campania = [item for item in usuario.faltas_tardanzas if item["campania"] == campania]
    faltas = [x for x in data_campania if x["tipoEvento"].lower() == "falta"]
    tardanzas = [x for x in data_campania if x["tipoEvento"].lower() == "tardanza"]

    objMonto = MontoTardanzaAusencia.objects.first()
    montoPorFalta = objMonto.monto_ausencia
    montoPorTardanza = objMonto.monto_tardanza

    total_desc = (len(tardanzas) * montoPorTardanza) + (len(faltas) * montoPorFalta)

    return {
        "total_descuentos": int(total_desc),
        "detalle": {
            "faltas": {
                "cantidad": len(faltas),
                "dinero": int(montoPorFalta * len(faltas)),
                "detalle": faltas
            },
            "tardanzas": {
                "cantidad": len(tardanzas),
                "dinero": int(montoPorTardanza * len(tardanzas)),
                "detalle": tardanzas
            }
        }
    }


#endregion


def detalle_liquidado_ventasPropias(usuario, campania, agencia):
    print(f"""\n\n
    ==================================================================
        DETALLE  DE VENTAS PROPIAS
    ==================================================================
    """)

    print(f"\n[DEBUG] detalle_liquidado_ventasPropias | Inicio. usuario={usuario}, campania={campania}, agencia={agencia}")

    cantidad_ventas = calcular_cantidad_ventasPropias(usuario, campania, agencia)
    productividad_x_ventas_propias = calcular_productividad_ventasPropias(usuario, campania, agencia)

    dict_comision_cant_ventas = get_detalle_comision_x_cantidad_ventasPropias(usuario, campania, agencia)
    comision_x_cantidad_ventas_propias = dict_comision_cant_ventas["comision"]
    detalle_ventas_propias = dict_comision_cant_ventas["planes"]

    dict_cuotas1 = get_detalle_cuotas1(usuario, campania, agencia)
    comision_x_cuotas1 = dict_cuotas1["comision_total"]
    cantidad_cuotas1 = dict_cuotas1["cantidadCuotas1"]
    detalle_cuotas1 = dict_cuotas1["detalle"]

    subtotal = comision_x_cantidad_ventas_propias + comision_x_cuotas1

    print("\n[DEBUG] detalle_liquidado_ventasPropias | Datos intermedios:")
    print(f"\n   - cantidad_ventas={cantidad_ventas}")
    print(f"\n   - productividad_x_ventas_propias={productividad_x_ventas_propias}")
    print(f"\n   - comision_x_cantidad_ventas_propias={comision_x_cantidad_ventas_propias}")
    print(f"\n   - comision_x_cuotas1={comision_x_cuotas1}")
    print(f"\n   - subtotal={subtotal}")

    resultado = {
        "comision_subtotal": subtotal,
        "detalle": {
            "cantidadVentas": cantidad_ventas,
            "productividadXVentasPropias": productividad_x_ventas_propias,
            "comisionXCantidadVentasPropias": comision_x_cantidad_ventas_propias,
            "detalleVentasPropias": detalle_ventas_propias,
            "comisionXCuotas1": comision_x_cuotas1,
            "cantidadCuotas1": cantidad_cuotas1,
            "detalleCuotas1": detalle_cuotas1
        }
    }

    print("[DEBUG] detalle_liquidado_ventasPropias | Resultado final:", resultado)
    return resultado


def detalle_descuestos(usuario, campania, agencia):
    print(f"""\n\n
    ==================================================================
        DETALLE  DE DESCUENTOS
    ==================================================================
    """)
    print(f"\n[DEBUG] detalle_descuestos | Inicio. usuario={usuario}, campania={campania}, agencia={agencia}")

    total_descuentos = 0
    aus_tard_dict = get_ausencias_tardanzas(usuario, campania)
    descuento_x_tardanzas_faltas = aus_tard_dict["total_descuentos"]
    detalle_descuento_x_tardanzas_faltas = aus_tard_dict["detalle"]

    total_descuentos += descuento_x_tardanzas_faltas

    print("\n[DEBUG] detalle_descuestos | Datos intermedios:")
    print(f"\n   - descuento_x_tardanzas_faltas={descuento_x_tardanzas_faltas}")
    print(f"\n  - total_descuentos={total_descuentos}")

    resultado = {
        "total_descuentos": total_descuentos,
        "detalle": {
            "tardanzas_faltas": detalle_descuento_x_tardanzas_faltas
        }
    }

    print("[DEBUG] detalle_descuestos | Resultado final:", resultado)
    return resultado


def detalle_premios_x_objetivo(usuario, campania, agencia, objetivo_gerente=0):
    print(f"""\n\n
    ==================================================================
        DETALLE  DE PREMIOS X OBJETIVO
    ==================================================================
    """)
    print(f"\n [DEBUG] detalle_premios_x_objetivo | Inicio. usuario={usuario}, campania={campania}, agencia={agencia}, objetivo_gerente={objetivo_gerente}")

    premio_subtotal = 0
    detalle = {}

    premio_x_productividad_ventas_propias = get_premio_x_productividad_ventasPropias(usuario, campania, agencia)

    print("\n [DEBUG] detalle_premios_x_objetivo | Premio productividad ventas propias =", premio_x_productividad_ventas_propias)

    # Según el rango, calculamos otros premios
    rango_lower = str(usuario.rango).lower()

    if rango_lower == "supervisor":
        premio_x_cantidad_ventas_equipo = get_premio_x_cantidad_ventas_equipo(usuario, campania, agencia)
        premio_x_productividad_ventas_equipo = get_premio_x_productividad_supervisor(usuario, campania, agencia)

        detalle = {
            "premio_x_cantidad_ventas_equipo": premio_x_cantidad_ventas_equipo,
            "premio_x_productividad_ventas_equipo": premio_x_productividad_ventas_equipo
        }

        premio_subtotal += (premio_x_cantidad_ventas_equipo + premio_x_productividad_ventas_equipo)
        print("\n [DEBUG] detalle_premios_x_objetivo | Supervisor => premios eq:", detalle)

    elif rango_lower == "gerente de sucursal":
        premio_x_cantidad_ventas_agencia = get_premio_x_cantidad_ventas_sucursal(campania, agencia, objetivo_gerente)
        detalle = {
            "premio_x_cantidad_ventas_agencia": premio_x_cantidad_ventas_agencia,
        }
        premio_subtotal += premio_x_cantidad_ventas_agencia
        print("\n [DEBUG] detalle_premios_x_objetivo | Gerente => premio agencia:", premio_x_cantidad_ventas_agencia)

    premio_subtotal += premio_x_productividad_ventas_propias
    detalle["premio_x_productividad_ventas_propias"] = premio_x_productividad_ventas_propias
    resultado = {
        "total_premios": premio_subtotal,
        "detalle": detalle
    }

    print("\n [DEBUG] detalle_premios_x_objetivo | Resultado final:", resultado)
    return resultado


def detalle_liquidado_x_rol(usuario, campania, agencia, porcentage_x_cuota_gerente=0):
    print(f"""\n\n
    ==================================================================
        DETALLE DE LIQUIDADO X ROL
    ==================================================================
    """)
    print(f"\n [DEBUG] detalle_liquidado_x_rol | Inicio. usuario={usuario}, campania={campania}, agencia={agencia}, porcentage_x_cuota_gerente={porcentage_x_cuota_gerente}")

    rango_lower = str(usuario.rango).lower()

    if rango_lower == "supervisor":
        cantidad_ventas_x_equipo = calcular_ventas_supervisor(usuario, campania, agencia)
        productividad_x_equipo = calcular_productividad_supervisor(usuario, campania, agencia)

        comision_x_cantidad_ventas_equipo = get_comision_x_cantidad_ventas_equipo(usuario, campania, agencia)
        detalle_ventas_equipo = detalle_de_equipo_x_supervisor(usuario, campania, agencia)

        print("\n [DEBUG] detalle_liquidado_x_rol | Supervisor => Ventas equipo:", cantidad_ventas_x_equipo)
        print("\n [DEBUG] detalle_liquidado_x_rol | Supervisor => Prod equipo:", productividad_x_equipo)
        print("\n [DEBUG] detalle_liquidado_x_rol | Supervisor => Comision eq:", comision_x_cantidad_ventas_equipo)

        resultado = {
            "comision_subtotal": comision_x_cantidad_ventas_equipo,
            "detalle": {
                "cantidadVentasXEquipo": cantidad_ventas_x_equipo,
                "productividadXVentasEquipo": productividad_x_equipo,
                "detalleVentasXEquipo": detalle_ventas_equipo
            }
        }
        print("\n [DEBUG] detalle_liquidado_x_rol | Resultado final Supervisor:", resultado)
        return resultado

    elif rango_lower == "gerente de sucursal":
        dict_cuotas_0 = get_detalle_cuotas_0(campania, agencia)
        dict_cuotas_x = get_detalle_cuotas_x(campania, agencia, porcentage_x_cuota_gerente)

        cantidad_total_de_cuotas_0 = dict_cuotas_0["cantidad_cuotas_0"]
        dinero_total_recaudado_cuotas_0 = dict_cuotas_0["dinero_recadudado_cuotas_0"]

        cantidad_total_de_cuotas_x = dict_cuotas_x["cantidad_total_cuotas"]
        dinero_total_recaudado_cuotas = dict_cuotas_x["dinero_total_cuotas"]
        comision_x_cuotas = dict_cuotas_x["comision_total_cuotas"]
        detalle_x_cuotas = dict_cuotas_x["detalleCuota"]

        print("\n [DEBUG] detalle_liquidado_x_rol | Gerente => Cuotas0:", dict_cuotas_0)
        print("\n [DEBUG] detalle_liquidado_x_rol | Gerente => CuotasX:", dict_cuotas_x)

        resultado = {
            "comision_subtotal": comision_x_cuotas,
            "detalle": {
                "cantidad_cuotas_0": cantidad_total_de_cuotas_0,
                "dinero_recaudado_cuotas_0": dinero_total_recaudado_cuotas_0,
                "cantidad_cuotas_1_4": cantidad_total_de_cuotas_x,
                "dinero_recaudado_cuotas": dinero_total_recaudado_cuotas,
                "detalle_x_cuotas": detalle_x_cuotas,
            }
        }
        print("\n [DEBUG] detalle_liquidado_x_rol | Resultado final Gerente:", resultado)
        return resultado

    else:
        # Caso por defecto: no supervisor ni gerente
        print("\n [DEBUG] detalle_liquidado_x_rol | Colaborador sin rol supervisor/gerente => comision 0")
        resultado = {
            "comision_subtotal": 0,
            "detalle": {}
        }
        return resultado


def get_comision_total(usuario, campania, agencia, ajustes_usuario=None):
    """
    Calcula toda la lógica de comisiones (ventas, descuentos, premios, rol, etc.)
    y además integra los ajustes manuales:
      - Ajustes positivos --> Se suman en premios (otros_premios)
      - Ajustes negativos --> Se suman en descuentos (otros_descuentos)
      - Si la comisión neta es menor que el asegurado, la persona cobra el asegurado,
        pero la comisión_bruta queda en 0 (para reflejar que el asegurado "reemplaza" a la comisión).
    """

    print(f"""\n\n
    ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
        DETALLE DE GENERAL {usuario.nombre} {campania} {agencia.pseudonimo}
    ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    """)
    print(f"[DEBUG]\n 1) AJUSTES = {ajustes_usuario}\n")

    if ajustes_usuario is None:
        ajustes_usuario = []
    print(f"[DEBUG]\n 2) AJUSTES = {ajustes_usuario}\n")
    # 1) Sección ventasPropias
    ventas_propias_dict = detalle_liquidado_ventasPropias(usuario, campania, agencia)
    comision_ventas_propias = ventas_propias_dict["comision_subtotal"]

    # 2) Sección descuentos
    descuentos_dict = detalle_descuestos(usuario, campania, agencia)
    total_desc = descuentos_dict["total_descuentos"]

    # 3) Sección premios por objetivo
    premios_dict = detalle_premios_x_objetivo(usuario, campania, agencia)
    total_premios = premios_dict["total_premios"]
    # 4) Sección rol
    rol_dict = detalle_liquidado_x_rol(usuario, campania, agencia)
    asegurado = 0
    comision_rol = 0
    premios_segun_rol = 0

    # Cálculo de 'comision_general' según el rol
    if (usuario.rango.lower() == "supervisor"):
        try:
            asegurado = get_asegurado(usuario)
            # comision_rol = max(rol_dict["comision_subtotal"], asegurado)  # EJEMPLO anterior
            # Pero ahora haremos la lógica final al final de la función, para no duplicar
            comision_rol = rol_dict["comision_subtotal"]
            premios_segun_rol += premios_dict["detalle"]["premio_x_productividad_ventas_equipo"] + premios_dict["detalle"]["premio_x_cantidad_ventas_equipo"]
        except ValueError as e:
            print(e)
        # Suma las ventas propias
        # comision_general = comision_rol + comision_ventas_propias

    elif usuario.rango.lower() == "vendedor":
        asegurado = get_asegurado(usuario)
        # Lo mismo: guardamos la comision_rol = ventas_propias
        comision_rol = comision_ventas_propias
        premios_segun_rol += premios_dict["detalle"]["premio_x_productividad_ventas_propias"]

        # comision_general = comision_rol
    elif (usuario.rango.lower() == "gerente de sucursal"):
        pass
    else:
        pass

    # 5) Comision base (antes de ajustes)
    comision_bruta = 0
    comision_bruta_segun_rol = comision_rol + premios_segun_rol
    if comision_bruta_segun_rol < asegurado:
        comision_bruta += asegurado - comision_bruta_segun_rol
        asegurado = asegurado - comision_bruta_segun_rol # Asegurado se reduce a lo que falta para llegar al asegurado

    else:
        asegurado = 0 # Si la comision es mayor que el asegurado, se queda con la comision
        comision_bruta += comision_bruta_segun_rol

    if (usuario.rango.lower() != "vendedor"):
        comision_bruta += comision_ventas_propias # Si no es vendedor, sumamos la comision de ventas propias
        comision_bruta += premios_dict["detalle"]["premio_x_productividad_ventas_propias"]

    # 6) Integrar los ajustes manuales
    ajustes_positivos = sum(a["dinero"] for a in ajustes_usuario if a["ajuste_tipo"] == "positivo")
    ajustes_negativos = sum(a["dinero"] for a in ajustes_usuario if a["ajuste_tipo"] == "negativo")
    print("[DEBUG]\n ??? Ajustes NEGATIVOS:", ajustes_negativos)
    print("[DEBUG]\n ??? Ajustes POSITIVOS:", ajustes_positivos)

    # Sumar a premios
    otros_premios = ajustes_positivos
    # Sumar a descuentos
    total_desc += ajustes_negativos

    # 7) Recalcular bruta y neta incluyendo ajustes
    comision_bruta += otros_premios
    comision_neta = comision_bruta - total_desc

    # Armamos el dict final
    resultado_final = {
        "comision_total": int(comision_neta),    # lo que efectivamente va a cobrar
        "comision_bruta": int(comision_bruta),   # la bruta real si superaba o 0 si no alcanzó el asegurado
        "asegurado": int(asegurado),
        "detalle": {
            "ventasPropias": ventas_propias_dict,
            "descuentos": descuentos_dict,
            "premios": premios_dict,
            "rol": rol_dict,
            # Aquí podemos exponer también en qué parte se metieron los ajustes:
            "ajustes": {
                "ajustes_positivos": ajustes_positivos,
                "ajustes_negativos": ajustes_negativos
            }
        },
        # Si quieres dejar una traza adicional:
        "descuentoTotal": int(total_desc),
        "premiosTotal": int(total_premios),
    }

    return resultado_final

