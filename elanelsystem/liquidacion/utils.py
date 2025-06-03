from collections import defaultdict
from datetime import timedelta
from elanelsystem.utils import parse_fecha
from sales.models import Ventas,MovimientoExterno
from .models import *
from django.db.models import Q
import datetime
import calendar
import math
from users.utils import snapshot_usuario_by_campana

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

def calcular_cantidad_ventasPropias(usuario, campania, agencia=None):
    """
    Retorna la cantidad de ventas (según chances) propias de un usuario
    en una campaña y agencia dadas.
    (Esto ya es siempre entero, no hace falta math.ceil)
    """
    ventas_query = Ventas.objects.filter(
        vendedor=usuario,
        campania=campania,
        is_commissionable=True,
    )

    return sum(len(v.cantidadContratos) for v in ventas_query)  # siempre entero

def calcular_productividad_ventasPropias(usuario, campania, agencia=None):
    """
    Retorna la 'productividad' total de las ventas propias (sum of venta.importe).
    Aplico math.ceil por si 'importe' fuera flotante.
    """
    ventas_query = Ventas.objects.filter(
        vendedor=usuario,
        campania=campania,
        is_commissionable=True,
    )

    total = sum(venta.importe for venta in ventas_query)
    return math.ceil(total)  # redondeamos hacia arriba

def get_detalle_comision_x_cantidad_ventasPropias(usuario, campania, agencia=None):
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

    ventas_qs = Ventas.objects.filter(
        vendedor=usuario,
        campania=campania,
        is_commissionable=True,
    )

    cantVentas2 = sum(len(v.cantidadContratos) for v in ventas_qs)
    coeficienteSelected = 0
    for venta in ventas_qs:
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

def get_premio_x_productividad_ventasPropias(usuario, campania, agencia=None):
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
        is_commissionable=True,
    )

    productividad = sum(v.importe for v in ventas_qs)

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

def get_detalle_cuotas1(usuario, campania, agencia=None):
    from sales.models import PagoCannon
    """
    Cuotas 1 pagadas dentro de 15 días -> comision del 10% de la cuota 2.
    Aplico math.ceil a total_comision_x_cuota1.
    """
    from elanelsystem.utils import parse_fecha

     # 1) Traer de golpe SOLO los pagos de cuota 1 que me interesan
    pagos_qs = (
        PagoCannon.objects
        .filter(
            venta__vendedor=usuario,
            # venta__agencia=agencia,
            venta__is_commissionable=True,
            nro_cuota=1,
            campana_de_pago=campania,
        )
        .select_related('venta')
    )

    total_comision = 0
    detalle = []
    contratos_por_venta = {}   # cache cantidadContratos por venta.id
    fecha_alta_cache = {}      # cache fecha parseada de venta.fecha

    for pago in pagos_qs:
        venta = pago.venta
        vid = venta.id

        # 1) cache parseo de venta.fecha
        if vid not in fecha_alta_cache:
            fecha_alta_cache[vid] = parse_fecha(venta.fecha)

        # 2) comprobar plazo de 15 días
        fecha_pago = parse_fecha(pago.fecha)
        dias = (fecha_pago - fecha_alta_cache[vid]).days
        if dias > 15:
            continue

        # 3) cantidad de contratos de esa venta
        contratos_detalle = {}
        if vid not in contratos_por_venta:
            contratos_por_venta[vid] = len(venta.cantidadContratos)
            contratos_detalle[vid] = venta.cantidadContratos
        cant_contratos = contratos_por_venta[vid]
        contratos_detalle = contratos_detalle[vid]
        # 4) calculamos la comisión de esta venta (10% de cuota 2)
        cuota2_total = venta.cuotas[2]['total'] if len(venta.cuotas) > 2 else 0
        comision_venta = math.ceil(cuota2_total * 0.10)

        # 5) armamos el dict de detalle para esta “cuota 1”
        #    combinamos la dict original venta.cuotas[1] con los nuevos campos
        cuota1_info = venta.cuotas[1].copy()
        cuota1_info.update({
            "fecha_incripcion_venta": pago.venta.fecha,
            "fecha_pago": pago.fecha,
            "contratos": contratos_detalle,
            "comision": comision_venta,
            "cuota_comercial": cuota2_total
        })
        detalle.append(cuota1_info)

        total_comision += comision_venta

    return {
        "comision_total": math.ceil(total_comision),
        "detalle": detalle,
        "cantidadCuotas1": sum(contratos_por_venta.values()),
    }


def comisiones_brutas_vendedor(usuario,campania,agencia=None):
    """
    Devuelve la comision bruta del vendedor. 
    """
    comision_x_cantidad_ventas = get_detalle_comision_x_cantidad_ventasPropias(usuario, campania)["comision"]
    comision_x_cuotas1 = get_detalle_cuotas1(usuario, campania)["comision_total"]
    comision_x_productividad = get_premio_x_productividad_ventasPropias(usuario, campania)
    
    return {
        "comision_total": math.ceil(comision_x_cantidad_ventas + comision_x_cuotas1 + comision_x_productividad),
        "comision_x_cantidad_ventas": comision_x_cantidad_ventas,
        "comision_x_cuotas1": comision_x_cuotas1,
        "comision_x_productividad": comision_x_productividad       
    }

#endregion

#region Funciones enfocadas a los  supervisores

def calcular_ventas_supervisor(usuario, campania, agencia=None):
    """
    Cantidad de ventas totales del supervisor. (Siempre entero)
    """
    ventas_qs = Ventas.objects.filter(
        supervisor=usuario,
        campania=campania,
        # agencia=agencia,
        is_commissionable=True,
    )

    return sum(len(v.cantidadContratos) for v in ventas_qs)  # entero

