from datetime import timedelta
from sales.models import Ventas,MovimientoExterno
from .models import *
from sales.utils import searchSucursalFromStrings, obtener_ultima_campania
from django.db.models import Q

def liquidaciones_countFaltas(colaborador):
    data = colaborador.faltas_tardanzas
    tardanzas = sum(1 for elemento in data if elemento["hora"] != "---")

    # Cada 3 tardanzas se cuenta 1 falta mas
    faltas = sum(1 for elemento in data if elemento["hora"] == "---") + int(tardanzas/3)
    return faltas

def liquidaciones_countTardanzas(colaborador):
    data = colaborador.faltas_tardanzas
    tardanzas = sum(1 for elemento in data if elemento["hora"] != "---")
    return tardanzas



# FUNCIONES PARA OBTENER LA COMISION DE UN USUARIO (Vendedor, Supervisor, Gerente Sucursal) -----------------------------------------
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

def getAsegurado(usuario,cantVentas):
    dineroAsegurado = 0

    # if(usuario.rango.lower() in "vendedor"):
    #     aseguradoObject = Asegurado.objects.get(dirigido="Vendedor")
    #     dineroAsegurado = aseguradoObject.dinero
    if(usuario.rango.lower() in "supervisor"):
        aseguradoObject = Asegurado.objects.get(dirigido="Supervisor")
        if(cantVentas < aseguradoObject.objetivo):
            dineroAsegurado = aseguradoObject.dinero
    return calcularAseguradoSegunDiasTrabajados(dineroAsegurado,usuario.fec_ingreso)


def getDetalleComisionPorCantVentasPropias(usuario,campania,agencia):
    typePlanes = ["com_48_60","com_24_30_motos","com_24_30_elec_soluc"]
    detalleDict = {"planes":{}}
    cantVentasTotal = 0
    comisionTotal = 0
    ventas = ""
    for typePlan in typePlanes:
        if(typePlan =="com_48_60"):
            ventas = Ventas.objects.filter(vendedor=usuario, campania=campania, agencia=agencia ,nro_cuotas__in=[48, 60])
        elif (typePlan =="com_24_30_motos"):
            ventas = Ventas.objects.filter(vendedor=usuario, campania=campania, agencia=agencia ,nro_cuotas__in=[24, 30] , producto__tipo_de_producto="Moto")
        elif (typePlan =="com_24_30_elec_soluc"):
            ventas = Ventas.objects.filter(vendedor=usuario, campania=campania, agencia=agencia ,nro_cuotas__in=[24, 30] , producto__tipo_de_producto__in=["Prestamo","Electrodomestico"])

        cantVentas = ventas.count()
        comision = 0

        # Verfica que coeficiente usar segun la cantidad de ventas
        coeficientes_dict_list = coeficienteCantidadOrdenadoVendedor()
        
        try:
            coeficienteCheck = next(coef for coef in coeficientes_dict_list if coef["cantidad"] >= cantVentas)
        except StopIteration:
            coeficienteCheck = 0

        # Iterar sobre las ventas y calcular la comisión total
        for venta in ventas:
            # Calcular la comisión por venta y sumarla al total
            comision_por_venta = venta.producto.importe * coeficienteCheck[typePlan] / 100
            comision += comision_por_venta
            
        detalleDict["planes"][typePlan] = {"cantidad_ventas": cantVentas, "comision": comision}

        cantVentasTotal += cantVentas 
        comisionTotal += comision 

    detalleDict["cantVentasTotalPropias"] = cantVentasTotal
    detalleDict["comisionTotal"] = comisionTotal
    return detalleDict

