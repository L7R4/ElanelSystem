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

        # Verfica que coeficiente usar segun la cantidad de ventas
        coeficientes_dict_list = coeficienteCantidadOrdenadoVendedor()
        
        try:
            coeficienteCheck = next(coef for coef in coeficientes_dict_list if coef["cantidad"] >= cantVentas)
        except StopIteration:
            coeficienteCheck = 0
        # Iterar sobre las ventas y calcular la comisión total

        
        # if usuario.nombre == "Sanchez Leila Ayelen":
        #     print("Coeficiente -> " + str(coeficienteCheck))
        for venta in ventas:
            # Calcular la comisión por venta y sumarla al total
            comision_por_venta = (venta.importe * coeficienteCheck[typePlan]) / 100
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
    # if usuario.nombre == "Sanchez Leila Ayelen":
    #     print("Productividad -> " + str(productividad))
    # Verfica que coeficiente usar segun la cantidad de ventas
    premio = 0
    premio_dict_list = coeficienteProductividadOrdenadoVendedor()
    
    if(productividad >= premio_dict_list[0]["dinero"]):
        premio = next(coef for coef in premio_dict_list if coef["dinero"] >= productividad)["dinero"]
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
                    totalDineroCuotas1 += v.cuotas[2]["total"]
                    
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
            oldPremiosPorCantVentas = list(filter(lambda x: x["concepto"].lower() == "Premio por cantidad de ventas" and x["campania"] == campania, premios))
            if(len(oldPremiosPorCantVentas) != 0):
                premio = {"metodoPago": "---", 
                        "dinero": f"{dineroAsegurado}", 
                        "agencia": f"{agencia.pseudonimo}", 
                        "campania": f"{campania}", 
                        "fecha": f"{datetime.now().strftime('%d/%m/%Y')}", 
                        "concepto": "Premio por cantidad de ventas"}
            
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

    # monto= 0
    # if(usuario.rango.lower() in "vendedor"):
    #     pass

    # if(usuario.rango.lower() in "supervisor"):
    #     asegurado = Asegurado.objects.get(dirigido="Supervisor")
    #     dineroAsegurado = asegurado.dinero
    #      # Si la suma de ventas del equipo supera 80, se le suma el asegurado como premio
    #     if cantVentas > 80:
    #         monto += dineroAsegurado
            
    # return monto

#region Funciones especificas del supervisor - - - - - - - -

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
    ventas_totales = Ventas.objects.filter(supervisor=usuario, campania=campania,agencia=agencia, adjudicado__status=False, deBaja__status=False)
    ventas_totales = [
        venta for venta in ventas_totales
        if len(venta.auditoria) > 0 and venta.auditoria[-1].get("grade") is True
    ]
    return len(ventas_totales)

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
    ventas = Ventas.objects.filter(supervisor=usuario, campania=campania,agencia=agencia, adjudicado__status=False, deBaja__status=False)
    ventas = [
        venta for venta in ventas
        if len(venta.auditoria) > 0 and venta.auditoria[-1].get("grade") is True
    ]
    cantVentas = ventas.count()

    total_comisionado = 0

    # Verfica que coeficiente usar segun la cantidad de ventas
    coeficientes_dict_list = coeficienteCantidadOrdenadoSupervisor()
    coeficienteCheck = next(coef for coef in coeficientes_dict_list if coef["cantidad"] >= cantVentas)

    # Iterar sobre las ventas y calcular la comisión total
    for venta in ventas:
        # Calcular la comisión por venta y sumarla al total
        comision_por_venta = venta.importe * coeficienteCheck["coeficiente"] / 100
        total_comisionado += comision_por_venta
    return total_comisionado

def desempenioEquipo(usuario,campania,agencia):
    listaVendedores = []
    ventas = Ventas.objects.filter(supervisor=usuario, campania=campania,agencia=agencia, adjudicado__status=False, deBaja__status=False)
    ventas = [
        venta for venta in ventas
        if len(venta.auditoria) > 0 and venta.auditoria[-1].get("grade") is True
    ]
    for venta in ventas:
        vendedor = venta.vendedor
        desempenioVendedor = {"nombre": vendedor.nombre,"cantidad_ventas": calcular_ventas_vendedor(vendedor,campania,agencia), "productividad":calcular_productividad_vendedor(vendedor,campania,agencia)}
        listaVendedores.append(desempenioVendedor)

    return listaVendedores

#endregion - - - - - - - - - - - - - - - - - - -

#region Funciones especificas del vendedor - - - - - - - - - -

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
    ventas = Ventas.objects.filter(vendedor=usuario, campania=campania,agencia=agencia, adjudicado__status=False, deBaja__status=False)
    # print(ventas)
    # for venta in ventas:
    #     print(venta.auditoria[-1].get("grade"))
    ventas = [
        venta for venta in ventas
        if len(venta.auditoria) > 0 and venta.auditoria[-1].get("grade") is True
    ]
    # cantVentasTotales = ventas.count()
    cantVentasTotales = len(ventas)

    return cantVentasTotales