def calcular_productividad_supervisor(usuario, campania, agencia=None):
    """
    Productividad total (sum of venta.importe). Aplico math.ceil.
    """
    ventas_qs = Ventas.objects.filter(
        supervisor=usuario,
        campania=campania,
        # agencia=agencia,
        is_commissionable=True,
    )

    total = sum(v.importe for v in ventas_qs)
    return math.ceil(total)

def get_premio_x_productividad_supervisor(usuario, campania, agencia=None):
    """
    Multiplicamos total_prod * coef. => ahí puede salir decimal => math.ceil
    """
    total_prod = calcular_productividad_supervisor(usuario, campania)
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

def get_premio_x_cantidad_ventas_equipo(usuario, campania, agencia=None):
    """
    Devuelve dineroAsegurado si la suma de ventas > 80, sino 0. 
    No hace falta ceil, pues dineroAsegurado es un entero. 
    Igual, por seguridad, podría hacerse math.ceil.
    """
    asegurado = Asegurado.objects.get(dirigido="Supervisor")
    dineroAsegurado = asegurado.dinero
    cantidad_ventas_x_equipo = calcular_ventas_supervisor(usuario,campania)
    
    if cantidad_ventas_x_equipo > 80:
        return math.ceil(dineroAsegurado)
    return 0

def get_comision_x_cantidad_ventas_equipo(usuario, campania, agencia=None):
    """
    total += venta.importe * coef => decimal => uso ceil en el final.
    """
    ventas_qs = Ventas.objects.filter(
        supervisor=usuario,
        campania=campania,
        # agencia=agencia,
        is_commissionable=True,
    )

    cantVentas = sum(len(v.cantidadContratos) for v in ventas_qs)

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
    for venta in ventas_qs:
        total += venta.importe * coef

    return math.ceil(total)

def detalle_de_equipo_x_supervisor(usuario, campania, agencia=None):
    """
    Lista con nombre, cantidad de ventas y productividad.
    Cantidad de ventas = entero; productividad = redondeo arriba.
    """
    ventas_qs = Ventas.objects.filter(
        supervisor=usuario,
        campania=campania,
        # agencia=agencia,
        is_commissionable=True,
    )
    
    detalle_vendedores = []
    for venta in ventas_qs:
        vend = venta.vendedor
        detalle = get_detalle_comision_x_cantidad_ventasPropias(vend, campania)["planes"]
        
        # detalle = detalle["planes"]
        item = {
            "nombre": vend.nombre,
            "cantidad_ventas": calcular_cantidad_ventasPropias(vend, campania),
            "productividad": calcular_productividad_ventasPropias(vend, campania),
            "detalle": detalle["com_24_30_motos"]["ventas"] + detalle["com_24_30_prestamo_combo"]["ventas"] + detalle["com_48_60"]["ventas"]
        }
        detalle_vendedores.append(item)
    return detalle_vendedores

def comisiones_brutas_supervisor(usuario,campania,agencia=None):
    """
    Devuelve la comision bruta del supervisor. 
    """
    comision_x_cantidad_ventas = get_comision_x_cantidad_ventas_equipo(usuario, campania)
    comision_x_productividad = get_premio_x_productividad_supervisor(usuario, campania)
    comision_x_ventas_equipo = get_premio_x_cantidad_ventas_equipo(usuario, campania)

    return {
        "comision_total": math.ceil(comision_x_cantidad_ventas + comision_x_productividad + comision_x_ventas_equipo),
        "comision_x_cantidad_ventas": comision_x_cantidad_ventas,
        "comision_x_productividad": comision_x_productividad,
        "comision_x_ventas_equipo": comision_x_ventas_equipo,
    }
#endregion

#region Funciones enfocadas a los gerentes de sucursal
def get_detalle_cuotas_x2(pagos_sucursal, porcentaje_x_cuota, gerente):
    """
    Comision de cuotas 1,2,3,4 => math.ceil en comision_total_cuotas.
    Ahora usamos solo PagoCannon para extraer los pagos ya filtrados.
    """
    
    cuotas_numeros = [1, 2, 3, 4]
    # Estructura base para acumular
    stats = {
        nro: {"cantidad": 0, "dinero": 0, "detalle": [], "cuotas": []}
        for nro in cuotas_numeros
    }

    # Filtrar en memoria LOS pagos válidos para este gerente en esta sucursal:
    pagos_validos = [
        p for p in pagos_sucursal
        if p.nro_cuota in cuotas_numeros
           and p.venta.gerente_id == gerente.id
           and p.venta.is_commissionable
    ]

    # Acumular en stats
    for pago in pagos_validos:
        idx = pago.nro_cuota
        venta = pago.venta
        total_cuota = venta.cuotas[idx].get("total", 0)
        contratos = len(venta.cantidadContratos)

        stats[idx]["cantidad"] += contratos
        stats[idx]["dinero"] += total_cuota
        stats[idx]["detalle"].append(total_cuota)
        # Agregamos al detalle de sub‐cuotas el dict original + metadata
        stats[idx]["cuotas"].append({
            **venta.cuotas[idx],
            "nro_cuota": idx,
            "nro_recibo": pago.nro_recibo,
            "fecha_pago": pago.fecha,
            "venta_id": venta.id,
            "cliente": venta.nro_cliente.nombre if venta.nro_cliente else None,
        })

    # Construir el resultado final
    result = {
        "porcentaje_x_cuota": porcentaje_x_cuota,
        "detalleCuota": {},
        "cantidad_total_cuotas": 0,
        "dinero_total_cuotas": 0,
        "comision_total_cuotas": 0,
    }

    for nro in cuotas_numeros:
        dinero = stats[nro]["dinero"]
        comision = dinero * porcentaje_x_cuota

        result["detalleCuota"][f"cuotas{nro}"] = {
            "cantidad": stats[nro]["cantidad"],
            "dinero_x_cuota": math.ceil(dinero),
            "comision": math.ceil(comision),
            "detalle": stats[nro]["detalle"],
            "cuotas": stats[nro]["cuotas"],
        }
        result["cantidad_total_cuotas"] += stats[nro]["cantidad"]
        result["dinero_total_cuotas"] += dinero
        result["comision_total_cuotas"] += comision

    result["dinero_total_cuotas"] = math.ceil(result["dinero_total_cuotas"])
    result["comision_total_cuotas"] = math.ceil(result["comision_total_cuotas"])
    return result