def getPremioProductividadVentasPropias(usuario,campania,agencia):
    # Consulta para obtener las ventas del vendedor en la campaña
    ventas = Ventas.objects.filter(vendedor=usuario, campania=campania,agencia=agencia)

    # Sumar los importes de los productos asociados a cada venta
    productividad = sum(venta.producto.importe for venta in ventas)

    # Verfica que coeficiente usar segun la cantidad de ventas
    premio = 0
    premio_dict_list = coeficienteProductividadOrdenadoVendedor()
    print("Premio --------------")
    print(premio_dict_list)
    if(productividad >= premio_dict_list[0]["dinero"]):
        premio = next(coef for coef in premio_dict_list if coef["dinero"] >= productividad)["dinero"]
    
    return premio

def getAusenciasTardanzas(usuario, campania):
        if(usuario.faltas_tardanzas == []):
            return {"total_descuentos": 0, "detalle":[]}
        else:
            aus_tar = [item for item in usuario.faltas_tardanzas if item["campania"] == campania]
            total_descuentos = sum(int(d["descuento"]) for d in aus_tar)
            return {"total_descuentos": total_descuentos, "detalle":aus_tar}

def getAdelantos(usuario,campania):
    dniUsuario = usuario.dni
    movsExternos = list(MovimientoExterno.objects.filter(campania=campania, nroIdentificacion=dniUsuario, adelanto=True))
    dineroTotal = 0

    for mov in movsExternos:
        dineroTotal += mov.dinero

    return {'dineroTotal': dineroTotal, 'detalle': movsExternos}

def getCuotas1(usuario,campania):
        totalDineroCuotas1 = 0
        cuotas1Adelantadas = []
        ventas = Ventas.objects.filter(vendedor=usuario,campania=campania ,adjudicado__status = False)
       
        for v in ventas:
            if(v.cuotas[1]["status"] == "Pagado"):
               fechaCuota = datetime.strptime(v.cuotas[1]["fecha_pago"],"%d/%m/%Y")
               fechaAltaVenta = datetime.strptime(v.fecha,"%d/%m/%Y")

               if((fechaCuota-fechaAltaVenta).days <= 15):
                    cuotas1Adelantadas.append(v.cuotas[1])
                    totalDineroCuotas1 += v.cuotas[2]["total"]
                    
        return {"totalDinero": totalDineroCuotas1,"detalle":cuotas1Adelantadas}


# Funciones especificas del supervisor - - - - - - - -

def coeficienteCantidadOrdenadoSupervisor():
        coeficientes_dict_list = [
            {"cantidad": instancia.cantidad_maxima, "coeficiente": instancia.coeficiente}
            for instancia in CoeficientePorCantidadSupervisor.objects.all()
        ]

        # Ordenar la lista por la cantidad
        coeficientes_dict_list = sorted(coeficientes_dict_list, key=lambda x: x["cantidad"])

        return coeficientes_dict_list
    
def coeficienteProductividadOrdenadoSupervisor():
    coeficientes_dict_list = [
        {"dinero": instancia.dinero, "coeficiente": instancia.coeficiente}
        for instancia in CoeficientePorProductividadSupervisor.objects.all()
    ]
    # Ordenar la lista por la cantidad
    coeficientes_dict_list = sorted(coeficientes_dict_list, key=lambda x: x["dinero"])
    return coeficientes_dict_list

def calcular_ventas_supervisor(usuario,campania,agencia):
    # Consulta para obtener la cantidad total de ventas del vendedor en la campaña
    ventas_totales = Ventas.objects.filter(supervisor=usuario, campania=campania, agencia=agencia).count()
        
    return ventas_totales

def calcular_productividad_supervisor(usuario,campania,agencia):
    # Consulta para obtener las ventas del vendedor en la campaña
    ventas = Ventas.objects.filter(supervisor=usuario, campania=campania,agencia=agencia)

    # Sumar los importes de los productos asociados a cada venta
    suma_importes = sum(venta.producto.importe for venta in ventas)
    return suma_importes

