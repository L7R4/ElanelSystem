from datetime import timedelta
from elanelsystem.utils import parse_fecha
from sales.models import Ventas,MovimientoExterno
from .models import *
from sales.utils import searchSucursalFromStrings, obtener_ultima_campania
from django.db.models import Q
import datetime
import calendar
import math

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

import math
import datetime
import calendar

#region Funciones enfocadas a los vendedores

def calcular_cantidad_ventasPropias(usuario, campania, agencia):
    """
    Retorna la cantidad de ventas (según chances) propias de un usuario
    en una campaña y agencia dadas.
    (Esto ya es siempre entero, no hace falta math.ceil)
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
    return sum(len(v.cantidadContratos) for v in ventas_auditadas)  # siempre entero

def calcular_productividad_ventasPropias(usuario, campania, agencia):
    """
    Retorna la 'productividad' total de las ventas propias (sum of venta.importe).
    Aplico math.ceil por si 'importe' fuera flotante.
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

    total = sum(venta.importe for venta in ventas_auditadas)
    return math.ceil(total)  # redondeamos hacia arriba

def get_detalle_comision_x_cantidad_ventasPropias(usuario, campania, agencia):
    """
    Recorre las ventas y determina la comisión. Aplico math.ceil al final.
    """
    detalleDict = {"planes": {}}
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
    detalleDict["planes"]["com_48_60"] = {
        "cantidad_ventas": 0,
        "comision": 0.0,
        "ventas": []
    }

    ventas_qs_2 = Ventas.objects.filter(
        vendedor=usuario,
        campania=campania,
        agencia=agencia,
        adjudicado__status=False,
        deBaja__status=False
    )
    ventas_auditadas2 = [
        v for v in ventas_qs_2
        if v.auditoria and len(v.auditoria) > 0 and v.auditoria[-1].get("grade") is True
    ]

    cantVentas2 = sum(len(v.cantidadContratos) for v in ventas_auditadas2)
    coeficienteSelected = 0
    for venta in ventas_auditadas2:
        if (venta.nro_cuotas in [24, 30] and venta.producto.tipo_de_producto == "Moto"):
            typePlan = "com_24_30_motos"
            bandas = [
                (0, 9, 0.0240),
                (10, 19, 0.0250),
                (20, 29, 0.0260),
                (30, float("inf"), 0.0270),
            ]
        elif (venta.nro_cuotas in [24, 30] and 
             (venta.producto.tipo_de_producto == "Solucion" or venta.producto.tipo_de_producto == "Combo")):
            typePlan = "com_24_30_prestamo_combo"
            bandas = [
                (0, 9, 0.0270),
                (10, 19, 0.0280),
                (20, 29, 0.0290),
                (30, float("inf"), 0.0310),
            ]
        elif (venta.nro_cuotas in [48, 60]):
            typePlan = "com_48_60"
            bandas = [
                (0, 9, 0.0135),
                (10, 19, 0.0140),
                (20, 29, 0.0145),
                (30, float("inf"), 0.0155),
            ]
        else:
            continue

        for (low, high, coef) in bandas:
            if low <= cantVentas2 <= high:
                coeficienteSelected = coef
                break

        comision_venta = venta.importe * coeficienteSelected
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

        detalleDict["planes"][typePlan]["coeficiente_correspondiente"] = coeficienteSelected 
        detalleDict["planes"][typePlan]["comision"] += comision_venta
        detalleDict["planes"][typePlan]["cantidad_ventas"] += len(venta.cantidadContratos)

    comisionTotal = 0.0
    for keyPlan in detalleDict["planes"]:
        # ceil a cada comision de plan
        detalleDict["planes"][keyPlan]["comision"] = math.ceil(detalleDict["planes"][keyPlan]["comision"])
        comisionTotal += detalleDict["planes"][keyPlan]["comision"]

    detalleDict["comision"] = math.ceil(comisionTotal)  # redondeamos total final
    detalleDict["coeficienteSelected"] = coeficienteSelected  # redondeamos total final

    return detalleDict

