from django.db import models
from django.forms import ValidationError
from users.models import Cliente,Usuario,Sucursal
from products.models import Products
from django.core.validators import RegexValidator
import json
import datetime
from dateutil.relativedelta import relativedelta
from sales.utils import obtener_ultima_campania

#region C-LISTA-PRECIOS
class CoeficientesListadePrecios(models.Model):
    valor_nominal = models.IntegerField("Valor Nominal:")
    cuota = models.IntegerField("Cuotas:")
    porcentage = models.FloatField("Porcentage:")
#endregion

#region VENTAS
class Ventas(models.Model):

    # Funcion para el siguiente numero de operacion automaticamente
    def returnOperacion():      
        if not Ventas.objects.last():
            numOperacion = 1
        else:
            lastOperacion = Ventas.objects.last()
            numOperacion = int(lastOperacion.nro_operacion) + 1
        return numOperacion
    
    # Funcion para crear las cuotas cuando se cree una venta 
    def crearCuotas(self):
        cuotas = self.cuotas
        fechaDeAlta = datetime.datetime.strptime(self.fecha, "%d/%m/%Y")
        # Setear la variable fechaDeVencimiento con un tipo fecha
        fechaDeVencimiento = fechaDeAlta
        contMeses = 0
        contYear = 0

        # Cuota 0
        cuotas.append({"cuota" :f'Cuota 0',
                       "nro_operacion": self.nro_operacion,
                       "status": "Pendiente",
                       "total": self.primer_cuota,
                       'pagado': 0,
                       'cobrador': "",
                       "fecha_pago": "", 
                       "hora": "", 
                       "metodoPago": "",
                       "descuento": 0,
                       "fechaDeVencimiento":"", 
                       "diasRetraso": 0,
                       "pagoParcial":{"status": False, "amount": []},
                       })
        
        # Otras cuotas
        for i in range(1,self.nro_cuotas+1):
            contMeses += 1
            
            #region Bloque para asignar la fecha de vencimiento a la primera cuota (Si es antes o desp del dia 25 del mes) a las ventas con modalidad MENSUAL
            if(self.modalidad == "Mensual"):
                if(i == 1):
                    if fechaDeAlta.day <= 25:
                        # Fecha de vencimiento es el 15 del próximo mes
                        fechaDeVencimiento = datetime.datetime(
                            year=fechaDeAlta.year,
                            month=fechaDeAlta.month,
                            day=15
                        ) + relativedelta(months=1)
                    else:
                        # Fecha de vencimiento es el 15 del siguiente mes después del próximo mes
                        fechaDeVencimiento = datetime.datetime(
                            year=fechaDeAlta.year,
                            month=fechaDeAlta.month,
                            day=15
                        ) + relativedelta(months=2)
                        
                else:
                    fechaDeVencimiento =  fechaDeVencimiento + self.contarDiasSegunModalidad(self.modalidad,fechaDeVencimiento)
            #endregion


            #region Bloque para asignar la fecha de vencimiento a otras MODALIDADES
            if(self.modalidad != "Mensual"):
                fechaDeVencimiento =  fechaDeVencimiento + self.contarDiasSegunModalidad(self.modalidad)
            #endregion

            cuotas.append({
                "cuota" :f'Cuota {i}',
                "nro_operacion": self.nro_operacion,
                "status": "Bloqueado",
                "total": self.importe_x_cuota + (self.importe_x_cuota * (self.PORCENTAJE_ANUALIZADO *contYear))/100,
                'pagado': 0,
                'cobrador': "",
                "fecha_pago": "", 
                "hora": "", 
                "metodoPago": "",
                "fechaDeVencimiento" : fechaDeVencimiento.strftime("%d/%m/%Y"),
                "descuento": 0,
                "diasRetraso": 0,
                "pagoParcial":{"status": False, "amount": []}
            })


            if(contMeses == 12):
                contMeses = 0
                contYear +=1


        if(self.adjudicado):
            for i in range(1,self.nro_cuotas+1):
                cuota = cuotas[i]
                cuota["interesPorMora"] = 0
                cuota["totalFinal"] = 0

        self.cuotas = cuotas
        self.save()
    
    # Modalidades de tiempo de pago
    MODALIDADES = (
        ('Diario', 'Diario'),
        ('Semanal', 'Semanal'),
        ('Quincenal', 'Quincenal'),
        ('Mensual', 'Mensual'),
    )
    
    PORCENTAJE_ANUALIZADO = 15
    
    # Estados inciales de campos deBaja, adjudicacion, auditorias
    DEFAULT_STATUS_BAJA ={
        "status" : False,
        "motivo" : "",
        "detalleMotivo" : "",
        "observacion" : "",
        "responsable" : ""
    }

    DEFAULT_STATUS_ADJUDICACION = {
        "status" : False,
        "tipo" : ""
    }

    DEFAULT_STATUS_AUDITORIAS =[{
            "version":0,
            "realizada":False,
            "grade":False,
            "comentarios":"",
            "fecha_hora": "",
        }]
    
    #region Campos
    nro_cliente = models.ForeignKey(Cliente,on_delete=models.CASCADE,related_name="ventas_nro_cliente")
    nro_solicitud = models.CharField("Nro solicitud:",max_length=10,validators=[RegexValidator(r'^\d+(\.\d+)?$', 'Ingrese un número válido')],default="")
    modalidad = models.CharField("Modalidad:",max_length=15, choices=MODALIDADES,default="")
    nro_cuotas = models.IntegerField()
    nro_operacion = models.IntegerField(default=returnOperacion)
    agencia = models.ForeignKey(Sucursal, on_delete=models.DO_NOTHING,blank = True, null = True)
    campania = models.IntegerField(default=0)
    cambioTitularidadField = models.JSONField(default=list,blank=True,null=True)
    
    suspendida = models.BooleanField(default=False)
    importe = models.FloatField("Importe:",default=0)
    tasa_interes = models.FloatField("Tasa de Interes:",validators=[RegexValidator(r'^\d+(\.\d+)?$', 'Ingrese un número válido')],default=0)
    primer_cuota =models.FloatField("Primer cuota:",default=0)
    anticipo =models.IntegerField("Cuota de Inscripcion:",default=0)
    intereses_generados = models.FloatField("Intereses Gen:",default=0)
    importe_x_cuota = models.FloatField("Importe x Cuota:",default=0)
    total_a_pagar = models.FloatField("Total a pagar:",default=0)
    fecha = models.CharField("Fecha:", max_length=30,default="")
    tipo_producto = models.CharField(max_length=20,default="")
    producto = models.ForeignKey(Products,on_delete=models.CASCADE,related_name="ventas_producto",default="")
    paquete = models.CharField(max_length=20,default="")
    nro_orden = models.CharField("Nro de Orden:",max_length=10,validators=[RegexValidator(r'^\d+(\.\d+)?$', 'Ingrese un número válido')],default="")
    vendedor = models.ForeignKey(Usuario,on_delete=models.CASCADE,related_name="ventas_ven_usuario",default="",blank=True,null=True)
    supervisor = models.ForeignKey(Usuario,on_delete=models.CASCADE,related_name="venta_super_usuario",default="",blank=True,null=True)
    observaciones = models.CharField("Obeservaciones:",max_length=255,blank=True,null=True)
    auditoria = models.JSONField(default=DEFAULT_STATUS_AUDITORIAS)
    adjudicado = models.JSONField(default=DEFAULT_STATUS_ADJUDICACION)
    deBaja = models.JSONField(default=DEFAULT_STATUS_BAJA)
    cuotas = models.JSONField(default=list)
    #endregion
    

    def contarDiasSegunModalidad(self,modalidad,ultimaFechaDevencimiento = ""):
        modalidad = modalidad.lower()

        if modalidad == 'diario':
            dias_a_sumar = 1
        elif modalidad == 'semanal':
            dias_a_sumar = 7
        elif modalidad == 'quincenal':
            dias_a_sumar = 15
        elif modalidad == 'mensual':
            # Usa relativedelta para sumar un mes y porque no todos los meses tienen la misma cantidad de dias forzamos el valor de los dias a 15
            ultimaFecha_mas_un_mes = (ultimaFechaDevencimiento + relativedelta(months=1)).replace(day=15)
            # # Calcula la diferencia en días
            dias_a_sumar = (ultimaFecha_mas_un_mes - ultimaFechaDevencimiento).days
        else:
            raise ValueError("Modalidad no válida")

        fecha_resultado = relativedelta(days=dias_a_sumar)
        return fecha_resultado


    def createCambioTitularidad(self,lastCuota,user,oldCustomer,newCustomer,pkOldCustomer,pkNewCustomer):
        cambioTitularidadField = self.cambioTitularidadField
        if(pkNewCustomer == self.nro_cliente.pk):
            raise ValueError("No se puede cambiar por el mismo cliente")
        
        if(len(cambioTitularidadField) == 0):
            idDelCambio = 0
            cambioTitularidadField.append(
                    {  
                       "change" :True,
                       "id": idDelCambio,
                       "lastCuota": lastCuota,
                       "fecha": datetime.datetime.now().strftime("%d/%m/%Y"),
                       "user": user,
                       "oldCustomer":oldCustomer,
                       "pkOldCustomer": pkOldCustomer,
                       "newCustomer":newCustomer,
                       "pkNewCustomer": pkNewCustomer

                    })
        else:
            idDelCambio = self.cambioTitularidadField[-1]["id"] + 1
            cambioTitularidadField.append(
                    {  
                       "change" :True,
                       "id": idDelCambio,
                       "lastCuota": lastCuota,
                       "fecha": datetime.datetime.now().strftime("%d/%m/%Y"),
                       "user": user,
                       "oldCustomer":oldCustomer,
                       "pkOldCustomer": pkOldCustomer,
                       "newCustomer":newCustomer,
                       "pkNewCustomer": pkNewCustomer

                    })
        
        self.save()


    def cuotas_pagadas(self):
        cuotas = [cuota for cuota in self.cuotas if cuota["status"] == "Pagado"]
        try:
            cuotas.pop(0)
            return [cuota for cuota in cuotas if cuota["status"] == "Pagado"]
        except IndexError as e:
            return []
    
    
    def darBaja(self,motivo,porcentaje,detalleMotivo,observacion,responsable):
        self.deBaja["status"] = True
        self.deBaja["motivo"] = motivo
        self.deBaja["porcentaje"] = porcentaje
        self.deBaja["observacion"] = observacion
        self.deBaja["detalleMotivo"] = detalleMotivo
        self.deBaja["responsable"] = responsable
        self.deBaja["fecha"] = datetime.datetime.now().strftime("%d/%m/%Y -- %H:%M")
        self.save()
         
        
    def calcularDineroADevolver(self):
        dineroADevolver = 0
        cuotasPagadasCant = len(self.cuotas_pagadas())
        porcentage = int(self.deBaja["porcentaje"])
        cuotasPagas = self.cuotas_pagadas()
        valores = [item["total"] for item in cuotasPagas]

        if(cuotasPagadasCant >= 6):
            dineroADevolver=(sum(valores)*(porcentage/100)) - cuotasPagas[len(cuotasPagas)-1]["total"]
        elif(porcentage != 0 and cuotasPagadasCant < 6):
            dineroADevolver = sum(valores)*(porcentage/100)
        return dineroADevolver


    def suspenderOperacion(self):
        initial = 1
        if(self.adjudicado["status"] == True):
            initial = 0

        cuotas = self.cuotas
        contAtrasados = 0
        for i in range(initial,int(self.nro_cuotas+initial)):
            if(cuotas[i]["status"] == "Atrasado"):
                contAtrasados +=1

        if contAtrasados >= 3:
            self.suspendida = True
            self.save()
        elif(self.suspendida == True and contAtrasados==0):
            self.suspendida = False
            self.save()
        elif(self.suspendida==False and contAtrasados < 3):
            print("La operacion "+ str(self.pk)+" esta activa")
        
        
    def crearAdjudicacion(self,nroDeVenta,tipo):
        self.cuotas.pop(0)
        self.cuotas[0]["status"] = "Pendiente"
        self.nro_operacion = nroDeVenta

        self.adjudicado["status"] = True
        self.adjudicado["tipo"] = tipo

        self.save()

    #region CuotasManagement
    def desbloquearCuota(self,cuota):
        for i in range(0,int(self.nro_cuotas)):
            if (cuota == self.cuotas[i]["cuota"]):
                self.cuotas[i+1]["status"] = "Pendiente"
                break
        self.save()
        
    
    def pagoTotal(self,cuota,metodoPago,cobrador):

        cuotaSeleccionada = list(filter(lambda x:x["cuota"] == cuota,self.cuotas))[0]
        if(cuotaSeleccionada["status"] != "Pagado"):
            cuotaSeleccionada["fecha_pago"] = datetime.datetime.now().strftime("%d/%m/%Y")
            cuotaSeleccionada["status"] = "Pagado"
            cuotaSeleccionada["pagado"] = cuotaSeleccionada["total"] - cuotaSeleccionada["descuento"]
            cuotaSeleccionada["cobrador"] = cobrador
            cuotaSeleccionada["hora"] = datetime.datetime.now().time().strftime("%H:%M")
            cuotaSeleccionada["metodoPago"] = metodoPago
            cuotaSeleccionada["campania"] = obtener_ultima_campania()
            self.desbloquearCuota(cuota)
            
            # Cada vez que se pague una cuota tiene que verificar el estado de la venta, es decir, si se reactiva, se suspende, etc.  
            self.suspenderOperacion()
        else:
            raise ValueError("Esta cuota ya esta pagada")
        
        self.save()
                

    def pagoParcial(self,cuota,metodoPago,amount,cobrador):
        cuotaSeleccionada = list(filter(lambda x:x["cuota"] == cuota,self.cuotas))[0]
        cuotaSeleccionada["pagoParcial"]["status"]= True
        cuotaSeleccionada["pagoParcial"]["amount"].append({"value": int(amount), 
                                                            "date":datetime.datetime.now().strftime("%d/%m/%Y"),
                                                            "hour": datetime.datetime.now().time().strftime("%H:%M"),
                                                            "metodo":metodoPago,
                                                            "cobrador": cobrador,
                                                            "campania":obtener_ultima_campania()})
        
        valores_parciales = cuotaSeleccionada.get("pagoParcial", {}).get("amount", [])
        valores_parciales = [item["value"] for item in valores_parciales]
        sumaPagosParciales = sum(valores_parciales)
        cuotaSeleccionada["pagado"] += sumaPagosParciales
        
        if(sumaPagosParciales < cuotaSeleccionada["total"] - cuotaSeleccionada["descuento"]):
            cuotaSeleccionada["status"] = "Parcial"
            
        elif(sumaPagosParciales == cuotaSeleccionada["total"] - cuotaSeleccionada["descuento"]):
            cuotaSeleccionada["status"] = "Pagado"
            self.desbloquearCuota(cuota)
            self.suspenderOperacion()
            
        self.save()
         

    def aplicarDescuento(self,cuota,dinero):
        cuotaSeleccionada = list(filter(lambda x:x["cuota"] == cuota,self.cuotas))[0]
        if(cuotaSeleccionada["status"] != "Pagado" and (cuotaSeleccionada["cuota"] == "Cuota 0" or cuotaSeleccionada["cuota"] == "Cuota 1")):
            cuotaSeleccionada["descuento"] += dinero
        else:
            raise ValueError("Solo se puede aplicar descuento a la cuota 0 y 1. En otro caso, esta cuota está pagada")
        self.save()


    def testVencimientoCuotas(self):
        initial = 1
        if(self.adjudicado["status"] == True):
            initial = 0

        for i in range(initial,int(self.nro_cuotas + initial)):
            cuota = self.cuotas[i]["fechaDeVencimiento"]
            if(datetime.datetime.now() > datetime.datetime.strptime(cuota,"%d/%m/%Y") and (self.cuotas[i]["status"] == "Pendiente" or self.cuotas[i]["status"] == "Bloqueado" or self.cuotas[i]["status"] == "Parcial")):
                self.cuotas[i]["status"] = "Atrasado"
                diasDeRetraso = self.contarDias(datetime.datetime.strptime(cuota,"%d/%m/%Y"))
                self.cuotas[i]["diasRetraso"] = diasDeRetraso
        self.save()
    #endregion

    def addPorcentajeAdjudicacion(self):
        NOW = datetime.datetime.now()
        INTERES = 0.01
        cuotas = self.cuotas

        initial = 1
        if(self.adjudicado["status"] == True):
            initial = 0

        for i in range(initial,int(self.nro_cuotas + initial)):
            fechaVencimiento = cuotas[i]["fechaDeVencimiento"]
            fechaVencimientoFormated = datetime.datetime.strptime(fechaVencimiento,"%d/%m/%Y")
            fechaInicioDeCuota = fechaVencimientoFormated + relativedelta(months=-1)
            
            if(NOW > fechaInicioDeCuota + relativedelta(days=+15)):
                cantidadDias = (NOW - (fechaInicioDeCuota + relativedelta(days=+15))).days
                cuotas[i]["interesPorMora"] = cantidadDias*INTERES
                cuotas[i]["totalFinal"] = cuotas[i]["total"]+(cuotas[i]["total"] * cuotas[i]["interesPorMora"])

            self.cuotas = cuotas
        self.save()


    def contarDias(self,fechaReferente):
        contadorDias = 0
        fechaHoy = datetime.datetime.now().strftime("%d/%m/%Y")
        while fechaReferente != datetime.datetime.strptime(fechaHoy,"%d/%m/%Y"):
            fechaReferente = fechaReferente + relativedelta(days=1)
            contadorDias += 1
        return contadorDias