def getPremioxProductividad(usuario,campania,agencia):
    totalProductividad = calcular_productividad_supervisor(usuario,campania,agencia)
    premio = 0
    # Verfica que coeficiente usar segun la cantidad de ventas
    coeficientes_dict_list = coeficienteProductividadOrdenadoSupervisor()
    if(totalProductividad >= coeficientes_dict_list[0]["dinero"]):
        coeficienteCheck = next(coef for coef in coeficientes_dict_list if coef["dinero"] >= totalProductividad)
        premio = totalProductividad * coeficienteCheck["coeficiente"]

    return premio

def getComisionCantVentas(usuario,campania,agencia):
    ventas = Ventas.objects.filter(supervisor=usuario,campania=campania,agencia=agencia)
    cantVentas = ventas.count()

    total_comisionado = 0

    # Verfica que coeficiente usar segun la cantidad de ventas
    coeficientes_dict_list = coeficienteCantidadOrdenadoSupervisor()
    coeficienteCheck = next(coef for coef in coeficientes_dict_list if coef["cantidad"] >= cantVentas)

    # Iterar sobre las ventas y calcular la comisión total
    for venta in ventas:
        # Calcular la comisión por venta y sumarla al total
        comision_por_venta = venta.producto.importe * coeficienteCheck["coeficiente"] / 100
        total_comisionado += comision_por_venta
    return total_comisionado

# - - - - - - - - - - - - - - - - - - -

# Funciones especificas del vendedor - - - - - - - - - -

def coeficienteCantidadOrdenadoVendedor():
    coeficientes_dict_list = [
        {"cantidad": instancia.cantidad_maxima, "com_48_60": instancia.com_48_60, "com_24_30_motos": instancia.com_24_30_motos, "com_24_30_elec_soluc": instancia.com_24_30_elec_soluc}
        for instancia in CoeficientePorCantidadVendedor.objects.all()
    ]
    # Ordenar la lista por la cantidad
    coeficientes_dict_list = sorted(coeficientes_dict_list, key=lambda x: x["cantidad"])
    return coeficientes_dict_list

def coeficienteProductividadOrdenadoVendedor():
    coeficientes_dict_list = [
        {"dinero": instancia.dinero, "premio": instancia.premio}
        for instancia in CoeficientePorProductividadVendedor.objects.all()
    ]
    # Ordenar la lista por la cantidad
    coeficientes_dict_list = sorted(coeficientes_dict_list, key=lambda x: x["dinero"])
    return coeficientes_dict_list

def calcular_ventas_vendedor(usuario,campania,agencia):
    # Consulta para obtener la cantidad total de ventas del vendedor en la campaña
    ventas_totales = Ventas.objects.filter(vendedor=usuario, campania=campania, agencia=agencia).count()
        
    return ventas_totales

def calcular_productividad_vendedor(usuario,campania,agencia):
    # Consulta para obtener las ventas del vendedor en la campaña
    ventas = Ventas.objects.filter(vendedor=usuario, campania=campania,agencia=agencia)

    # Sumar los importes de los productos asociados a cada venta
    suma_importes = sum(venta.producto.importe for venta in ventas)
    return suma_importes

# - - - - - - - - - - - - - - - - - - -

# Funcionsaes especificas del gerente de sucursal - - - - - - - - - -

def getCuotasX(campania,agencia):
    cuotasToFilter = ['1','2','3','4']
    cuotasDict = {}
    
    cantidadTotalCuotas = 0
    dineroTotalCuotas = 0
    comisionTotalCuotas = 0
    ventas = Ventas.objects.filter(agencia=agencia,campania=campania, adjudicado__status=False)

    # Cuota de inscripcion
    cantCuotas0 = 0
    dineroTotal_Cuota0 = 0
    objetivo = Asegurado.objects.get(dirigido ="Gerente sucursal").objetivo
    dinero = Asegurado.objects.get(dirigido ="Gerente sucursal").dinero
    for v in ventas:
        if(v.cuotas[0]["status"] == "Pagado"):
            cantCuotas0 += 1
            dineroTotal_Cuota0 += v.cuotas[0]["total"]
    comisionTotal_x_Cuota0 = dinero * cantCuotas0 if cantCuotas0 >= objetivo else 0
    cantidadTotalCuotas += cantCuotas0
    dineroTotalCuotas += dineroTotal_Cuota0
    comisionTotalCuotas += comisionTotal_x_Cuota0
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
    