def get_detalle_cuotas_02(pagos_sucursal):
    """
    Cuotas 0 => redondear dinero_recadudado_cuotas_0
    Ahora usando solo PagoCannon para extraer pagos de cuota 0.
    """

    pagos0 = [p for p in pagos_sucursal if p.nro_cuota == 0]

    cantidad_cuotas_0 = sum(len(p.venta.cantidadContratos) for p in pagos0)
    dinero_recaudado_cuotas_0 = sum(p.monto for p in pagos0)

    detalle = [
        {
            "nro_recibo": p.nro_recibo,
            "fecha_pago": p.fecha,
            "monto": p.monto,
            "venta_id": p.venta.id,
            "vendedor": p.venta.vendedor.nombre if p.venta.vendedor else None,
        }
        for p in pagos0
    ]

    return {
        "cantidad_cuotas_0": cantidad_cuotas_0,
        "dinero_recaudado_cuotas_0": math.ceil(dinero_recaudado_cuotas_0),
        "detalle_pagos": detalle,
    }


def get_premio_x_cantidad_ventas_sucursal2(campania, agencia, objetivo_gerente=0):
    from elanelsystem.utils import get_sucursales_por_provincias
    
    """
    1000 * cantidad_cuotas_0 si >= objetivo => se multiplica => potencial decimal no,
    pero se hace un int. Por seguridad, math.ceil.
    """
    # objetivo_gerente = 200
    cantidad_cuotas_0 = get_detalle_cuotas_0(campania, agencia)["cantidad_cuotas_0"]

    if cantidad_cuotas_0 >= objetivo_gerente:
        return math.ceil(1000 * cantidad_cuotas_0)
    return 0


