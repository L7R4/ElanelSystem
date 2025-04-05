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
    return sum(venta.total_a_pagar for venta in ventas_auditadas)

def get_detalle_comision_x_cantidad_ventasPropias(usuario,campania,agencia):

    """
    Calcula la comisión total de las ventas del usuario, 
    diferenciando planes 48/60, 24/30 motos y 24/30 electro/solucion (?)
    Retorna un dict con:
      {
        planes: {
          "com_48_60": {cantidad_ventas, comision, [...ventas]},
          "com_24_30_motos": {...},
          "com_24_30_elec_soluc": {...}
        },
        comisionTotal: Y
      }
    """

    typePlanes = ["com_48_60","com_24_30_motos","com_24_30_elec_soluc"]
    detalleDict = {"planes":{}}
    comisionTotal = 0
    ventas_qs = ""
    
    for typePlan in typePlanes:
        if typePlan == "com_48_60":
            ventas_qs = Ventas.objects.filter(
                vendedor=usuario,
                campania=campania,
                agencia=agencia,
                nro_cuotas__in=[48, 60],
                adjudicado__status=False,
                deBaja__status=False
            )
        elif typePlan == "com_24_30_motos":
            ventas_qs = Ventas.objects.filter(
                vendedor=usuario,
                campania=campania,
                agencia=agencia,
                nro_cuotas__in=[24, 30],
                producto__tipo_de_producto="Moto",
                adjudicado__status=False,
                deBaja__status=False
            )
        else:  # com_24_30_elec_soluc
            ventas_qs = Ventas.objects.filter(
                vendedor=usuario,
                campania=campania,
                agencia=agencia,
                nro_cuotas__in=[24, 30],
                producto__tipo_de_producto__in=["Prestamo", "Electrodomestico"],
                adjudicado__status=False,
                deBaja__status=False
            )

        ventas_auditadas = [
            v for v in ventas_qs
            if v.auditoria and len(v.auditoria) > 0 and v.auditoria[-1].get("grade") is True
        ]
        cantVentas = sum(len(v.cantidadContratos) for v in ventas_auditadas)

        # Bandas de comision
        bandas = [
            (0, 9, 0.0135),
            (9, 20, 0.0140),
            (20, 30, 0.0145),
            (30, float("inf"), 0.0155),
        ]
        coeficienteSelected = 0
        for low, high, coef in bandas:
            if low <= cantVentas < high:
                coeficienteSelected = coef
                break

        # Calcula la comision total
        comision = 0
        for venta in ventas_auditadas:
            comision += venta.importe * coeficienteSelected
        
        # Se arma la sub-seccion
        detalleDict["planes"][typePlan] = {
            "cantidad_ventas": cantVentas,
            "comision": comision,
            "ventas": [{
                "pk": v.pk,
                "importe": v.importe,
                "nro_cuotas": v.nro_cuotas,
                "producto": v.producto.nombre,
                "fecha": v.fecha,
                "cantidadContratos": v.cantidadContratos,
                "nro_operacion": v.nro_operacion,
                "nro_cliente": v.nro_cliente.nro_cliente,
                "nombre_cliente": v.nro_cliente.nombre
            } for v in ventas_auditadas]
        }

        comisionTotal += comision 

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
        campania=campania,
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

    for venta in ventas_auditadas:
        # Chequear si la cuota 1 está pagada
        if venta.cuotas[1]["status"] == "Pagado":
            fechaPagoC1 = parse_fecha(venta.cuotas[1]["pagos"][0]["fecha"])
            fechaAltaVenta = parse_fecha(venta.fecha)
            dias_dif = (fechaPagoC1 - fechaAltaVenta).days
            if dias_dif <= 15:
                cuotas1Adelantadas.append(venta.cuotas[1])
                # sumamos 10% de la cuota 2
                total_comision_x_cuota1 += venta.cuotas[2]["total"] * 0.10

    return {
        "comision_total": total_comision_x_cuota1,
        "detalle": cuotas1Adelantadas,
        "cantidadCuotas1": len(cuotas1Adelantadas)
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
    return sum(v.total_a_pagar for v in ventas_filtradas)


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

#endregion
def detalle_liquidado_ventasPropias(usuario,campania,agencia):
    cantidad_ventas = calcular_cantidad_ventasPropias(usuario,campania,agencia)
    productividad_x_ventas_propias = calcular_productividad_ventasPropias(usuario,campania,agencia)
    comision_x_cantidad_ventas_propias = get_detalle_comision_x_cantidad_ventasPropias(usuario,campania,agencia)["comision"] # Sumar
    detalle_ventas_propias = get_detalle_comision_x_cantidad_ventasPropias(usuario,campania,agencia)["planes"]
    comision_x_cuotas1 = get_detalle_cuotas1(usuario,campania,agencia)["comision_total"] # Sumar
    cantidad_cuotas1 = get_detalle_cuotas1(usuario,campania,agencia)["cantidadCuotas1"] 
    detalle_cuotas1 = get_detalle_cuotas1(usuario,campania,agencia)["detalle"]

    return{
        "comision_subtotal": comision_x_cantidad_ventas_propias + comision_x_cuotas1,
        "detalle":{
            "cantidadVentas": cantidad_ventas,
            "productividadXVentasPropias": productividad_x_ventas_propias,
            "comisionXCantidadVentasPropias": comision_x_cantidad_ventas_propias,
            "detalleVentasPropias": detalle_ventas_propias,
            "comisionXCuotas1": comision_x_cuotas1,
            "cantidadCuotas1": cantidad_cuotas1,
            "detalleCuotas1": detalle_cuotas1
        }
    }


def detalle_descuestos(usuario,campania,agencia):
    pass


def detalle_premios_x_objetivo(usuario,campania,agencia):
    premio_subtotal = 0
    detalle = {}

    premio_x_productividad_ventas_propias = get_premio_x_productividad_ventasPropias(usuario,campania,agencia) # Sumar
    
    if (str(usuario.rango).lower() == "supervisor"):
        premio_x_cantidad_ventas = get_premio_x_cantidad_ventas_equipo(usuario,campania,agencia)
        premio_x_productividad_ventas = get_premio_x_productividad_supervisor(usuario,campania,agencia)

        detalle = {
            "premio_x_cantidad_ventas_equipo": premio_x_cantidad_ventas,
            "premio_x_productividad_ventas_equipo":premio_x_productividad_ventas
        }

        premio_subtotal += premio_x_cantidad_ventas + premio_x_productividad_ventas
        
    elif (str(usuario.rango).lower() == "gerente de sucursal"):
        pass
    pass

def detalle_liquidado_x_rol(usuario,campania,agencia, porcentage_x_cuota_gerente=0):
    if(str(usuario.rango).lower() == "supervisor"):
        cantidad_ventas_x_equipo = calcular_ventas_supervisor(usuario,campania,agencia)
        productividad_x_equipo = calcular_productividad_supervisor(usuario,campania,agencia)
        comision_x_cantidad_ventas_equipo = get_comision_x_cantidad_ventas_equipo(usuario,campania,agencia)["comision"] # Sumar
        detalle_ventas_equipo = detalle_de_equipo_x_supervisor(usuario,campania,agencia)["planes"]

        return{
            "comision_subtotal": comision_x_cantidad_ventas_equipo,
            "detalle":{
                "cantidadVentasXEquipo": cantidad_ventas_x_equipo,
                "productividadXVentasEquipo": productividad_x_equipo,
                "detalleVentasXEquipo": detalle_ventas_equipo,
            }
        }
    elif(str(usuario.rango).lower() == "gerente de sucursal"):
        cantidad_total_de_cuotas = get_detalle_cuotas_x(campania, agencia, porcentage_x_cuota_gerente)["cantidad_total_cuotas"]
        dinero_total_recaudado_cuotas = get_detalle_cuotas_x(campania, agencia, porcentage_x_cuota_gerente)["dinero_total_cuotas"]
        comision_x_cuotas = get_detalle_cuotas_x(campania, agencia, porcentage_x_cuota_gerente)["comision_total_cuotas"]
        detalle_x_cuotas = get_detalle_cuotas_x(campania, agencia, porcentage_x_cuota_gerente)["detalleCuota"]
        
        return{
            "comision_subtotal": comision_x_cuotas,
            "detalle":{
                "cantidad_cuotas_1_4": cantidad_total_de_cuotas,
                "dinero_recaudado_cuotas": dinero_total_recaudado_cuotas,
                "detalle_x_cuotas": detalle_x_cuotas,
            }
        }






#--------------------------------------------------------------------------------------------------------------------------------
def calcularAseguradoSegunDiasTrabajados(dinero,fecha_ingreso):
    # Obtener la fecha actual
    fecha_actual = datetime.now()

    # Obtener el último día del mes actual
    ultimo_dia_mes = datetime(fecha_actual.year, fecha_actual.month, 1) + timedelta(days=32)
    ultimo_dia_mes = ultimo_dia_mes.replace(day=1) - timedelta(days=1)

    
    # Inicializar contador de días hábiles
    dias_habiles = 0

    # Recorrer cada día entre la fecha de ingreso y el último día del mes
    fecha_iter = datetime.strptime(fecha_ingreso, '%d/%m/%Y')
    while fecha_iter <= ultimo_dia_mes:
        # Si el día de la semana no es domingo, aumentar contador de días hábiles
        if fecha_iter.weekday() != 6:  # El código 6 corresponde al domingo
            dias_habiles += 1
        fecha_iter += timedelta(days=1)



    dinero_a_pagar = 0
    if(dias_habiles < ultimo_dia_mes.day):
        # Calcular el dinero correspondiente por día
        dinero_por_dia = dinero / ultimo_dia_mes.day 

        # Calcular el monto a pagar al trabajador
        dinero_a_pagar = dinero_por_dia * dias_habiles

    elif(dias_habiles >= ultimo_dia_mes.day):
        dinero_a_pagar = dinero

    return dinero_a_pagar

def getAsegurado(usuario,comisiones):
    dineroAsegurado = 0
    if(usuario.rango.lower() in "vendedor"):
        asegurado = Asegurado.objects.get(dirigido="Vendedor")
        dineroAsegurado = asegurado.dinero
        # Si las comisiones son menores que el dinero asegurado, se cobra el asegurado
        if comisiones < dineroAsegurado:
            return dineroAsegurado
        return 0
    
    if(usuario.rango.lower() in "supervisor"):
        asegurado = Asegurado.objects.get(dirigido="Supervisor")
        dineroAsegurado = asegurado.dinero

        if comisiones < dineroAsegurado:
            return dineroAsegurado
        return 0


    return calcularAseguradoSegunDiasTrabajados(dineroAsegurado,usuario.fec_ingreso)

def getDetalleComisionPorCantVentasPropias(usuario,campania,agencia):
    typePlanes = ["com_48_60","com_24_30_motos","com_24_30_elec_soluc"]
    detalleDict = {"planes":{}}
    cantVentasTotal = 0
    comisionTotal = 0
    ventas = ""
    
    for typePlan in typePlanes:
        if(typePlan =="com_48_60"):
            ventas = Ventas.objects.filter(vendedor=usuario, campania=campania, agencia=agencia ,nro_cuotas__in=[48, 60], adjudicado__status=False, deBaja__status=False)
        elif (typePlan =="com_24_30_motos"):
            ventas = Ventas.objects.filter(vendedor=usuario, campania=campania, agencia=agencia ,nro_cuotas__in=[24, 30] , producto__tipo_de_producto="Moto", adjudicado__status=False, deBaja__status=False)
        elif (typePlan =="com_24_30_elec_soluc"):
            ventas = Ventas.objects.filter(vendedor=usuario, campania=campania, agencia=agencia ,nro_cuotas__in=[24, 30] , producto__tipo_de_producto__in=["Prestamo","Electrodomestico"], adjudicado__status=False, deBaja__status=False)
        
        ventas = [
            venta for venta in ventas
            if len(venta.auditoria) > 0 and venta.auditoria[-1].get("grade") is True
        ]
        cantVentas = len(ventas)

        comision = 0
        bandas = [
            (0, 9, 0.0135),
            (9,20, 0.0140),
            (20, 30, 0.0145),
            (30, float("inf"), 0.0155),
        ]
        coeficienteSelected = 0
        for low, high, coeficiente in bandas:
            if low <= cantVentas < high:
                coeficienteSelected = coeficiente
                break

    
        for venta in ventas:
            # Calcular la comisión por venta y sumarla al total
            comision_por_venta = (venta.importe * coeficienteSelected)
            comision += comision_por_venta
        
        detalleDict["planes"][typePlan] = {
            "cantidad_ventas": cantVentas, 
            "comision": comision, 
            "ventas": [
                {"pk":venta.pk, 
                 "importe":venta.importe,
                 "nro_cuotas":venta.nro_cuotas,
                 "producto":venta.producto.nombre,
                 "fecha":venta.fecha,
                 "cantidadContratos":venta.cantidadContratos,
                 "nro_operacion":venta.nro_operacion,
                 "nro_cliente":venta.nro_cliente.nro_cliente,
                 "nombre_cliente":venta.nro_cliente.nombre} 
                for venta in ventas
                ]}

        cantVentasTotal += cantVentas 
        comisionTotal += comision 

    detalleDict["cantVentasTotalPropias"] = cantVentasTotal
    detalleDict["comisionTotal"] = comisionTotal
    return detalleDict

def getPremioProductividadVentasPropias(usuario,campania,agencia):
    # Consulta para obtener las ventas del vendedor en la campaña

    ventas = Ventas.objects.filter(vendedor=usuario, campania=campania,agencia=agencia, adjudicado__status=False, deBaja__status=False)
    ventas = [
        venta for venta in ventas
        if len(venta.auditoria) > 0 and venta.auditoria[-1].get("grade") is True
    ]

    # Sumar los importes de los productos asociados a cada ventacom_CantVentas_total
    productividad = sum(venta.importe for venta in ventas)
    premio = 0
    
    # Lista de tuplas: (limite_inferior, limite_superior, premio)
    bandas = [
        (0,        6000000, 0),
        (6000000,  8000000, 10000),
        (8000000, 10000000, 15000),
        (10000000, float("inf"), 20000),
    ]
    for low, high, dinero in bandas:
        if low <= productividad < high:
            premio = dinero
            break
    print("Premio seleccionado -> " + str(premio) )
    return premio

def getAusenciasTardanzas(usuario, campania):
        if(usuario.faltas_tardanzas == []):
            return {"total_descuentos": 0, 
                    "detalle":
                        {"faltas":{"cantidad":0,"dinero":0},
                         "tardanzas":{"cantidad":0,"dinero":0}
                        }
                    }
        else:
            ausencias_tardanzas = [item for item in usuario.faltas_tardanzas if item["campania"] == campania]
            faltas = [item for item in ausencias_tardanzas if item["tipoEvento"] == "Falta"]
            tardanzas = [item for item in ausencias_tardanzas if item["tipoEvento"] == "Tardanza"]

            montoPorFalta = MontoTardanzaAusencia.objects.first().monto_ausencia
            montoPorTardanza = MontoTardanzaAusencia.objects.first().monto_tardanza

            total_descuentos = (montoPorTardanza*len(tardanzas))+(montoPorFalta*len(faltas))
           
            return {"total_descuentos": int(total_descuentos), 
                    "detalle": 
                        {"faltas":{"cantidad":len(faltas),"dinero":int(montoPorFalta*len(faltas))},
                         "tardanzas":{"cantidad":len(tardanzas),"dinero":int(montoPorTardanza*len(tardanzas))}
                        } 
                    }

def getAdelantos(usuario,campania):
    descuentosDeCampaña = [descuento for descuento in usuario.descuentos if descuento["campania"] == campania]

    dineroTotal = sum([int(item["dinero"]) for item in descuentosDeCampaña])

    return {'dineroTotal': dineroTotal, 'detalle': descuentosDeCampaña}

def getCuotas1(usuario,campania,agencia):
        totalDineroCuotas1 = 0
        cuotas1Adelantadas = []
        ventas = Ventas.objects.filter(vendedor=usuario, campania=campania,agencia=agencia, adjudicado__status=False, deBaja__status=False)
        ventas = [
            venta for venta in ventas
            if len(venta.auditoria) > 0 and venta.auditoria[-1].get("grade") is True
        ]
        for v in ventas:
            if(v.cuotas[1]["status"] == "Pagado"):
               fechaCuota = parse_fecha(v.cuotas[1]["pagos"][0]["fecha"])
               fechaAltaVenta = parse_fecha(v.fecha)

               if((fechaCuota-fechaAltaVenta).days <= 15):
                    cuotas1Adelantadas.append(v.cuotas[1])
                    totalDineroCuotas1 += v.cuotas[2]["total"] * 0.10
                    
        return {"totalDinero": totalDineroCuotas1,"detalle":cuotas1Adelantadas, "cantidadCuotas1": len(cuotas1Adelantadas)}

def setPremiosPorObjetivo(usuario,campania,agencia,comisiones=0,cantVentas=0):
    premios = list(usuario.premios)
    if(usuario.rango.lower() in "vendedor"):
        pass

    if(usuario.rango.lower() in "supervisor"):
        asegurado = Asegurado.objects.get(dirigido="Supervisor")
        dineroAsegurado = asegurado.dinero
         # Si la suma de ventas del equipo supera 80, se le suma el asegurado como premio
        if cantVentas > 80:
            oldPremiosPorCantVentas = list(filter(lambda x: x["concepto"].lower() == "premio por cantidad de ventas" and x["campania"] == campania, premios))
            if(len(oldPremiosPorCantVentas) != 0):
                premio = {"metodoPago": "---", 
                        "dinero": f"{dineroAsegurado}", 
                        "agencia": f"{agencia.id}", 
                        "campania": f"{campania}", 
                        "fecha": f"{datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                        "concepto": "Premio: por cantidad de ventas"
                        }
            
                premios.append(premio)
            else:
                pass

    # return monto

def getPremiosPorObjetivo(usuario, campania):
    listaPosiblesPremios = ["premio por cantidad de ventas", "premio por productividad de ventas"]
    premios = list(usuario.premios)
    premios = list(filter(lambda x: x["concepto"].lower() in listaPosiblesPremios and x["campania"] == campania, premios))

    premiosDinero = list(map(lambda x: int(x["dinero"]), premios))

    return {"premiosList": premios,"totalPremios": sum(premiosDinero)}

#region Funciones especificas del supervisor - - - - - - - -   
 
def calcular_ventas_supervisor(usuario,campania,agencia):
    # Consulta para obtener la cantidad total de ventas del vendedor en la campaña
    ventas_totales = Ventas.objects.filter(supervisor=usuario, campania=campania,agencia=agencia, adjudicado__status=False, deBaja__status=False)
    ventas_totales = [
        venta for venta in ventas_totales
        if len(venta.auditoria) > 0 and venta.auditoria[-1].get("grade") is True
    ]
    ventas_segun_chances = [len(venta.cantidadContratos) for venta in ventas_totales]
    ventas_segun_chances = sum(ventas_segun_chances)
    # print(f"Cantidad de ventas del supervisor {usuario.nombre} de la agencia {agencia.pseudonimo} en la {campania} \n\n {ventas_segun_chances}")
    
    return ventas_segun_chances

def calcular_productividad_supervisor(usuario,campania,agencia):
    # Consulta para obtener las ventas del vendedor en la campaña
    ventas = Ventas.objects.filter(
        supervisor=usuario, 
        campania=campania,
        agencia=agencia, 
        adjudicado__status=False, 
        deBaja__status=False
        )
    
    ventas = [
        venta for venta in ventas
        if len(venta.auditoria) > 0 and venta.auditoria[-1].get("grade") is True
    ]

    # Sumar los importes de los productos asociados a cada venta
    suma_importes = sum(venta.total_a_pagar for venta in ventas)
    return suma_importes

def getPremioxProductividad_supervisor(usuario,campania,agencia):
    totalProductividad = calcular_productividad_supervisor(usuario,campania,agencia)
    premio = 0
    bandas = [
        (0, 16000000, 0),
        (16000000, 18000000, 0.00020),
        (18000000, 22000000, 0.00030),
        (22000000, 26000000, 0.00050),
        (26000000, 30000000, 0.00075),
        (30000000, float("inf"), 0.001),
    ]
    for low, high, coeficiente in bandas:
        if low <= totalProductividad < high:
            premio = totalProductividad * coeficiente
            break

    return premio

def getComisionCantVentas_supervisor(usuario,campania,agencia):
    ventas = Ventas.objects.filter(supervisor=usuario, campania=campania,agencia=agencia, adjudicado__status=False, deBaja__status=False)
    ventas = [
        venta for venta in ventas
        if len(venta.auditoria) > 0 and venta.auditoria[-1].get("grade") is True
    ]

    cantVentas = len(ventas)
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
    coeficienteSelected = 0
    for low, high, coeficiente in bandas:
        if low <= cantVentas < high:
            coeficienteSelected = coeficiente
            break
    
    total_comisionado = 0
    # Iterar sobre las ventas y calcular la comisión total
    for venta in ventas:
        # Calcular la comisión por venta y sumarla al total
        comision_por_venta = venta.importe * coeficienteSelected
        total_comisionado += comision_por_venta
    return total_comisionado

def desempenioEquipo_supervisor(usuario,campania,agencia):
    listaVendedores = []
    ventas = Ventas.objects.filter(supervisor=usuario, campania=campania,agencia=agencia, adjudicado__status=False, deBaja__status=False)
    ventas = [
        venta for venta in ventas
        if len(venta.auditoria) > 0 and venta.auditoria[-1].get("grade") is True
    ]
    for venta in ventas:
        vendedor = venta.vendedor
        desempenioVendedor = {"nombre": vendedor.nombre,"cantidad_ventas": calcular_cantidad_ventasPropias(vendedor,campania,agencia), "productividad":calcular_productividad_ventasPropias(vendedor,campania,agencia)}
        listaVendedores.append(desempenioVendedor)

    return listaVendedores

#endregion - - - - - - - - - - - - - - - - - - -

#region Funcionsaes especificas del gerente de sucursal - - - - - - - - - -

def getCuotasX(campania,agencia):
    cuotasToFilter = ['1','2','3','4']
    cuotasDict = {}
    
    cantidadTotalCuotas = 0
    dineroTotalCuotas = 0
    comisionTotalCuotas = 0
    ventas = Ventas.objects.filter(agencia=agencia,campania=campania, adjudicado__status=False, deBaja__status=False)
    ventas = [
        venta for venta in ventas
        if len(venta.auditoria) > 0 and venta.auditoria[-1].get("grade") is True
    ]
    # print()

    # Cuota de inscripcion
    cantCuotas0 = 0
    dineroTotal_Cuota0 = 0
    # objetivo = Asegurado.objects.get(dirigido ="Gerente sucursal").objetivo
    dinero = Asegurado.objects.get(dirigido ="Gerente sucursal").dinero
    for v in ventas:
        if(v.cuotas[0]["status"] == "Pagado"):
            cantCuotas0 += 1
            dineroTotal_Cuota0 += v.cuotas[0]["total"]
    comisionTotal_x_Cuota0 = dinero * cantCuotas0 if cantCuotas0 >= 300 else 0
    cantidadTotalCuotas += cantCuotas0
    dineroTotalCuotas += dineroTotal_Cuota0
    comisionTotalCuotas += comisionTotal_x_Cuota0
    cuotasDict["detalleCuota"] = {}
    cuotasDict["detalleCuota"]["cuotas0"] = {"cantCuotas": cantCuotas0,"dineroTotal":dineroTotal_Cuota0,"dineroComisionado":comisionTotal_x_Cuota0}

    # Otras cuotas
    for number in cuotasToFilter:
        cantCuotasX = 0
        dineroTotal_CuotaX = 0
        for v in ventas:
            if(v.cuotas[int(number)]["status"] == "Pagado"):
                cantCuotasX += 1
                dineroTotal_CuotaX += v.cuotas[int(number)]["total"]

        comisionTotal_x_CuotaX = dineroTotal_CuotaX * 0.08
        cantidadTotalCuotas += cantCuotasX
        dineroTotalCuotas += dineroTotal_CuotaX
        comisionTotalCuotas += comisionTotal_x_CuotaX

        cuotasDict["detalleCuota"][f"cuotas{number}"] = {"cantidad": cantCuotasX, "dineroTotal": dineroTotal_CuotaX,"dineroComisionado":comisionTotal_x_CuotaX}

    cuotasDict["cantidadTotal_Cuotas"] = cantidadTotalCuotas
    cuotasDict["dineroTotal_Cuotas"] = dineroTotalCuotas
    cuotasDict["comisionTotal_Cuotas"] = comisionTotalCuotas
    return cuotasDict
    
#endregion - - - - - - - - - - - - - - - - - - -


def getComisionTotal(usuario,campania,agencia): 
    desempenioDeColaborador = {}
    detailDesempenioDict = {}

    print(f"""- - - - - - - - - - - - - -
          Detalle de liquidacion de colaborador: {usuario.nombre}, en la campaña {campania} y en la agencia {agencia.pseudonimo} 
          - - - - - - - - - - - - - -""")
    
    #region SECCION DE VENTAS PROPIAS

    # 1 - Obtiene la cantidad (total resumido) de ventas  propias
    desempenioDeColaborador["cant_ventas_propia"] = calcular_cantidad_ventasPropias(usuario,campania,agencia)
    print(f"\n Cantidad de ventas propias: {desempenioDeColaborador['cant_ventas_propia']}")

    # 2 - # Obtiene la productividad (total resumido) por las ventas propias
    desempenioDeColaborador["productividad_propia"] = calcular_productividad_ventasPropias(usuario,campania,agencia)
    print(f"\n Productividad de ventas propias: {desempenioDeColaborador['productividad_propia']}")

    # 3 - Obtiene la comision por cantidad de ventas propias
    desempenioDeColaborador["comision_x_cantVentasPropias"] = getDetalleComisionPorCantVentasPropias(usuario,campania,agencia)["comisionTotal"]
    print(f"\n Comision por cantidad de ventas propias: {desempenioDeColaborador['comision_x_cantVentasPropias']}")

    # 3.1 - Obtiene el detalle de la comision por cantidad de ventas propias
    detailDesempenioDict["cantidad_ventasPropias_comision"] = getDetalleComisionPorCantVentasPropias(usuario,campania,agencia) # Obtiene mas a detalle la comision por la cantidad ventas propias
        

    # 4 - Obtiene el premio por productividad de ventas propias
    desempenioDeColaborador["comision_x_productividadPropia"] = getPremioProductividadVentasPropias(usuario,campania,agencia)
    print(f"\n Premio por productividad de ventas propias: {desempenioDeColaborador['comision_x_productividadPropia']}")

    #endregion



    detailDesempenioDict["cantidad_ventasPropias_comision"] = getDetalleComisionPorCantVentasPropias(usuario,campania,agencia) # Obtiene mas a detalle la comision por la cantidad ventas propias
    detailDesempenioDict["productividad_ventasPropias_comision"] = getPremioProductividadVentasPropias(usuario,campania,agencia) # Obtiene mas a detalle la comision por la productividad de ventas propias
    detailDesempenioDict["cuotas1"] = getCuotas1(usuario,campania,agencia) # Obtiene a detalle la comision por cuotas 1 adelantadas
    detailDesempenioDict["adelantos"] = getAdelantos(usuario,campania) # Obtiene los adelantos de dinero que se le otorgo

    detailDesempenioDict["ausencias_tardanzas"] = getAusenciasTardanzas(usuario,campania) # Obtiene las faltas y tardanzas

    # Seteamos el subtotal por rol y el asegurado, ya que depende del rol de estos usuarios pueden cambiar los valores y dejamos como "Comision base" la manera en como comisiona un vendedor.
    desempenioDeColaborador["subtotal_comisionado_fromRol"] = 0

    # Esto se tiene que descontar de la comision ---> (detailDesempenioDict["adelantos"]["dineroTotal"] + detailDesempenioDict["ausencias_tardanzas"]["total_descuentos"])
    desempenioDeColaborador["subtotal_comisionado_ventasPropias"] = (detailDesempenioDict["cantidad_ventasPropias_comision"]["comisionTotal"] + detailDesempenioDict["productividad_ventasPropias_comision"] + detailDesempenioDict["cuotas1"]["totalDinero"])
    
    
    desempenioDeColaborador["cant_ventas_fromRol"] = 0
    desempenioDeColaborador["productividad_fromRol"] = 0
    if(usuario.rango.lower() not in "admin"):
        if(usuario.rango.lower() == "supervisor"):
            desempenioDeColaborador["cant_ventas_fromRol"] = calcular_ventas_supervisor(usuario,campania,agencia)
            desempenioDeColaborador["productividad_fromRol"] = calcular_productividad_supervisor(usuario,campania,agencia)
            desempenioDeColaborador["desempenioEquipo"] = desempenioEquipo_supervisor(usuario,campania,agencia)
            detailDesempenioDict["cantidad_ventasFromRol_comision"] = getComisionCantVentas_supervisor(usuario,campania,agencia)
            detailDesempenioDict["productividad_ventasFromRol_comision"] = getPremioxProductividad_supervisor(usuario,campania,agencia)

            desempenioDeColaborador["subtotal_comisionado_fromRol"] = detailDesempenioDict["cantidad_ventasFromRol_comision"] + detailDesempenioDict["productividad_ventasFromRol_comision"]

            # total_comisionado_sin_asegurado = (desempenioDeColaborador["subtotal_comisionado_fromRol"] + desempenioDeColaborador["subtotal_comisionado_ventasPropias"]) - (detailDesempenioDict["adelantos"]["dineroTotal"] + detailDesempenioDict["ausencias_tardanzas"]["total_descuentos"])
            # setPremiosPorObjetivo(usuario,campania,agencia,total_comisionado_sin_asegurado, desempenioDeColaborador["cant_ventas_fromRol"])
           
        elif(usuario.rango.lower() == "gerente sucursal"):
            detailDesempenioDict["cuotasX"] = getCuotasX(campania,agencia)
            desempenioDeColaborador["subtotal_comisionado_fromRol"] = detailDesempenioDict["cuotasX"]["comisionTotal_Cuotas"]
    
    desempenioDeColaborador["descuentoTotal"] = (detailDesempenioDict["adelantos"]["dineroTotal"] + detailDesempenioDict["ausencias_tardanzas"]["total_descuentos"])
    desempenioDeColaborador["comisionado_sin_descuento"] = (desempenioDeColaborador["subtotal_comisionado_fromRol"] + desempenioDeColaborador["subtotal_comisionado_ventasPropias"])
    desempenioDeColaborador["comisionado_con_descuento"] = (desempenioDeColaborador["subtotal_comisionado_fromRol"] + desempenioDeColaborador["subtotal_comisionado_ventasPropias"])  - desempenioDeColaborador["descuentoTotal"]
    desempenioDeColaborador["asegurado"] = getAsegurado(usuario,desempenioDeColaborador["comisionado_sin_descuento"])
    # desempenioDeColaborador["total_comisionado_sin_asegurado"] = desempenioDeColaborador["comisionado_sin_descuento"]
    
    setPremiosPorObjetivo(usuario,campania,agencia,desempenioDeColaborador["cant_ventas_fromRol"])

    premios = getPremiosPorObjetivo(usuario,campania)   
    desempenioDeColaborador["premios"] = premios["totalPremios"]
    detailDesempenioDict["premios"] = premios["premiosList"]
    
    desempenioDeColaborador["total_comisionado"] =  desempenioDeColaborador["comisionado_con_descuento"] + desempenioDeColaborador["asegurado"] + desempenioDeColaborador["premios"]

    desempenioDeColaborador["detalle"] = detailDesempenioDict
    
    return desempenioDeColaborador