def get_premio_x_productividad_ventasPropias(usuario, campania, agencia):
    """
    Devuelve un premio fijo según la productividad. 
    Ojo con la lógica: si las bandas devuelven un entero, no hace falta,
    pero si multiplicas, sí. Ejemplo actual no multiplica, 
    excepto en la parte 'bandas' -> no se hace un * coef, sino un valor fijo.
    Aun así, por seguridad uso math.ceil.
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

    return math.ceil(premio)  # Por si acaso (aquí igual es entero)

def get_detalle_cuotas1(usuario, campania, agencia):
    """
    Cuotas 1 pagadas dentro de 15 días -> comision del 10% de la cuota 2.
    Aplico math.ceil a total_comision_x_cuota1.
    """
    from elanelsystem.utils import parse_fecha

    ventas_qs = Ventas.objects.filter(
        vendedor=usuario,
        # campania=campania,  # si deseas filtrar
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
    for venta in ventas_auditadas:
        if venta.cuotas[1]["status"] == "Pagado" and venta.cuotas[1]["pagos"][0]["campaniaPago"] == campania:
            fechaPagoC1 = parse_fecha(venta.cuotas[1]["pagos"][0]["fecha"])
            fechaAltaVenta = parse_fecha(venta.fecha)
            dias_dif = (fechaPagoC1 - fechaAltaVenta).days
            if dias_dif <= 15:
                cuotas1Adelantadas.append(venta.cuotas[1])
                cant_cuotas_1 += len(venta.cantidadContratos)
                total_comision_x_cuota1 += venta.cuotas[2]["total"] * 0.10

    return {
        "comision_total": math.ceil(total_comision_x_cuota1),
        "detalle": cuotas1Adelantadas,
        "cantidadCuotas1": cant_cuotas_1
    }

#endregion

#region Funciones enfocadas a los  supervisores

def calcular_ventas_supervisor(usuario, campania, agencia):
    """
    Cantidad de ventas totales del supervisor. (Siempre entero)
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
    return sum(len(v.cantidadContratos) for v in ventas_auditadas)  # entero

def calcular_productividad_supervisor(usuario, campania, agencia):
    """
    Productividad total (sum of venta.importe). Aplico math.ceil.
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
    total = sum(v.importe for v in ventas_filtradas)
    return math.ceil(total)

def get_premio_x_productividad_supervisor(usuario, campania, agencia):
    """
    Multiplicamos total_prod * coef. => ahí puede salir decimal => math.ceil
    """
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
    return math.ceil(premio)

def get_premio_x_cantidad_ventas_equipo(usuario, campania, agencia):
    """
    Devuelve dineroAsegurado si la suma de ventas > 80, sino 0. 
    No hace falta ceil, pues dineroAsegurado es un entero. 
    Igual, por seguridad, podría hacerse math.ceil.
    """
    asegurado = Asegurado.objects.get(dirigido="Supervisor")
    dineroAsegurado = asegurado.dinero
    cantidad_ventas_x_equipo = calcular_ventas_supervisor(usuario,campania,agencia)
    
    if cantidad_ventas_x_equipo > 80:
        return math.ceil(dineroAsegurado)
    return 0

def get_comision_x_cantidad_ventas_equipo(usuario, campania, agencia):
    """
    total += venta.importe * coef => decimal => uso ceil en el final.
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
    cantVentas = sum(len(v.cantidadContratos) for v in ventas_auditadas)

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

    return math.ceil(total)

def detalle_de_equipo_x_supervisor(usuario, campania, agencia):
    """
    Lista con nombre, cantidad de ventas y productividad.
    Cantidad de ventas = entero; productividad = redondeo arriba.
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
    for venta in ventas_auditadas:
        print(f"ID de Venta: {venta.nro_cliente.nombre}")
        vend = venta.vendedor
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
    Comision de cuotas 1,2,3,4 => math.ceil en comisionTotalCuotas.
    """
    cuotasDict = {"porcetage_x_cuota": porcetage_x_cuota, "detalleCuota": {}}
    porcetage_x_cuota = 0.08
    cantidadTotalCuotas = 0
    dineroTotalCuotas = 0
    comisionTotalCuotas = 0

    ventas_qs = Ventas.objects.filter(
        agencia=agencia,
        adjudicado__status=False,
        deBaja__status=False
    )
    ventas_auditadas = [
        v for v in ventas_qs
        if v.auditoria and len(v.auditoria) > 0 and v.auditoria[-1].get("grade") is True
    ]

    cuotasToFilter = ['1','2','3','4']
    for number in cuotasToFilter:
        cnt = 0
        dineroTotalX = 0
        cuotas_x_list = []
        for vent in ventas_auditadas:
            if vent.cuotas[int(number)]["status"] == "Pagado" and vent.cuotas[int(number)]["pagos"][0]["campaniaPago"] == campania:
                cnt += len(vent.cantidadContratos)
                # if(str(vent.nro_operacion) == "1801"):
                #     print(f"ID de Venta: {vent.nro_cliente.nombre} - Cuota: {number} - Dinero: {vent.cuotas[10]['total']}")
                #     return
                dineroTotalX += vent.cuotas[10]["total"]
                cuotas_x_list.append(vent.cuotas[10]["total"])
        comisionX = dineroTotalX * porcetage_x_cuota
        cantidadTotalCuotas += cnt
        dineroTotalCuotas += dineroTotalX
        comisionTotalCuotas += comisionX

        cuotasDict["detalleCuota"][f"cuotas{number}"] = {
            "cantidad": cnt,
            "dinero_x_cuota": math.ceil(dineroTotalX),
            "comision": math.ceil(comisionX),
            "detalle": cuotas_x_list
        }

    cuotasDict["cantidad_total_cuotas"] = cantidadTotalCuotas
    cuotasDict["dinero_total_cuotas"] = math.ceil(dineroTotalCuotas)
    cuotasDict["comision_total_cuotas"] = math.ceil(comisionTotalCuotas)
    return cuotasDict