def calcular_productividad_vendedor(usuario,campania,agencia):
    # Consulta para obtener las ventas del vendedor en la campaña
    ventas = Ventas.objects.filter(vendedor=usuario, campania=campania,agencia=agencia, adjudicado__status=False, deBaja__status=False)
    ventas = [
            venta for venta in ventas
            if len(venta.auditoria) > 0 and venta.auditoria[-1].get("grade") is True
    ]
    # Sumar los importes de los productos asociados a cada venta
    suma_importes = sum(venta.total_a_pagar for venta in ventas)
    return suma_importes

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

    
    # Obtenemos, INDEPENDIENTEMENTE del rango del usuario, las POSIBLES VENTAS PROPIAS del mismo
    desempenioDeColaborador["cant_ventas_propia"] = calcular_ventas_vendedor(usuario,campania,agencia) # Obtiene la cantidad (total resumido) de ventas  propias
    desempenioDeColaborador["productividad_propia"] = calcular_productividad_vendedor(usuario,campania,agencia) # Obtiene la productividad (total resumido) por las ventas propias

    detailDesempenioDict["cantidad_ventasPropias_comision"] = getDetalleComisionPorCantVentasPropias(usuario,campania,agencia) # Obtiene mas a detalle la comision por la cantidad ventas propias
    detailDesempenioDict["productividad_ventasPropias_comision"] = getPremioProductividadVentasPropias(usuario,campania,agencia) # Obtiene mas a detalle la comision por la productividad de ventas propias
    detailDesempenioDict["cuotas1"] = getCuotas1(usuario,campania,agencia) # Obtiene a detalle la comision por cuotas 1 adelantadas
    detailDesempenioDict["adelantos"] = getAdelantos(usuario,campania) # Obtiene los adelantos de dinero que se le otorgo

    detailDesempenioDict["ausencias_tardanzas"] = getAusenciasTardanzas(usuario,campania) # Obtiene las faltas y tardanzas

    # Seteamos el subtotal por rol y el asegurado, ya que depende del rol de estos usuarios pueden cambiar los valores y dejamos como "Comision base" la manera en como comisiona un vendedor.
    desempenioDeColaborador["subtotal_comisionado_fromRol"] = 0

    # Esto se tiene que descontar de la comision ---> (detailDesempenioDict["adelantos"]["dineroTotal"] + detailDesempenioDict["ausencias_tardanzas"]["total_descuentos"])
    desempenioDeColaborador["subtotal_comisionado_ventasPropias"] = (detailDesempenioDict["cantidad_ventasPropias_comision"]["comisionTotal"] + detailDesempenioDict["productividad_ventasPropias_comision"] + detailDesempenioDict["cuotas1"]["totalDinero"])
    # print("---------------------")
    # print(usuario.rango.lower())

    if(usuario.rango.lower() not in "admin"):
        if(usuario.rango.lower() == "supervisor"):
            desempenioDeColaborador["cant_ventas_fromRol"] = calcular_ventas_supervisor(usuario,campania,agencia)
            desempenioDeColaborador["productividad_fromRol"] = calcular_productividad_supervisor(usuario,campania,agencia)
            desempenioDeColaborador["desempenioEquipo"] = desempenioEquipo(usuario,campania,agencia)
            detailDesempenioDict["cantidad_ventasFromRol_comision"] = getComisionCantVentas(usuario,campania,agencia) if desempenioDeColaborador["asegurado"] == 0 else 0
            detailDesempenioDict["productividad_ventasFromRol_comision"] = getPremioxProductividad(usuario,campania,agencia)

            desempenioDeColaborador["subtotal_comisionado_fromRol"] = detailDesempenioDict["cantidad_ventasFromRol_comision"] + detailDesempenioDict["productividad_ventasFromRol_comision"]

            # total_comisionado_sin_asegurado = (desempenioDeColaborador["subtotal_comisionado_fromRol"] + desempenioDeColaborador["subtotal_comisionado_ventasPropias"]) - (detailDesempenioDict["adelantos"]["dineroTotal"] + detailDesempenioDict["ausencias_tardanzas"]["total_descuentos"])
            # setPremiosPorObjetivo(usuario,campania,agencia,total_comisionado_sin_asegurado, desempenioDeColaborador["cant_ventas_fromRol"])
           
        elif(usuario.rango.lower() == "gerente sucursal"):
            detailDesempenioDict["cuotasX"] = getCuotasX(campania,agencia)
            desempenioDeColaborador["subtotal_comisionado_fromRol"] = detailDesempenioDict["cuotasX"]["comisionTotal_Cuotas"]
    
    desempenioDeColaborador["descuentoTotal"] = (detailDesempenioDict["adelantos"]["dineroTotal"] + detailDesempenioDict["ausencias_tardanzas"]["total_descuentos"])
    desempenioDeColaborador["comisionado_sin_descuento"] = (desempenioDeColaborador["subtotal_comisionado_fromRol"] + desempenioDeColaborador["subtotal_comisionado_ventasPropias"])
    desempenioDeColaborador["comisionado_con_descuento"] = (desempenioDeColaborador["subtotal_comisionado_fromRol"] + desempenioDeColaborador["subtotal_comisionado_ventasPropias"])  - desempenioDeColaborador["descuentoTotal"]
    desempenioDeColaborador["asegurado"] = getAsegurado(usuario,desempenioDeColaborador["comisionado_con_descuento"])

    
    setPremiosPorObjetivo(usuario,campania,agencia,desempenioDeColaborador["total_comisionado_sin_asegurado"], desempenioDeColaborador["cant_ventas_fromRol"])
    premios = getPremiosPorObjetivo(usuario,campania)   
    desempenioDeColaborador["premios"] = premios["totalPremios"]
    detailDesempenioDict["premios"] = premios["premiosList"]
    
    desempenioDeColaborador["total_comisionado"] =  desempenioDeColaborador["comisionado_con_descuento"] + desempenioDeColaborador["asegurado"] + desempenioDeColaborador["premios"]

    desempenioDeColaborador["detalle"] = detailDesempenioDict
    
    return desempenioDeColaborador