def get_detalle_sucursales_de_region2(gerente, agencia, campania):
    from sales.models import PagoCannon
    from elanelsystem.utils import get_sucursales_por_provincias


    # 1) Obtener nombres de sucursales de la región y sus objetos
    nombres_region = get_sucursales_por_provincias(agencia)
    sucursales_region_objs = list(
        Sucursal.objects.filter(pseudonimo__in=nombres_region)
    )

    all_pagos_by_region = (
        PagoCannon.objects
        .filter(
            Q(venta__agencia__in=sucursales_region_objs),
            venta__is_commissionable=True,
            nro_cuota__in=[0, 1, 2, 3, 4],
            campana_de_pago=campania
        )
        .select_related("venta", "venta__agencia")
    )

    all_pagos_by_gerente = (
        PagoCannon.objects
        .filter(
            Q(venta__gerente=gerente) & ~Q(venta__agencia__in=sucursales_region_objs),
            venta__is_commissionable=True,
            nro_cuota__in=[0, 1, 2, 3, 4],
            campana_de_pago=campania
        )
        .select_related("venta", "venta__agencia")
    )



    # 4) Listas para decidir porcentajes y premios
    agencias_8_porc = [
        "Corrientes, Corrientes", "Concordia, Entre Rios", "Resistencia, Chaco",
        "Posadas, Misiones", "Santiago Del Estero, Santiago Del Estero",
        "Formosa, Formosa", "Saenz Peña, Chaco"
    ]
    agencias_6_porc = ["Paso De Los Libres, Corrientes", "Goya, Corrientes"]
    agencias_objs_200_ventas = [
        "Corrientes, Corrientes", "Concordia, Entre Rios", "Resistencia, Chaco",
        "Posadas, Misiones", "Santiago Del Estero, Santiago Del Estero", "Formosa, Formosa"
    ]

    # 5) Diccionario de resultado
    result = {
        "detalleRegion": {},
        "porcetage_x_cuota": 0,
        "cantidad_total_cuotas": 0,
        "dinero_total_cuotas": 0,
        "comision_total_cuotas": 0,
        "dinero_recadudado_cuotas_0": 0,
    }

    # 2) Agrupar pagos por sucursal para los pagos de la region
    pagos_por_sucursal = defaultdict(list)
    for p in all_pagos_by_region:
        pagos_por_sucursal[p.venta.agencia_id].append(p)

    # 3) Agrupar pagos por sucursal para los pagos que corresponden solamente al gerente
    pagos_del_gerente = defaultdict(list)
    for p in all_pagos_by_gerente:
        pagos_del_gerente[p.venta.agencia_id].append(p)

    
    for p in all_pagos_by_region:
        

    # for suc_obj  in sucursales_involucradas:
    #     suc_nombre = suc_obj.pseudonimo
    #     porcentaje_1_4 = 0.08 if suc_nombre in agencias_8_porc else 0.06


        


    #     sucObject = Sucursal.objects.filter(pseudonimo=suc).first()
    #     porcentage_x_cuota = 0
    #     premios_por_venta = 0

    #     if(sucObject != agencia):
    #         porcentage_x_cuota = 0.03
    #         pagos_by_region = [p for p in all_pagos if p.venta.gerente != gerente and p.venta.agencia == sucObject]
    #     else:
    #         porcentage_x_cuota = 0.08 if suc in agencias_8_porc else 0.06
    #         pagos_by_region = [p for p in all_pagos if p.venta.gerente == gerente and p.venta.agencia == sucObject]

    #         if(suc in agencias_objs_200_ventas):
    #             premios_por_venta = get_premio_x_cantidad_ventas_sucursal(campania, sucObject, 200)

    #         else:
    #             premios_por_venta = get_premio_x_cantidad_ventas_sucursal(campania, sucObject, 150)
                
    #     result["porcetage_x_cuota"] = porcentage_x_cuota

    #     suc_clean = sucObject.pseudonimo.replace(" ", "").replace(",", "").lower()
        
    #     detalle_cuota_x = get_detalle_cuotas_x2(campania,sucObject,porcentage_x_cuota)
    #     detalle_cuota_0 = get_detalle_cuotas_02(campania,sucObject)

    #     result["detalleRegion"][f"{suc_clean}"] = {
    #         "suc_id": sucObject.id,
    #         "suc_name": sucObject.pseudonimo,
    #         "suc_info": detalle_cuota_x | detalle_cuota_0 ,
    #         "premios_por_venta": math.ceil(premios_por_venta),
    #         "sub_total":math.ceil(detalle_cuota_x["comision_total_cuotas"] + premios_por_venta)
    #     }

    #     result["cantidad_total_cuotas"] += math.ceil(detalle_cuota_x["cantidad_total_cuotas"])
    #     result["dinero_total_cuotas"] += math.ceil(detalle_cuota_x["dinero_total_cuotas"])
    #     result["comision_total_cuotas"] += math.ceil(detalle_cuota_x["comision_total_cuotas"])
    #     result["dinero_recadudado_cuotas_0"] += math.ceil(detalle_cuota_0["dinero_recadudado_cuotas_0"])

    # # Analisis 2) Manejo cuyos pagos son del gerente en cuestion sin importar su region, sino por el simple hecho trabajado en esa sucursal
    # sucursal_ids_involucradas = all_pagos.values_list("venta__agencia_id", flat=True).distinct()
    # sucursales_involucradas = Sucursal.objects.filter(id__in=list(sucursal_ids_involucradas))

    # for suc in sucursales_involucradas:
    #     pagos_by_gerente = [p for p in all_pagos if p.venta.gerente == gerente and agencia != suc]
    #     porcentage_x_cuota = 0.08 if suc.pseudonimo in agencias_8_porc else 0.06

    #     suc_clean = sucObject.pseudonimo.replace(" ", "").replace(",", "").lower()

    #     detalle_cuota_x = get_detalle_cuotas_x2(campania,sucObject,porcentage_x_cuota)
    #     detalle_cuota_0 = get_detalle_cuotas_02(campania,sucObject)

    #     if result["detalleRegion"].get(f"{suc_clean}"):
    #         result["detalleRegion"][f"{suc_clean}"]["suc_info"].update(detalle_cuota_x | detalle_cuota_0)
    #         result["detalleRegion"][f"{suc_clean}"]["sub_total"] += math.ceil(detalle_cuota_x["comision_total_cuotas"])
    #     else:
    #         result["detalleRegion"][f"{suc_clean}"] = {
    #             "suc_id": suc.id,
    #             "suc_name": suc.pseudonimo,
    #             "suc_info": detalle_cuota_x | detalle_cuota_0,
    #             "premios_por_venta": 0,  # No aplica en este caso
    #             "sub_total": math.ceil(detalle_cuota_x["comision_total_cuotas"])
    #         }
    #     result["cantidad_total_cuotas"] += math.ceil(detalle_cuota_x["cantidad_total_cuotas"])
    #     result["dinero_total_cuotas"] += math.ceil(detalle_cuota_x["dinero_total_cuotas"])
    #     result["comision_total_cuotas"] += math.ceil(detalle_cuota_x["comision_total_cuotas"])
    #     result["dinero_recadudado_cuotas_0"] += math.ceil(detalle_cuota_0["dinero_recadudado_cuotas_0"])
    

    # # Agrupo los pagos segun corresponda a su comision
    # weps= {}
    # for suc_id, pagos in pagos_por_sucursal.items():
    #     weps["agencia_id"] = suc_id
    #     for p in pagos:
    #         venta = p.venta
    #         suc = venta.agencia.pseudonimo
    #         gerente = venta.gerente

    #         if():
    #             pass
    #         elif():
    #             pass
    #         elif():
    #             pass
                







def get_detalle_cuotas_x(campania, agencia, porcetage_x_cuota):
    """
    Comision de cuotas 1,2,3,4 => math.ceil en comision_total_cuotas.
    Ahora usamos solo PagoCannon para extraer los pagos ya filtrados.
    """
    from sales.models import PagoCannon
    # Los índices de cuota que nos interesan
    cuotas_numeros = [1, 2, 3, 4]

    # Diccionario base
    result = {
        "porcetage_x_cuota": porcetage_x_cuota,
        "detalleCuota": {},
        "cantidad_total_cuotas": 0,
        "dinero_total_cuotas": 0,
        "comision_total_cuotas": 0,
    }

    # Inicializamos acumuladores por cuota
    stats = {
        nro: {"cantidad": 0, "dinero": 0, "detalle": [], "cuotas":[]}
        for nro in cuotas_numeros
    }

    # 1) Traemos todos los pagos que cumplan las condiciones
    pagos = (
        PagoCannon.objects
        .filter(
            venta__agencia=agencia,
            venta__is_commissionable=True,
            nro_cuota__in=cuotas_numeros,
            campana_de_pago=campania,
        )
        .select_related("venta")  # para no golpear la db al leer pago.venta
    )

    # 2) Recorremos solo los pagos válidos
    for pago in pagos:
        venta = pago.venta
        idx = pago.nro_cuota
        cuota_info = venta.cuotas[idx]
        total_cuota = venta.cuotas[5]["total"]
        n_contratos = len(venta.cantidadContratos)
        
        cuota_info.update({
            "fecha_pago": pago.fecha,
            "contratos": venta.cantidadContratos,
        })

        stats[idx]["cantidad"] += n_contratos
        stats[idx]["dinero"]   += total_cuota
        stats[idx]["detalle"].append(total_cuota)
        stats[idx]["cuotas"].append(cuota_info)

    # 3) Construimos el bloque de salida y acumulamos totales
    for nro in cuotas_numeros:
        dinero = stats[nro]["dinero"]
        comision = dinero * porcetage_x_cuota

        result["detalleCuota"][f"cuotas{nro}"] = {
            "cantidad": stats[nro]["cantidad"],
            "dinero_x_cuota": math.ceil(dinero),
            "comision": math.ceil(comision),
            "detalle": stats[nro]["detalle"],
            "cuotas":  stats[nro]["cuotas"]
        }

        result["cantidad_total_cuotas"]   += stats[nro]["cantidad"]
        result["dinero_total_cuotas"]     += dinero
        result["comision_total_cuotas"]   += comision

    # 4) Redondeos finales
    result["dinero_total_cuotas"]   = math.ceil(result["dinero_total_cuotas"])
    result["comision_total_cuotas"] = math.ceil(result["comision_total_cuotas"])

    return result