def get_detalle_cuotas_0(campania, agencia):
    """
    Cuotas 0 => redondear dinero_recadudado_cuotas_0
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
        "dinero_recadudado_cuotas_0": math.ceil(dinero_recadudado_cuotas_0)
    }

def get_premio_x_cantidad_ventas_sucursal(campania, agencia, objetivo_gerente=0):
    """
    1000 * cantidad_cuotas_0 si >= objetivo => se multiplica => potencial decimal no,
    pero se hace un int. Por seguridad, math.ceil.
    """
    objetivo_gerente = 200
    cantidad_cuotas_0 = get_detalle_cuotas_0(campania, agencia)["cantidad_cuotas_0"]

    if cantidad_cuotas_0 >= objetivo_gerente:
        return math.ceil(1000 * cantidad_cuotas_0)
    return 0

#endregion

#region Funciones para obtener y calcular el asegurado de los usuarios

def parse_campania_to_dates(campania_str):
    # sin cambios en parse; no hay redondeos
    meses_map = {
        "enero": 1,
        "febrero": 2,
        "marzo": 3,
        "abril": 4,
        "mayo": 5,
        "junio": 6,
        "julio": 7,
        "agosto": 8,
        "septiembre": 9,
        "setiembre": 9,
        "octubre": 10,
        "noviembre": 11,
        "diciembre": 12
    }

    partes = campania_str.split()
    if len(partes) != 2:
        raise ValueError(f"Formato de campaña inválido: {campania_str}")

    nombre_mes = partes[0].lower()
    anio = int(partes[1])

    if nombre_mes not in meses_map:
        raise ValueError(f"Mes inválido en la campaña: {nombre_mes}")

    mes = meses_map[nombre_mes]

    primer_dia = datetime.date(anio, mes, 1)
    ultimo_dia_num = calendar.monthrange(anio, mes)[1]
    ultimo_dia = datetime.date(anio, mes, ultimo_dia_num)

    return (primer_dia, ultimo_dia)

def calcular_asegurado_segun_dias_trabajados(dinero, usuario, campania_str):
    """
    Aplico math.ceil al proporcional. 
    """
    inicio_campania, fin_campania = parse_campania_to_dates(campania_str)

    fecha_ingreso = usuario.fec_ingreso
    if isinstance(fecha_ingreso, str):
        fecha_ingreso = datetime.datetime.strptime(fecha_ingreso, "%d/%m/%Y")

    fecha_egreso = usuario.fec_egreso if usuario.fec_egreso else None
    if fecha_egreso and isinstance(fecha_egreso, str):
        fecha_egreso = datetime.datetime.strptime(fecha_egreso, "%d/%m/%Y")

    if not fecha_egreso:
        fecha_egreso = datetime.datetime.now()

    if isinstance(fecha_ingreso, datetime.datetime):
        fecha_ingreso = fecha_ingreso.date()
    if isinstance(fecha_egreso, datetime.datetime):
        fecha_egreso = fecha_egreso.date()

    fecha_inicio_real = max(fecha_ingreso, inicio_campania)
    fecha_fin_real = min(fecha_egreso, fin_campania)

    if fecha_inicio_real > fecha_fin_real:
        dias_trabajados_campania = 0
    else:
        dias_trabajados_campania = (fecha_fin_real - fecha_inicio_real).days + 1

    print(f"Dias trabajados {dias_trabajados_campania}")
    if dias_trabajados_campania >= 30:
        return math.ceil(dinero)
    else:
        proporcional = (dinero / 30) * dias_trabajados_campania
        return math.ceil(proporcional)

def get_asegurado(usuario, campania_str):
    rango = usuario.rango.lower()
    if rango == "vendedor":
        asegurado_obj = Asegurado.objects.get(dirigido="Vendedor")
        dineroAsegurado = asegurado_obj.dinero
        return calcular_asegurado_segun_dias_trabajados(dineroAsegurado, usuario, campania_str)
    elif rango == "supervisor":
        asegurado_obj = Asegurado.objects.get(dirigido="Supervisor")
        dineroAsegurado = asegurado_obj.dinero
        return calcular_asegurado_segun_dias_trabajados(dineroAsegurado, usuario, campania_str)
    elif rango == "gerente sucursal":
        # Podrías hacer math.ceil si quieres 
        asegurado_obj = Asegurado.objects.get(dirigido="Gerente sucursal")
        return math.ceil(asegurado_obj.dinero)
    else:
        raise ValueError("Error al obtener el asegurado: rango no reconocido.")

#endregion

#region Funciones enfocadas en los descuentos

def get_ausencias_tardanzas(usuario, campania):
    """
    Retorna faltas/tardanzas con su total_descuentos. 
    Llamamos int(...) en la suma, si hubiera decimal => math.ceil. 
    Pero según tu MontoTardanzaAusencia, 
    si es entero no hace falta. Te muestro el uso de ceil:
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
    total_desc = math.ceil(total_desc)

    return {
        "total_descuentos": total_desc,
        "detalle": {
            "faltas": {
                "cantidad": len(faltas),
                "dinero": math.ceil(montoPorFalta * len(faltas)),
                "detalle": faltas
            },
            "tardanzas": {
                "cantidad": len(tardanzas),
                "dinero": math.ceil(montoPorTardanza * len(tardanzas)),
                "detalle": tardanzas
            }
        }
    }

