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

def calcular_cantidad_ventasPropias(ventas):
    """
    Retorna la cantidad de ventas (según chances) propias de un usuario
    en una campaña y agencia dadas.
    (Esto ya es siempre entero, no hace falta math.ceil)
    """

    response ={}
    response["cant_ventas"] = sum([len(v.cantidadContratos) for v in ventas])
    response["detalle"] = [v.nro_operacion for v in ventas]

    return response

def calcular_productividad_ventasPropias(ventas):
    """
    Retorna la 'productividad' total de las ventas propias (sum of venta.importe).
    Aplico math.ceil por si 'importe' fuera flotante.
    """
    productividad_x_suc = sum(venta.importe for venta in ventas)

    return productividad_x_suc

def get_detalle_comision_x_cantidad_ventasPropias(ventas):
    """
    Recorre las ventas y determina la comisión. Aplico math.ceil al final.
    """

    cantVentas2 = sum(len(v.cantidadContratos) for v in ventas)
    coeficienteSelected = 0

    response = {"planes": {}}
    response["planes"]["com_24_30_motos"] = {
        "cantidad_ventas": 0,
        "comision": 0.0,
        "ventas": []
    }
    response["planes"]["com_24_30_prestamo_combo"] = {
        "cantidad_ventas": 0,
        "comision": 0.0,
        "ventas": []
    }
    response["planes"]["com_48_60"] = {
        "cantidad_ventas": 0,
        "comision": 0.0,
        "ventas": []
    }
    
    for venta in ventas:
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
        response["planes"][typePlan]["ventas"].append({
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
        response["planes"][typePlan]["coeficiente_correspondiente"] = coeficienteSelected 
        response["planes"][typePlan]["comision"] += comision_venta
        response["planes"][typePlan]["cantidad_ventas"] += len(venta.cantidadContratos)


    comisionTotal_by_suc = 0
    for keyPlan in response["planes"]:
        # ceil a cada comision de plan
        response["planes"][keyPlan]["comision"] = math.ceil(response["planes"][keyPlan]["comision"])
        comisionTotal_by_suc += response["planes"][keyPlan]["comision"]
    response["comision"] = math.ceil(comisionTotal_by_suc)

    return response

def get_premio_x_productividad_ventasPropias(ventas):
    """
    Devuelve un premio fijo según la productividad. 
    Ojo con la lógica: si las bandas devuelven un entero, no hace falta,
    pero si multiplicas, sí. Ejemplo actual no multiplica, 
    excepto en la parte 'bandas' -> no se hace un * coef, sino un valor fijo.
    Aun así, por seguridad uso math.ceil.
    """

    productividad = sum(v.importe for v in ventas)

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

def get_detalle_cuotas1(usuario, campania, agencia_id=None):
    from sales.models import PagoCannon
    """
    Cuotas 1 pagadas dentro de 15 días -> comision del 10% de la cuota 2.
    Aplico math.ceil a total_comision_x_cuota1.
    """
    from elanelsystem.utils import parse_fecha

     # 1) Traer de golpe SOLO los pagos de cuota 1 que me interesan
    if agencia_id != None:
        pagos_qs = (
            PagoCannon.objects
            .filter(
                venta__vendedor=usuario,
                venta__agencia__id=agencia_id,
                venta__is_commissionable=True,
                nro_cuota=1,
                campana_de_pago=campania,
            )
            .select_related('venta')
        )
    else:
        pagos_qs = (
            PagoCannon.objects
            .filter(
                venta__vendedor=usuario,
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


def comisiones_brutas_vendedor(usuario, campania, ventas):
    """
    Devuelve la comision bruta del vendedor. 
    """
    comision_x_cantidad_ventas = get_detalle_comision_x_cantidad_ventasPropias(ventas)["comision"]
    comision_x_cuotas1 = get_detalle_cuotas1(usuario, campania)["comision_total"]
    comision_x_productividad = get_premio_x_productividad_ventasPropias(ventas)
    
    return {
        "comision_total": math.ceil(comision_x_cantidad_ventas + comision_x_cuotas1 + comision_x_productividad),
        "comision_x_cantidad_ventas": comision_x_cantidad_ventas,
        "comision_x_cuotas1": comision_x_cuotas1,
        "comision_x_productividad": comision_x_productividad       
    }

#endregion

#region Funciones enfocadas a los  supervisores

def calcular_ventas_supervisor(ventas):
    """
    Cantidad de ventas totales del supervisor. (Siempre entero)
    """
    return sum(len(v.cantidadContratos) for v in ventas)  # entero

def calcular_productividad_supervisor(ventas):
    """
    Productividad total (sum of venta.importe). Aplico math.ceil.
    """
    total = sum(v.importe for v in ventas)
    return math.ceil(total)

def get_premio_x_productividad_supervisor(ventas):
    """
    Multiplicamos total_prod * coef. => ahí puede salir decimal => math.ceil
    """
    total_prod = calcular_productividad_supervisor(ventas)
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

def get_premio_x_cantidad_ventas_equipo(ventas):
    """
    Devuelve dineroAsegurado si la suma de ventas > 80, sino 0. 
    No hace falta ceil, pues dineroAsegurado es un entero. 
    Igual, por seguridad, podría hacerse math.ceil.
    """
    asegurado = Asegurado.objects.get(dirigido="Supervisor")
    dineroAsegurado = asegurado.dinero
    cantidad_ventas_x_equipo = calcular_ventas_supervisor(ventas)
    
    if cantidad_ventas_x_equipo > 80:
        return math.ceil(dineroAsegurado)
    return 0

def get_comision_x_cantidad_ventas_equipo(ventas):
    """
    total += venta.importe * coef => decimal => uso ceil en el final.
    """
    cantVentas = sum(len(v.cantidadContratos) for v in ventas)

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
    for venta in ventas:
        total += venta.importe * coef

    return math.ceil(total)

def comisiones_brutas_supervisor(ventas):
    """
    Devuelve la comision bruta del supervisor. 
    """
    comision_x_cantidad_ventas = get_comision_x_cantidad_ventas_equipo(ventas)
    comision_x_productividad = get_premio_x_productividad_supervisor(ventas)
    comision_x_ventas_equipo = get_premio_x_cantidad_ventas_equipo(ventas)

    return {
        "comision_total": math.ceil(comision_x_cantidad_ventas + comision_x_productividad + comision_x_ventas_equipo),
        "comision_x_cantidad_ventas": comision_x_cantidad_ventas,
        "comision_x_productividad": comision_x_productividad,
        "comision_x_ventas_equipo": comision_x_ventas_equipo,
    }
#endregion

#region Funciones enfocadas a los gerentes de sucursal
def get_detalle_cuotas_x2(pagos_sucursal, porcentaje_x_cuota):
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
    pagos_validos = [p for p in pagos_sucursal if p.nro_cuota in cuotas_numeros]

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


def get_premio_x_cantidad_ventas_sucursal2(pagos_0, objetivo_gerente=0):
    # from elanelsystem.utils import get_subAgencias_por_provincia
    
    """
    1000 * cantidad_cuotas_0 si >= objetivo => se multiplica => potencial decimal no,
    pero se hace un int. Por seguridad, math.ceil.
    """
    # objetivo_gerente = 200
    cantidad_cuotas_0 = get_detalle_cuotas_02(pagos_0)["cantidad_cuotas_0"]

    if cantidad_cuotas_0 >= objetivo_gerente:
        return math.ceil(1000 * cantidad_cuotas_0)
    return 0


def get_detalle_sucursales_de_region2(gerente, agencia, campania):
    from sales.models import PagoCannon
    from elanelsystem.utils import get_subAgencias_por_provincia

    # 1) Obtener todos los pagos que es del gerente SEGUN el atributo "venta__gerente" 
    all_pagos_by_gerente = (
        PagoCannon.objects
        .filter(
            Q(venta__gerente=gerente),
            venta__is_commissionable=True,
            nro_cuota__in=[0, 1, 2, 3, 4],
            campana_de_pago=campania
        )
        .select_related("venta", "venta__agencia")
    )


    # 2) Setear las agencias que le corresponden un determinado % (por ej: 8% o 6%) y su premio de por objetivo de ventas
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

    # 3) Diccionario de resultado
    result = {
        "detalleRegion": {},
        "porcetage_x_cuota": 0,
        "cantidad_total_cuotas": 0,
        "dinero_total_cuotas": 0,
        "comision_total_cuotas": 0,
        "dinero_recadudado_cuotas_0": 0,
    }

    # 4) Agrupar pagos por sucursal
    pagos_del_gerente = defaultdict(list)
    for p in all_pagos_by_gerente:
        pagos_del_gerente[p.venta.agencia_id].append(p)

    # 5) Procesar los pagos agrupados por sucursal
    for key, value in pagos_del_gerente.items():
        suc_obj = Sucursal.objects.filter(id=key).first()
        suc_clean = suc_obj.pseudonimo.replace(" ", "").replace(",", "").lower()

        # print(f"\n Sucursal a trabajar -> {suc_clean}")
        porcentage_x_cuota = 0.08 if suc_obj.pseudonimo in agencias_8_porc else 0.06
        premios_por_venta = 0
        # print(f"\n Procentaje seleccionado -> {porcentage_x_cuota}")

        pagos_1_4 = get_detalle_cuotas_x2(value, porcentage_x_cuota)
        pagos_0 = get_detalle_cuotas_02(value)

        if(suc_obj.pseudonimo in agencias_objs_200_ventas):
            premios_por_venta = get_premio_x_cantidad_ventas_sucursal2(value, 200)
        else:
            premios_por_venta = get_premio_x_cantidad_ventas_sucursal2(value, 150)

        result["porcetage_x_cuota"] = porcentage_x_cuota

        result["detalleRegion"][f"{suc_clean}"] = {
            "suc_id": key,
            "suc_name": suc_obj.pseudonimo,
            "suc_info": pagos_1_4 | pagos_0,
            "premios_por_venta": math.ceil(premios_por_venta),
            "sub_total": math.ceil(pagos_1_4["comision_total_cuotas"] + premios_por_venta)
        }


        result["cantidad_total_cuotas"] += math.ceil(pagos_1_4["cantidad_total_cuotas"])
        result["dinero_total_cuotas"] += math.ceil(pagos_1_4["dinero_total_cuotas"])
        result["comision_total_cuotas"] += math.ceil(pagos_1_4["comision_total_cuotas"])
        result["dinero_recadudado_cuotas_0"] += math.ceil(pagos_0["dinero_recaudado_cuotas_0"])
                

    # 6) Luego en caso que corresponda, obtener la cartera de pagos de las subagencias
    subAgencias = get_subAgencias_por_provincia(agencia)
    if subAgencias != []:
        sucursales_region_objs = list(
            Sucursal.objects.filter(pseudonimo__in=subAgencias)
        )
        
        all_pagos_by_subAgencias = (
            PagoCannon.objects
            .filter(
                Q(venta__agencia__in=sucursales_region_objs),
                venta__is_commissionable=True,
                nro_cuota__in=[1, 2, 3, 4],
                campana_de_pago=campania
            )
            .select_related("venta", "venta__agencia")
        )

        pagos_de_subAgencias = defaultdict(list)
        for p in all_pagos_by_subAgencias:
            pagos_de_subAgencias[p.venta.agencia_id].append(p)

        for key, value in pagos_de_subAgencias.items():
            suc_obj = Sucursal.objects.filter(id=key).first()
            suc_clean = suc_obj.pseudonimo.replace(" ", "").replace(",", "").lower()

            porcentage_x_cuota = 0.03
            premios_por_venta = 0

            pagos_1_4 = get_detalle_cuotas_x2(value, porcentage_x_cuota)
            pagos_0 = get_detalle_cuotas_02(value)

            result["porcetage_x_cuota"] = porcentage_x_cuota

            clave_suc = suc_clean
            if clave_suc in result["detalleRegion"]:
                # Si ya existe, sumamos los valores
                result["detalleRegion"][f"{suc_clean}"]["suc_info"] = {**result["detalleRegion"][f"{suc_clean}"]["suc_info"]} | pagos_1_4 | pagos_0
                result["detalleRegion"][f"{suc_clean}"]["comision_total_cuotas"] += math.ceil(pagos_1_4["comision_total_cuotas"])
            else:

                result["detalleRegion"][f"{suc_clean}"] = {
                    "suc_id": key,
                    "suc_name": suc_obj.pseudonimo,
                    "suc_info": pagos_1_4 | pagos_0,
                    "premios_por_venta": 0,
                    "sub_total": math.ceil(pagos_1_4["comision_total_cuotas"] + 0)
                }


                result["cantidad_total_cuotas"] += math.ceil(pagos_1_4["cantidad_total_cuotas"])
                result["dinero_total_cuotas"] += math.ceil(pagos_1_4["dinero_total_cuotas"])
                result["comision_total_cuotas"] += math.ceil(pagos_1_4["comision_total_cuotas"])
                result["dinero_recadudado_cuotas_0"] += math.ceil(pagos_0["dinero_recaudado_cuotas_0"])

    return result


def comisiones_brutas_gerente(gerente, agencia,campania):
    """
    Devuelve la comision bruta del gerente.
    """
    detalle_region = get_detalle_sucursales_de_region2(gerente, agencia, campania)

    
    total_premios = 0
    for r in detalle_region["detalleRegion"].values():
        total_premios += r["premios_por_venta"]

    return {
        "comision_total": math.ceil(detalle_region["comision_total_cuotas"]) + math.ceil(total_premios),
        "comision_total_cuotas": detalle_region["comision_total_cuotas"],
        "total_premios": total_premios
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

    # print(f"Dias trabajados {dias_trabajados_campania}")
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

def detalle_liquidado_ventasPropias(usuario, campania):
    """
    Al final sumas la subcomisión. Ya viene redondeada de get_detalle_comision_x_cantidad_ventasPropias
    y get_detalle_cuotas1. 
    Podrías forzar un math.ceil en 'subtotal'.
    """
    ventas_qs = Ventas.objects.filter(vendedor= usuario, campania=campania, is_commissionable=True)
    comisiones_brutas_dict = comisiones_brutas_vendedor(usuario, campania, ventas_qs)
    if(usuario.nombre == "Silva Joaquin Emanuel"):
        print(comisiones_brutas_dict)
        
    response ={
        **comisiones_brutas_dict,
        "cant_ventas_total":0,
        "productividad_x_ventas_propias_total": 0,
        "cantidad_cuotas_1_total":0,
        "cant_ventas_com_24_30_motos": 0,
        "comisiones_com_24_30_motos": 0,
        "cant_ventas_com_24_30_prestamo_combo": 0,
        "comisiones_com_24_30_prestamo_combo": 0,
        "cant_ventas_com_48_60": 0,
        "comisiones_com_48_60": 0,
        "detalle": {}    
    }

    ventas_x_suc = defaultdict(list)
    for v in ventas_qs:
        ventas_x_suc[v.agencia.id].append(v)

    for suc, ventas in ventas_x_suc.items():
        suc_obj = Sucursal.objects.filter(id=suc).first()
        suc_clean = suc_obj.pseudonimo.replace(" ", "").replace(",", "").lower()
        # 1) Calcular cantidad de ventas propias
        cantidad_ventas = calcular_cantidad_ventasPropias(ventas)["cant_ventas"]

        # 2) Calcular productividad por ventas propias
        productividad_x_ventas_propias = calcular_productividad_ventasPropias(ventas)

        premio_x_productividad = get_premio_x_productividad_ventasPropias(ventas)

        # 3) Obtener detalle de comisiones por cantidad de ventas propias
        dict_comision_cant_ventas = get_detalle_comision_x_cantidad_ventasPropias(ventas)
        detalle_ventas_propias = dict_comision_cant_ventas["planes"]
        # coeficienteSelected = dict_comision_cant_ventas["coeficienteSelected"]

        # 4) Obtener detalle de cuotas 1
        dict_cuotas1 = get_detalle_cuotas1(usuario, campania, suc)
        cantidad_cuotas1 = dict_cuotas1["cantidadCuotas1"]
        detalle_cuotas1 = dict_cuotas1["detalle"]

        # 5) Sumar resultados al response
        response["cant_ventas_total"] += cantidad_ventas
        response["productividad_x_ventas_propias_total"] += productividad_x_ventas_propias
        response["cantidad_cuotas_1_total"] += cantidad_cuotas1
        response["cant_ventas_com_24_30_motos"] += detalle_ventas_propias["com_24_30_motos"]["cantidad_ventas"]
        response["comisiones_com_24_30_motos"] += detalle_ventas_propias["com_24_30_motos"]["comision"]
        response["cant_ventas_com_24_30_prestamo_combo"] += detalle_ventas_propias["com_24_30_prestamo_combo"]["cantidad_ventas"]
        response["comisiones_com_24_30_prestamo_combo"] += detalle_ventas_propias["com_24_30_prestamo_combo"]["comision"]
        response["cant_ventas_com_48_60"] += detalle_ventas_propias["com_48_60"]["cantidad_ventas"]
        response["comisiones_com_48_60"] += detalle_ventas_propias["com_48_60"]["comision"]


        response["detalle"][suc_clean] = {
            "suc_name": suc_obj.pseudonimo,
            "cantidadVentas": cantidad_ventas,
            "productividadXVentasPropias": productividad_x_ventas_propias,
            "cantidadCuotas1": cantidad_cuotas1,
            "comision_x_productividad": premio_x_productividad,
            "comision_x_cuotas1": dict_cuotas1["comision_total"],
            "comision_subTotal": dict_comision_cant_ventas["comision"],
            "detalle": {
                "detalleVentasPropias": detalle_ventas_propias,
                "detalleCuotas1": detalle_cuotas1
            }
        }

    return response

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

def detalle_liquidado_x_rol(usuario, campania, suc):

    snapshot_usuario_by_campania = snapshot_usuario_by_campana(usuario, campania)
    rango_lower = snapshot_usuario_by_campania[0].rango.lower()
    # print(f"\n\nRango de {usuario.nombre} -> {rango_lower}")
    if rango_lower == "supervisor":
        ventas_qs = Ventas.objects.filter(supervisor= usuario, campania=campania, is_commissionable=True)
        comisiones_brutas_dict = comisiones_brutas_supervisor(ventas_qs)
        
        ventas_x_suc = defaultdict(list)
        for v in ventas_qs:
            ventas_x_suc[v.agencia.id].append(v)
        
        response = {
            **comisiones_brutas_dict,
            "cantidadVentasXEquipo_total": 0,
            "productividad_x_equipo_total": 0,
            "detalle" : {}
        }

        for ag, ventas in ventas_x_suc.items():
            suc_obj = Sucursal.objects.filter(id=ag).first()
            suc_clean = suc_obj.pseudonimo.replace(" ", "").replace(",", "").lower()

            cantidad_ventas_x_equipo = calcular_ventas_supervisor(ventas)
            productividad_x_equipo = calcular_productividad_supervisor(ventas)
            comisiones_brutas_dict_x_sucursal = comisiones_brutas_supervisor(ventas)

            # 5) Sumar resultados al response
            response["cantidadVentasXEquipo_total"] += cantidad_ventas_x_equipo
            response["productividad_x_equipo_total"] += productividad_x_equipo
            response["detalle"][suc_clean] = {
                "suc_name": suc_obj.pseudonimo,
                **comisiones_brutas_dict_x_sucursal,
                "cantidad_ventas_x_equipo": cantidad_ventas_x_equipo,
                "productividad_x_equipo": productividad_x_equipo,
            }


        return response

    elif rango_lower == "gerente sucursal":
        detalleRegion = get_detalle_sucursales_de_region2(usuario, suc, campania)

        comisiones_brutas_dict = comisiones_brutas_gerente(usuario, suc, campania)

        response = {
            **comisiones_brutas_dict,
            "cantidad_total_cuotas": detalleRegion["cantidad_total_cuotas"],
            "dinero_total_cuotas": detalleRegion["dinero_total_cuotas"],
            "dinero_recadudado_cuotas_0": detalleRegion["dinero_recadudado_cuotas_0"],
            "detalle" : detalleRegion["detalleRegion"] 
        }

        return response

    else:
        return {
            "comision_total": 0,
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
    ventas_propias_dict = detalle_liquidado_ventasPropias(usuario, campania)
    comision_bruta_vendedor = ventas_propias_dict["comision_total"]
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
        comision_bruta_inicial = comision_bruta_vendedor
    elif rango_lower == "supervisor":
        comision_bruta_inicial = rol_dict["comision_total"]
    elif rango_lower == "gerente sucursal":
        suc_clean = agencia.pseudonimo.replace(" ", "").replace(",", "").lower()
        comision_bruta_inicial = rol_dict["detalle"][suc_clean]["sub_total"]

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
        if rango_lower == "gerente sucursal":
            comision_bruta_final = rol_dict["comision_total"] + diferencia_asegurado

    else:
        comision_bruta_final = comision_bruta_inicial

    # 6) Ajustes y descuentos
    ajustes_positivos = sum(a["dinero"] for a in ajustes_usuario if a["ajuste_tipo"] == "positivo")
    ajustes_negativos = sum(a["dinero"] for a in ajustes_usuario if a["ajuste_tipo"] == "negativo")

    total_descuentos += ajustes_negativos
    comision_bruta_final += ajustes_positivos

    # Si no es vendedor, sumamos comisiones de ventas propias nuevamente (+ premios) 
    if rango_lower != "vendedor":
        comision_bruta_final += comision_bruta_vendedor

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


def factory_pagos(pagos):
    pagos_list=[]
    for pago in pagos:
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


def detalle_pagos_x_gerente(gerente,campania):
    from sales.models import PagoCannon

    all_pagos_by_gerente = (
        PagoCannon.objects
        .filter(
            Q(venta__gerente=gerente),
            venta__is_commissionable=True,
            nro_cuota__in=[0, 1, 2, 3, 4],
            campana_de_pago=campania
        )
        .select_related("venta", "venta__agencia")
    )
    pagos = factory_pagos(all_pagos_by_gerente)
    return pagos


def detalles_pagos_x_region(agencia,campania):
    from elanelsystem.utils import get_subAgencias_por_provincia
    from sales.models import PagoCannon

    pagos = []
    subAgencias = get_subAgencias_por_provincia(agencia)
    if subAgencias != []:
        sucursales_region_objs = list(
            Sucursal.objects.filter(pseudonimo__in=subAgencias)
        )
        
        all_pagos_by_subAgencias = (
            PagoCannon.objects
            .filter(
                Q(venta__agencia__in=sucursales_region_objs),
                venta__is_commissionable=True,
                nro_cuota__in=[1, 2, 3, 4],
                campana_de_pago=campania
            )
            .select_related("venta", "venta__agencia")
        )

        ventas = factory_pagos(all_pagos_by_subAgencias)
        pagos.extend(ventas)

    return pagos


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
    from elanelsystem.utils import get_subAgencias_por_provincia
    sucursales_x_region = get_subAgencias_por_provincia(agencia)

    all_ventas = []
    for sucursal in sucursales_x_region:
        sucursalObject = Sucursal.objects.filter(pseudonimo=sucursal).first()
        ventas = detalle_ventas_consideradas_x_sucursal(sucursalObject,campania)
        all_ventas.extend(ventas)
    return all_ventas


def detalle_cuotas_0(gerente,campania):
    cuotas_por_region = detalle_pagos_x_gerente(gerente,campania)
    return list(filter(lambda x: x["nro_cuota"] == 0, cuotas_por_region))


def detalles_cuotas_1_a_4(agencia,campania,gerente):
    nums_cuotas = [1, 2, 3, 4]
    all_cuotas = []
    cuotas_por_region = detalles_pagos_x_region(agencia,campania)
    cuotas_por_gerente = detalle_pagos_x_gerente(gerente,campania)
    all_cuotas = cuotas_por_region + cuotas_por_gerente
    return list(filter(lambda x: x["nro_cuota"] in nums_cuotas, all_cuotas))




#endregion