def get_detalle_cuotas_0(campania, agencia):
    """
    Cuotas 0 => redondear dinero_recadudado_cuotas_0
    Ahora usando solo PagoCannon para extraer pagos de cuota 0.
    """
    from sales.models import PagoCannon


    # 1) Traer todos los pagos de cuota 0 para la campaña y agencia dadas
    pagos0 = (
        PagoCannon.objects
        .filter(
            venta__agencia=agencia,
            venta__campania=campania,
            venta__is_commissionable=True,
            nro_cuota=0,
            campana_de_pago=campania,
        )
        .select_related("venta")  # evitar JOIN extra al leer venta
    )

    # 2) Contar cuántas "cuotas 0" efectivas (= número de contratos por venta)
    cantidad_cuotas_0 = sum(len(pago.venta.cantidadContratos) for pago in pagos0)

    # 3) Sumar todo el dinero recaudado de esas cuotas 0
    dinero_recadudado_cuotas_0 = sum(pago.monto for pago in pagos0)

    # 4) Devolver el mismo formato de dict, con ceil en el dinero
    return {
        "cantidad_cuotas_0": cantidad_cuotas_0,
        "dinero_recadudado_cuotas_0": math.ceil(dinero_recadudado_cuotas_0),
    }


def get_premio_x_cantidad_ventas_sucursal(campania, agencia, objetivo_gerente=0):
    from elanelsystem.utils import get_sucursales_por_provincias
    
    """
    1000 * cantidad_cuotas_0 si >= objetivo => se multiplica => potencial decimal no,
    pero se hace un int. Por seguridad, math.ceil.
    """
    # objetivo_gerente = 200
    cantidad_cuotas_0 = get_detalle_cuotas_0(campania, agencia)["cantidad_cuotas_0"]

    if cantidad_cuotas_0 >= objetivo_gerente:
        return math.ceil(1000 * cantidad_cuotas_0)
    return 0


def get_detalle_sucursales_de_region(agencia,campania):
    from elanelsystem.utils import get_sucursales_por_provincias
    
    agencias_8_porc =["Corrientes, Corrientes", "Concordia, Entre Rios", "Resistencia, Chaco","Posadas, Misiones","Santiago Del Estero, Santiago Del Estero","Formosa, Formosa","Saenz Peña, Chaco"]
    agencias_6_porc =["Paso De Los Libres, Corrientes", "Goya, Corrientes"]
    agencias_objs_200_ventas = ["Corrientes, Corrientes", "Concordia, Entre Rios", "Resistencia, Chaco","Posadas, Misiones","Santiago Del Estero, Santiago Del Estero","Formosa, Formosa"]
    result = {
        "detalleRegion": {},
        "porcetage_x_cuota": 0,
        "cantidad_total_cuotas": 0,
        "dinero_total_cuotas": 0,
        "comision_total_cuotas": 0,
        "cantidad_cuotas_0": 0,
        "dinero_recadudado_cuotas_0": 0,
    }

    lista_sucursales = get_sucursales_por_provincias(agencia)

    for suc in lista_sucursales:
        sucObject = Sucursal.objects.filter(pseudonimo=suc).first()
        porcentage_x_cuota = 0
        premios_por_venta = 0

        if(sucObject != agencia):
            porcentage_x_cuota = 0.03
        else:
            porcentage_x_cuota = 0.08 if suc in agencias_8_porc else 0.06
            if(suc in agencias_objs_200_ventas):
                premios_por_venta = get_premio_x_cantidad_ventas_sucursal(campania, sucObject, 200)

            else:
                premios_por_venta = get_premio_x_cantidad_ventas_sucursal(campania, sucObject, 150)
                
        result["porcetage_x_cuota"] = porcentage_x_cuota

        suc_clean = sucObject.pseudonimo.replace(" ", "").replace(",", "").lower()
        
        detalle_cuota_x = get_detalle_cuotas_x(campania,sucObject,porcentage_x_cuota)
        detalle_cuota_0 = get_detalle_cuotas_0(campania,sucObject)

        result["detalleRegion"][f"{suc_clean}"] = {
            "suc_id": sucObject.id,
            "suc_name": sucObject.pseudonimo,
            "suc_info": detalle_cuota_x | detalle_cuota_0 ,
            "premios_por_venta": math.ceil(premios_por_venta),
            "sub_total":math.ceil(detalle_cuota_x["comision_total_cuotas"] + premios_por_venta)
        }

        result["cantidad_total_cuotas"] += math.ceil(detalle_cuota_x["cantidad_total_cuotas"])
        result["dinero_total_cuotas"] += math.ceil(detalle_cuota_x["dinero_total_cuotas"])
        result["comision_total_cuotas"] += math.ceil(detalle_cuota_x["comision_total_cuotas"])
        result["dinero_recadudado_cuotas_0"] += math.ceil(detalle_cuota_0["dinero_recadudado_cuotas_0"])
    return result