#endregion

# Las funciones detalle_liquidado_ventasPropias, detalle_descuestos, etc.
# ya usan las de arriba, pero revisemos si necesitan un math.ceil extra.

def detalle_liquidado_ventasPropias(usuario, campania, agencia):
    """
    Al final sumas la subcomisión. Ya viene redondeada de get_detalle_comision_x_cantidad_ventasPropias
    y get_detalle_cuotas1. 
    Podrías forzar un math.ceil en 'subtotal'.
    """
    cantidad_ventas = calcular_cantidad_ventasPropias(usuario, campania, agencia)
    productividad_x_ventas_propias = calcular_productividad_ventasPropias(usuario, campania, agencia)
    
    dict_comision_cant_ventas = get_detalle_comision_x_cantidad_ventasPropias(usuario, campania, agencia)
    comision_x_cantidad_ventas_propias = dict_comision_cant_ventas["comision"]
    detalle_ventas_propias = dict_comision_cant_ventas["planes"]
    coeficienteSelected = dict_comision_cant_ventas["coeficienteSelected"]


    dict_cuotas1 = get_detalle_cuotas1(usuario, campania, agencia)
    comision_x_cuotas1 = dict_cuotas1["comision_total"]
    cantidad_cuotas1 = dict_cuotas1["cantidadCuotas1"]
    detalle_cuotas1 = dict_cuotas1["detalle"]

    subtotal = comision_x_cantidad_ventas_propias + comision_x_cuotas1
    subtotal = math.ceil(subtotal)

    resultado = {
        "comision_subtotal": subtotal,
        "coeficienteSelected": coeficienteSelected,
        "detalle": {
            "cantidadVentas": cantidad_ventas,  # entero
            "productividadXVentasPropias": productividad_x_ventas_propias,  # ceil
            "comisionXCantidadVentasPropias": comision_x_cantidad_ventas_propias,  # ya ceil
            "detalleVentasPropias": detalle_ventas_propias,
            "comisionXCuotas1": comision_x_cuotas1,  # ceil
            "cantidadCuotas1": cantidad_cuotas1,
            "detalleCuotas1": detalle_cuotas1
        }
    }
    return resultado