#endregion

#region ARQUEO
class ArqueoCaja(models.Model):
    agencia = models.ForeignKey(Sucursal, on_delete=models.DO_NOTHING,blank = True, null = True)
    fecha = models.CharField("Fecha", max_length=30)
    admin = models.CharField(max_length=70, default="")
    responsable = models.CharField(max_length=70, default="")
    totalPlanilla = models.FloatField("Total Planilla Efectivo", default=0)
    totalSegunDiarioCaja = models.FloatField("Total segun diario de caja", default=0)
    diferencia = models.FloatField("Diferencia", default=0)
    observaciones = models.TextField()
    detalle = models.JSONField(default=dict)
#endregion

#region MOVsEXTERNOS
class MovimientoExterno(models.Model):
    TIPOS_MOVIMIENTOS = (
        ('Ingreso', 'Ingreso'),
        ('Egreso', 'Egreso'), 
    )
    TIPOS_COMPROBANTES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    )
    TIPOS_MONEDAS = (
        ('ARS', 'ARS'),
        ('USD', 'USD'),
        ('BRL', 'BRL'),
    )

    TIPO_DE_IDENTIFICACION = (
        ('DNI', 'DNI'),
        ('CUIT', 'CUIT'),
    )
    
    tipoIdentificacion = models.CharField("Tipo de identificacion:", max_length=15, choices=TIPO_DE_IDENTIFICACION, blank=True, null=True)
    nroIdentificacion = models.CharField("N° de Identificacion:", max_length=20, blank=True, null=True)
    tipoComprobante = models.CharField("Tipo de comprobante:", max_length=3, choices=TIPOS_COMPROBANTES, blank=True, null=True)
    nroComprobante = models.CharField("Nro de comprobante:", max_length=40, blank=True, null=True)
    denominacion = models.CharField("Denominacion del ente:", max_length=60, blank=True, null=True)
    tipoMoneda = models.CharField("Tipo de moneda:", max_length=3, choices=TIPOS_MONEDAS, blank=True, null=True)
    movimiento = models.CharField("Movimiento:",max_length=8, choices=TIPOS_MOVIMIENTOS)
    dinero = models.FloatField("Dinero:")
    metodoPago = models.CharField("Metodo de pago:",max_length=30)
    agencia = models.ForeignKey(Sucursal, on_delete=models.DO_NOTHING,blank = True, null = True)
    ente = models.CharField("Ente:",max_length=40)
    fecha = models.CharField("Fecha:",max_length=10)
    campania = models.IntegerField("Campaña:",default=0)
    concepto = models.CharField("Concepto:",max_length=200)
    premio = models.BooleanField("Premio:", default=False)
    adelanto = models.BooleanField("Adelanto:",default=False)
    hora = models.CharField("Hora:",max_length=6)

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)
        movimiento = cleaned_data.get('movimiento')

        if movimiento != 'Ingreso':
            tipo_identificacion = cleaned_data.get('tipoIdentificacion')
            nro_identificacion = cleaned_data.get('nroIdentificacion')
            tipo_comprobante = cleaned_data.get('tipoComprobante')
            nro_comprobante = cleaned_data.get('nroComprobante')

            tipo_identificacion_permitidas = [m[0].lower() for m in self.TIPO_DE_IDENTIFICACION]
            if tipo_identificacion and tipo_identificacion.lower() not in tipo_identificacion_permitidas:
                raise ValidationError({'tipoIdentificacion': 'Tipo de identificación no válida'})

            if nro_identificacion and not nro_identificacion.isdigit():
                raise ValidationError({'nroIdentificacion': 'El número de identificación debe ser un valor numérico.'})

            tipo_comprobante_permitidas = [m[0].lower() for m in self.TIPOS_COMPROBANTES]
            if tipo_comprobante and tipo_comprobante.lower() not in tipo_comprobante_permitidas:
                raise ValidationError({'tipoComprobante': 'Tipo de comprobante no válido'})

            if nro_comprobante and not nro_comprobante.isdigit():
                raise ValidationError({'nroComprobante': 'El número de comprobante debe ser un valor numérico.'})
        else:
            tipo_moneda = cleaned_data.get('nroComprobante')
            tipo_monedas_permitidas = [m[0].lower() for m in self.TIPOS_MONEDAS]
            if tipo_moneda and tipo_moneda.lower() not in tipo_monedas_permitidas:
                raise ValidationError({'tipoMoneda': 'Tipo de moneda no válida'})
#endregion