def comisiones_brutas_gerente(agencia,campania):
    """
    Devuelve la comision bruta del gerente.
    """
    detalle_region = get_detalle_sucursales_de_region(agencia,campania)["detalleRegion"]

    total_comision = 0
    for r in detalle_region.values():
        total_comision += r["sub_total"]

    return {
        "comision_total": math.ceil(total_comision),
        "detalle_region": detalle_region,
    }

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
    snapshot_usuario_by_campania = snapshot_usuario_by_campana(usuario, campania_str)

    rango = snapshot_usuario_by_campania[0].rango.lower()
    if rango == "vendedor":
        asegurado_obj = Asegurado.objects.get(dirigido="Vendedor")
        dineroAsegurado = asegurado_obj.dinero
        return calcular_asegurado_segun_dias_trabajados(dineroAsegurado, snapshot_usuario_by_campania[0], campania_str)
    elif rango == "supervisor":
        asegurado_obj = Asegurado.objects.get(dirigido="Supervisor")
        dineroAsegurado = asegurado_obj.dinero
        return calcular_asegurado_segun_dias_trabajados(dineroAsegurado, snapshot_usuario_by_campania[0], campania_str)
    elif rango == "gerente sucursal":
        # Podrías hacer math.ceil si quieres 
        asegurado_obj = Asegurado.objects.get(dirigido="Gerente sucursal")
        return math.ceil(asegurado_obj.dinero)
    else:
        raise ValueError("Error al obtener el asegurado: rango no reconocido.")
    

    # rango = usuario.rango.lower()
    # if rango == "vendedor":
    #     asegurado_obj = Asegurado.objects.get(dirigido="Vendedor")
    #     dineroAsegurado = asegurado_obj.dinero
    #     return calcular_asegurado_segun_dias_trabajados(dineroAsegurado, usuario, campania_str)
    # elif rango == "supervisor":
    #     asegurado_obj = Asegurado.objects.get(dirigido="Supervisor")
    #     dineroAsegurado = asegurado_obj.dinero
    #     return calcular_asegurado_segun_dias_trabajados(dineroAsegurado, usuario, campania_str)
    # elif rango == "gerente sucursal":
    #     # Podrías hacer math.ceil si quieres 
    #     asegurado_obj = Asegurado.objects.get(dirigido="Gerente sucursal")
    #     return math.ceil(asegurado_obj.dinero)
    # else:
    #     raise ValueError("Error al obtener el asegurado: rango no reconocido."

#endregion

#region Funciones enfocadas en los descuentos