# - - - - - - - - - - - - - - - - - - -


def getComisionTotal(usuario,campania,agencia):
    desempenioDeColaborador = {}
    detailDesempenioDict = {}
    detailDesempenioDict["comision_CantVentasPropias"] = getDetalleComisionPorCantVentasPropias(usuario,campania,agencia)
    detailDesempenioDict["comision_ProducVentasPropias"] = getPremioProductividadVentasPropias(usuario,campania,agencia)
    detailDesempenioDict["adelantos"] = getAdelantos(usuario,campania)
    detailDesempenioDict["aus_tar"] = getAusenciasTardanzas(usuario,campania)
    detailDesempenioDict["cuotas1"] = getCuotas1(usuario,campania)
    print(usuario.rango)
    print("---------------------")
    if(usuario.rango.lower() not in "admin"):
        if(usuario.rango.lower() in "vendedor"):
            desempenioDeColaborador["cant_ventas"] = calcular_ventas_vendedor(usuario,campania,agencia)
            desempenioDeColaborador["productividad"] = calcular_productividad_vendedor(usuario,campania,agencia)
            desempenioDeColaborador["total_comisionado"] = (detailDesempenioDict["comision_CantVentasPropias"]["comisionTotal"] + detailDesempenioDict["comision_ProducVentasPropias"] + detailDesempenioDict["cuotas1"]["totalDinero"]) - (detailDesempenioDict["adelantos"]["dineroTotal"] + detailDesempenioDict["aus_tar"]["total_descuentos"])
            
        elif(usuario.rango.lower() in "supervisor"):
            desempenioDeColaborador["cant_ventas"] = calcular_ventas_supervisor(usuario,campania,agencia)
            desempenioDeColaborador["productividad"] = calcular_productividad_supervisor(usuario,campania,agencia)
            detailDesempenioDict["com_CantVentas_total"] = getComisionCantVentas(usuario,campania,agencia)
            detailDesempenioDict["com_PremioProductividad_total"] = getPremioxProductividad(usuario,campania,agencia)
            detailDesempenioDict["asegurado"] = getAsegurado(usuario,desempenioDeColaborador["cant_ventas"])

            desempenioDeColaborador["total_comisionado"] = (detailDesempenioDict["comision_CantVentasPropias"]["comisionTotal"] + detailDesempenioDict["comision_ProducVentasPropias"] + detailDesempenioDict["com_CantVentas_total"] + detailDesempenioDict["com_PremioProductividad_total"] + detailDesempenioDict["cuotas1"]["totalDinero"] + detailDesempenioDict["asegurado"]) - (detailDesempenioDict["adelantos"]["dineroTotal"] + detailDesempenioDict["aus_tar"]["total_descuentos"])
        elif(usuario.rango.lower() in "gerente sucural"):
            detailDesempenioDict["cuotasX"] = getCuotasX(campania,agencia)
            
            desempenioDeColaborador["total_comisionado"] = (detailDesempenioDict["comision_CantVentasPropias"]["comisionTotal"] + detailDesempenioDict["comision_ProducVentasPropias"] + detailDesempenioDict["cuotas1"]["totalDinero"] + detailDesempenioDict["cuotasX"]["comisionTotal_Cuotas"]) - (detailDesempenioDict["adelantos"]["dineroTotal"] + detailDesempenioDict["aus_tar"]["total_descuentos"])
        

    desempenioDeColaborador["detalle"] = detailDesempenioDict
    print("Desempeño de colaborador")
    print(desempenioDeColaborador)
    return desempenioDeColaborador