def detalle_descuestos(usuario, campania, agencia):
    """
    Aplica get_ausencias_tardanzas (que ya usa ceil).
    No se hace multiplicación extra, 
    así que con eso basta.
    """
    aus_tard_dict = get_ausencias_tardanzas(usuario, campania)
    descuento_x_tardanzas_faltas = aus_tard_dict["total_descuentos"]
    detalle_descuento_x_tardanzas_faltas = aus_tard_dict["detalle"]

    total_descuentos = descuento_x_tardanzas_faltas  # ya es ceil
    resultado = {
        "total_descuentos": total_descuentos,
        "detalle": {
            "tardanzas_faltas": detalle_descuento_x_tardanzas_faltas
        }
    }
    return resultado

def detalle_premios_x_objetivo(usuario, campania, agencia, objetivo_gerente=0):
    """
    get_premio_x_productividad_ventasPropias => ceil
    get_premio_x_cantidad_ventas_equipo => ceil
    get_premio_x_productividad_supervisor => ceil
    get_premio_x_cantidad_ventas_sucursal => ceil
    Sumamos => aplicamos ceil a final.
    """
    premio_subtotal = 0
    detalle = {}

    premio_x_productividad_ventas_propias = get_premio_x_productividad_ventasPropias(usuario, campania, agencia)

    rango_lower = str(usuario.rango).lower()
    if rango_lower == "supervisor":
        premio_x_cantidad_ventas_equipo = get_premio_x_cantidad_ventas_equipo(usuario, campania, agencia)
        premio_x_productividad_ventas_equipo = get_premio_x_productividad_supervisor(usuario, campania, agencia)
        detalle = {
            "premio_x_cantidad_ventas_equipo": premio_x_cantidad_ventas_equipo,
            "premio_x_productividad_ventas_equipo": premio_x_productividad_ventas_equipo
        }
        premio_subtotal += (premio_x_cantidad_ventas_equipo + premio_x_productividad_ventas_equipo)
    elif rango_lower == "gerente sucursal":
        premio_x_cantidad_ventas_agencia = get_premio_x_cantidad_ventas_sucursal(campania, agencia, objetivo_gerente)
        detalle = {
            "premio_x_cantidad_ventas_agencia": premio_x_cantidad_ventas_agencia,
        }
        premio_subtotal += premio_x_cantidad_ventas_agencia

    premio_subtotal += premio_x_productividad_ventas_propias
    premio_subtotal = math.ceil(premio_subtotal)

    detalle["premio_x_productividad_ventas_propias"] = premio_x_productividad_ventas_propias
    resultado = {
        "total_premios": premio_subtotal,
        "detalle": detalle
    }
    return resultado

def detalle_liquidado_x_rol(usuario, campania, agencia, porcentage_x_cuota_gerente=0):
    """
    P.ej. comision_x_cantidad_ventas_equipo => ceil
    comision_x_cuotas => ceil
    etc. Revisado arriba, devuelven ya en ceil.
    """
    rango_lower = str(usuario.rango).lower()

    if rango_lower == "supervisor":
        cantidad_ventas_x_equipo = calcular_ventas_supervisor(usuario, campania, agencia)
        productividad_x_equipo = calcular_productividad_supervisor(usuario, campania, agencia)
        comision_x_cantidad_ventas_equipo = get_comision_x_cantidad_ventas_equipo(usuario, campania, agencia)
        detalle_ventas_equipo = detalle_de_equipo_x_supervisor(usuario, campania, agencia)
        resultado = {
            "comision_subtotal": comision_x_cantidad_ventas_equipo,  # ya ceil
            "detalle": {
                "cantidadVentasXEquipo": cantidad_ventas_x_equipo,    # int
                "productividadXVentasEquipo": productividad_x_equipo, # ceil
                "detalleVentasXEquipo": detalle_ventas_equipo
            }
        }
        return resultado

    elif rango_lower == "gerente sucursal":
        dict_cuotas_0 = get_detalle_cuotas_0(campania, agencia)
        dict_cuotas_x = get_detalle_cuotas_x(campania, agencia, porcentage_x_cuota_gerente)

        cantidad_total_de_cuotas_0 = dict_cuotas_0["cantidad_cuotas_0"]  # int
        dinero_total_recaudado_cuotas_0 = dict_cuotas_0["dinero_recadudado_cuotas_0"]  # ceil

        cantidad_total_de_cuotas_x = dict_cuotas_x["cantidad_total_cuotas"]  # int
        dinero_total_recaudado_cuotas = dict_cuotas_x["dinero_total_cuotas"] # ceil
        comision_x_cuotas = dict_cuotas_x["comision_total_cuotas"]           # ceil
        detalle_x_cuotas = dict_cuotas_x["detalleCuota"]

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
        return resultado

    else:
        return {
            "comision_subtotal": 0,
            "detalle": {}
        }