def get_ausencias_tardanzas(usuario, campania):
    from users.models import Ausencia
    """
    Retorna faltas/tardanzas del modelo Ausencia para el usuario y campaña dada,
    calculando totales y devolviendo un dict con la misma forma que antes.
    """

    # 2) Filtrar todas las Ausencia de este usuario en esa campaña
    qs = Ausencia.objects.filter(usuario=usuario, campania=campania)


    # 3) Separar faltas y tardanzas
    faltas = [a for a in qs if a.tipo.lower() == "falta"]
    tardanzas = [a for a in qs if a.tipo.lower() == "tardanza"]

    # 4) Obtener montos
    objMonto = MontoTardanzaAusencia.objects.first()
    montoPorFalta = objMonto.monto_ausencia
    montoPorTardanza = objMonto.monto_tardanza

    # 5) Total descuentos
    total_desc = math.ceil(len(faltas) * montoPorFalta + len(tardanzas) * montoPorTardanza)

    # 6) Construir las listas de detalle con el mismo esquema de keys
    def to_dict(a):
        return {
            "tipoEvento": a.tipo,
            "campania": campania,
            "dia": a.dia,
            "hora": a.hora,
            "motivo": a.motivo,
            "fecha_de_carga": a.fecha_de_carga,
        }

    detalle_faltas = [to_dict(a) for a in faltas]
    detalle_tardanzas = [to_dict(a) for a in tardanzas]

    return {
        "total_descuentos": total_desc,
        "detalle": {
            "faltas": {
                "cantidad": len(faltas),
                "dinero": math.ceil(len(faltas) * montoPorFalta),
                "detalle": detalle_faltas
            },
            "tardanzas": {
                "cantidad": len(tardanzas),
                "dinero": math.ceil(len(tardanzas) * montoPorTardanza),
                "detalle": detalle_tardanzas
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
    comisiones_brutas = comisiones_brutas_vendedor(usuario, campania, agencia)
    productividad_x_ventas_propias = calcular_productividad_ventasPropias(usuario, campania, agencia)
    
    dict_comision_cant_ventas = get_detalle_comision_x_cantidad_ventasPropias(usuario, campania, agencia)
    # comision_x_cantidad_ventas_propias = dict_comision_cant_ventas["comision"]
    detalle_ventas_propias = dict_comision_cant_ventas["planes"]
    coeficienteSelected = dict_comision_cant_ventas["coeficienteSelected"]


    dict_cuotas1 = get_detalle_cuotas1(usuario, campania, agencia)
    # comision_x_cuotas1 = dict_cuotas1["comision_total"]
    cantidad_cuotas1 = dict_cuotas1["cantidadCuotas1"]
    detalle_cuotas1 = dict_cuotas1["detalle"]

    # subtotal = comision_x_cantidad_ventas_propias + comision_x_cuotas1
    # subtotal = math.ceil(subtotal)

    resultado = {
        **comisiones_brutas,
        "coeficienteSelected": coeficienteSelected,
        "cantidadVentas": cantidad_ventas,
        "productividadXVentasPropias": productividad_x_ventas_propias, 
        "cantidadCuotas1": cantidad_cuotas1,
        "detalle": {
            "detalleVentasPropias": detalle_ventas_propias,
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

def detalle_liquidado_x_rol(usuario, campania, agencia, porcentage_x_cuota_gerente=0):
    """
    P.ej. comision_x_cantidad_ventas_equipo => ceil
    comision_x_cuotas => ceil
    etc. Revisado arriba, devuelven ya en ceil.
    """
    snapshot_usuario_by_campania = snapshot_usuario_by_campana(usuario, campania)
    rango_lower = snapshot_usuario_by_campania[0].rango.lower()

    if rango_lower == "supervisor":
        comisiones_brutas = comisiones_brutas_supervisor(usuario, campania, agencia)
        cantidad_ventas_x_equipo = calcular_ventas_supervisor(usuario, campania, agencia)
        productividad_x_equipo = calcular_productividad_supervisor(usuario, campania, agencia)
        # comision_x_cantidad_ventas_equipo = get_comision_x_cantidad_ventas_equipo(usuario, campania, agencia)
        # detalle_ventas_equipo = detalle_de_equipo_x_supervisor(usuario, campania, agencia)
        resultado = {
            **comisiones_brutas,
            "cantidadVentasXEquipo": cantidad_ventas_x_equipo,
            "productividadXVentasEquipo": productividad_x_equipo,
        }

        # resultado = {
        #     "comision_subtotal": comision_x_cantidad_ventas_equipo,  # ya ceil
        #     "detalle": {
        #         "cantidadVentasXEquipo": cantidad_ventas_x_equipo,    # int
        #         "productividadXVentasEquipo": productividad_x_equipo, # ceil
        #         "detalleVentasXEquipo": detalle_ventas_equipo
        #     }
        # }
        return resultado

    elif rango_lower == "gerente sucursal":
        detalleRegion = get_detalle_sucursales_de_region(agencia, campania)
        region = detalleRegion["detalleRegion"]         

        resultado = {**region}
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

    # print(f"\n ✅ Detalle de ventas propias liquidadas de -------- {usuario.nombre} --------:\n")
    # print(f"{ventas_propias_dict}")

    # 2) Descuentos
    descuentos_dict = detalle_descuestos(usuario, campania, agencia)
    total_descuentos = descuentos_dict["total_descuentos"]


    # 4) Comisión / bonos de rol
    rol_dict = detalle_liquidado_x_rol(usuario, campania, agencia)
    # print(f"\n ✅ Detalle de rol liquidadas de -------- {usuario.nombre} --------:\n")
    # print(f"{rol_dict}")
    
    snapshot_usuario_by_campania = snapshot_usuario_by_campana(usuario, campania)
    rango_lower = snapshot_usuario_by_campania[0].rango.lower()
    # rango_lower = usuario.rango.lower()
    comision_bruta_inicial = 0
    if rango_lower == "vendedor":
        comision_bruta_inicial = comisiones_brutas_vendedor(usuario,campania,agencia)["comision_total"]
    elif rango_lower == "supervisor":
        comision_bruta_inicial = comisiones_brutas_supervisor(usuario,campania,agencia)["comision_total"]
    elif rango_lower == "gerente sucursal":
        comision_bruta_inicial = comisiones_brutas_gerente(agencia,campania)["comision_total"]

    # 5) Asegurado
    try:
        asegurado_completo = get_asegurado(usuario, campania)
        # print(f"\n ASEGURADO DE {usuario.nombre} -> {asegurado_completo}\n")
    except ValueError as e:
        # print("\nError en get_asegurado()\n")
        # print(e)
        asegurado_completo = 0

    # Comparamos con el asegurado
    diferencia_asegurado = 0
    if comision_bruta_inicial < asegurado_completo:
        diferencia_asegurado = asegurado_completo - comision_bruta_inicial
        comision_bruta_final = comision_bruta_inicial + diferencia_asegurado
    else:
        comision_bruta_final = comision_bruta_inicial

    # 6) Ajustes y descuentos
    ajustes_positivos = sum(a["dinero"] for a in ajustes_usuario if a["ajuste_tipo"] == "positivo")
    ajustes_negativos = sum(a["dinero"] for a in ajustes_usuario if a["ajuste_tipo"] == "negativo")

    total_descuentos += ajustes_negativos
    comision_bruta_final += ajustes_positivos

    # Si no es vendedor, sumamos comisiones de ventas propias nuevamente (+ premios) 
    if rango_lower != "vendedor":
        comision_bruta_final += comisiones_brutas_vendedor(usuario,campania,agencia)["comision_total"]

    comision_neta = comision_bruta_final - total_descuentos

    # Aplico math.ceil para que ambos sean redondeados hacia arriba
    comision_bruta_final = math.ceil(comision_bruta_final)
    comision_neta = math.ceil(comision_neta)
    diferencia_asegurado = math.ceil(diferencia_asegurado)

    resultado_final = {
        "comision_total": comision_neta,
        "comision_bruta": comision_bruta_final,
        "asegurado": diferencia_asegurado,
        "detalle": {
            "ventasPropias": ventas_propias_dict,
            "descuentos": descuentos_dict,
            "rol": rol_dict,
            "ajustes": {
                "ajustes_positivos": ajustes_positivos,
                "ajustes_negativos": ajustes_negativos
            }
        },
        "descuentoTotal": total_descuentos,
    }

    return resultado_final



#region Detalle de las ventas consideradas para comisionar en JSON

def detalle_ventas_consideradas_x_sucursal(agencia,campania):
    ventas_qs = Ventas.objects.filter(
        campania=campania,
        agencia=agencia,
        is_commissionable=True,
    )

    ventas_list=[]
    for venta in ventas_qs:
        for contrato in venta.cantidadContratos:
            ventas_list.append(
                {
                    "agencia_id": venta.agencia.id,
                    "agencia": venta.agencia.pseudonimo,
                    "nro_cliente": venta.nro_cliente.nro_cliente,
                    "nombre_cliente": venta.nro_cliente.nombre,
                    "contrato": contrato["nro_contrato"],
                    "nro_cuotas": venta.nro_cuotas,
                    "importe": int(venta.importe / len(venta.cantidadContratos)),
                    "fecha_inscripcion": venta.fecha,
                    "campana": venta.campania,
                    "producto_id":venta.producto.id,
                    "producto": venta.producto.nombre,
                    "tipo_producto": venta.producto.tipo_de_producto,
                    "vendedor_id": venta.vendedor.id,
                    "vendedor": venta.vendedor.nombre,
                    "supervisor_id": venta.supervisor.id,
                    "supervisor": venta.supervisor.nombre,
                }
            )
    return ventas_list


def detalles_ventas_propias(agencia,campania,user):
    ventas = detalle_ventas_consideradas_x_sucursal(agencia,campania)
    ventas_by_user = list(filter(lambda x: x["vendedor_id"] == user.id, ventas))

    return ventas_by_user


def detalles_ventas_x_equipo(agencia,campania,user):
    ventas = detalle_ventas_consideradas_x_sucursal(agencia,campania)
    ventas_by_user = list(filter(lambda x: x["supervisor_id"] == user.id, ventas))

    return ventas_by_user


def detalle_pagos_considerados_x_agencia(agencia,campania):
    from sales.models import PagoCannon

    pagos_qs = (
        PagoCannon.objects
        .filter(
            venta__agencia=agencia,
            venta__is_commissionable=True,
            campana_de_pago=campania,
        )
        .select_related('venta')
    )

    pagos_list=[]
    for pago in pagos_qs:
        for contrato in pago.venta.cantidadContratos:
            pagos_list.append(
                {
                    "agencia_id": pago.venta.agencia.id,
                    "agencia": pago.venta.agencia.pseudonimo,
                    "venta_id": pago.venta.id,
                    "nro_cliente": pago.venta.nro_cliente.nro_cliente,
                    "nombre_cliente": pago.venta.nro_cliente.nombre,
                    "contrato": contrato["nro_contrato"],
                    "fecha_inscripcion_venta": pago.venta.fecha,
                    "fecha_pago": pago.fecha,
                    "nro_cuota": pago.nro_cuota,
                    "campana_pago": pago.campana_de_pago,
                    "monto": int(pago.monto /len(pago.venta.cantidadContratos)),
                    "vendedor_id": pago.venta.vendedor.id,
                    "vendedor": pago.venta.vendedor.nombre,
                    "supervisor_id": pago.venta.supervisor.id,
                    "supervisor": pago.venta.supervisor.nombre,
                    "producto_id":pago.venta.producto.id,
                    "producto": pago.venta.producto.nombre,
                    "tipo_producto": pago.venta.producto.tipo_de_producto,
                }
            )
    return pagos_list


def detalles_pagos_x_region(agencia,campania):
    from elanelsystem.utils import get_sucursales_por_provincias
    sucursales_x_region = get_sucursales_por_provincias(agencia)

    all_pagos = []
    for sucursal in sucursales_x_region:
        sucursalObject = Sucursal.objects.filter(pseudonimo=sucursal).first()
        ventas = detalle_pagos_considerados_x_agencia(sucursalObject,campania)
        all_pagos.extend(ventas)
    return all_pagos


def detalle_cuota_1_adelantadas(agencia,campania,user):
    from sales.models import PagoCannon

    pagos_cuotas1_qs = (
        PagoCannon.objects
        .filter(
            venta__agencia=agencia,
            venta__is_commissionable=True,
            venta__vendedor=user,
            nro_cuota=1,
            campana_de_pago=campania,
        )
        .select_related('venta')
    )

    pagos_cuotas1_list=[]
    for pago in pagos_cuotas1_qs:
        for contrato in pago.venta.cantidadContratos:
            pagos_cuotas1_list.append(
                {
                    "agencia_id": pago.venta.agencia.id,
                    "agencia": pago.venta.agencia.pseudonimo,
                    "venta_id": pago.venta.id,
                    "nro_cliente": pago.venta.nro_cliente.nro_cliente,
                    "nombre_cliente": pago.venta.nro_cliente.nombre,
                    "contrato": contrato["nro_contrato"],
                    "fecha_inscripcion_venta": pago.venta.fecha,
                    "fecha_pago": pago.fecha,
                    "dias_diff": (parse_fecha(pago.fecha) - parse_fecha(pago.venta.fecha)).days,
                    "nro_cuota": pago.nro_cuota,
                    "campana_pago": pago.campana_de_pago,
                    "monto": pago.monto,
                    "vendedor_id": pago.venta.vendedor.id,
                    "vendedor": pago.venta.vendedor.nombre,
                    "supervisor_id": pago.venta.supervisor.id,
                    "supervisor": pago.venta.supervisor.nombre,
                    "producto_id":pago.venta.producto.id,
                    "producto": pago.venta.producto.nombre,
                    "tipo_producto": pago.venta.producto.tipo_de_producto,
                }
            )
    return pagos_cuotas1_list


def detalles_ventas_x_region(agencia,campania):
    from elanelsystem.utils import get_sucursales_por_provincias
    sucursales_x_region = get_sucursales_por_provincias(agencia)

    all_ventas = []
    for sucursal in sucursales_x_region:
        sucursalObject = Sucursal.objects.filter(pseudonimo=sucursal).first()
        ventas = detalle_ventas_consideradas_x_sucursal(sucursalObject,campania)
        all_ventas.extend(ventas)
    return all_ventas


def detalle_cuotas_0(agencia,campania):
    cuotas_por_region = detalles_pagos_x_region(agencia,campania)
    return list(filter(lambda x: x["nro_cuota"] == 0, cuotas_por_region))


def detalles_cuotas_1_a_4(agencia,campania):
    nums_cuotas = [1, 2, 3, 4]
    cuotas_por_region = detalles_pagos_x_region(agencia,campania)
    return list(filter(lambda x: x["nro_cuota"] in nums_cuotas, cuotas_por_region))




#endregion