def get_comision_total(usuario, campania, agencia, ajustes_usuario=None):
    """
    Finalmente, en la suma final se pueden generar decimales. 
    Aplicamos math.ceil en comision_bruta y comision_neta 
    si quieres “siempre redondear hacia arriba”.
    """
    if ajustes_usuario is None:
        ajustes_usuario = []

    # 1) Comisiones de ventas propias
    ventas_propias_dict = detalle_liquidado_ventasPropias(usuario, campania, agencia)
    comision_ventas_propias = ventas_propias_dict["comision_subtotal"]
    print(f"\n Detalle liquidado de -------- {usuario.nombre} --------:\n")
    print(f"{ventas_propias_dict}")
    # 2) Descuentos
    descuentos_dict = detalle_descuestos(usuario, campania, agencia)
    total_descuentos = descuentos_dict["total_descuentos"]

    # 3) Premios
    premios_dict = detalle_premios_x_objetivo(usuario, campania, agencia)
    total_premios = premios_dict["total_premios"]

    # 4) Comisión / bonos de rol
    rol_dict = detalle_liquidado_x_rol(usuario, campania, agencia)
    
    comision_rol = 0
    premios_segun_rol = 0

    rango_lower = usuario.rango.lower()
    if rango_lower == "vendedor":
        comision_rol = comision_ventas_propias
        premios_segun_rol += premios_dict["detalle"]["premio_x_productividad_ventas_propias"]
    elif rango_lower == "supervisor":
        comision_rol = rol_dict["comision_subtotal"]
        premios_segun_rol += (
            premios_dict["detalle"]["premio_x_productividad_ventas_equipo"] +
            premios_dict["detalle"]["premio_x_cantidad_ventas_equipo"]
        )
    elif rango_lower == "gerente sucursal":
        comision_rol = rol_dict["comision_subtotal"]
        premios_segun_rol += premios_dict["detalle"]["premio_x_cantidad_ventas_agencia"]

    sum_rol_premios = comision_rol + premios_segun_rol

    # 5) Asegurado
    try:
        asegurado_completo = get_asegurado(usuario, campania)
        print(f"\n ASEGURADO DE {usuario.nombre} -> {asegurado_completo}\n")
    except ValueError:
        asegurado_completo = 0

    # Comparamos con el asegurado
    diferencia_asegurado = 0
    if sum_rol_premios < asegurado_completo:
        diferencia_asegurado = asegurado_completo - sum_rol_premios
        comision_bruta = sum_rol_premios + diferencia_asegurado
    else:
        comision_bruta = sum_rol_premios

    # 6) Ajustes y descuentos
    ajustes_positivos = sum(a["dinero"] for a in ajustes_usuario if a["ajuste_tipo"] == "positivo")
    ajustes_negativos = sum(a["dinero"] for a in ajustes_usuario if a["ajuste_tipo"] == "negativo")

    total_descuentos += ajustes_negativos
    comision_bruta += ajustes_positivos

    # Si no es vendedor, sumamos comisiones de ventas propias nuevamente (+ premios) 
    if rango_lower != "vendedor":
        comision_bruta += (comision_ventas_propias + premios_dict["detalle"]["premio_x_productividad_ventas_propias"])

    comision_neta = comision_bruta - total_descuentos

    # Aplico math.ceil para que ambos sean redondeados hacia arriba
    comision_bruta = math.ceil(comision_bruta)
    comision_neta = math.ceil(comision_neta)
    diferencia_asegurado = math.ceil(diferencia_asegurado)

    resultado_final = {
        "comision_total": comision_neta,
        "comision_bruta": comision_bruta,
        "asegurado": diferencia_asegurado,
        "detalle": {
            "ventasPropias": ventas_propias_dict,
            "descuentos": descuentos_dict,
            "premios": premios_dict,
            "rol": rol_dict,
            "ajustes": {
                "ajustes_positivos": ajustes_positivos,
                "ajustes_negativos": ajustes_negativos
            }
        },
        "descuentoTotal": total_descuentos,
        "premiosTotal": total_premios,
    }

    return resultado_final
