from django.db import models
from users.models import Cliente,Usuario
from products.models import Products
from django.core.validators import RegexValidator
import json
import datetime
from dateutil.relativedelta import relativedelta


class CoeficientesListadePrecios(models.Model):
    valor_nominal = models.IntegerField("Valor Nominal:")
    cuota = models.IntegerField("Cuotas:")
    porcentage = models.FloatField("Porcentage:")

# class ListadePreciosDeCuotaInscripcion(models.Model):
#     valor_nominal = models.IntegerField("Valor Nominal:")
#     cuota = models.IntegerField("Cuotas:")
#     porcentage = models.FloatField("Porcentage:")


class Ventas(models.Model):

    def returnOperacion():
        if not Ventas.objects.last():
            numOperacion = 1
        else:
            lastOperacion = Ventas.objects.last()
            numOperacion = int(lastOperacion.nro_operacion) + 1
        return numOperacion
       
    
    MODALIDADES = (
        ('Diario', 'Diario'),
        ('Semanal', 'Semanal'),
        ('Quincenal', 'Quincenal'),
        ('Mensual', 'Mensual'),
    )
    PORCENTAJE_ANUALIZADO = 15;
   
    AGENCIAS = (
        ("Agencia Chaco", "Agencia Chaco"),
        ("Agencia Corrientes", "Agencia Corrientes"),
        ("Agencia Misiones", "Agencia Misiones"),
    )

    nro_cliente = models.ForeignKey(Cliente,on_delete=models.CASCADE,related_name="ventas_nro_cliente")
    nro_solicitud = models.CharField("Nro solicitud:",max_length=10,validators=[RegexValidator(r'^\d+(\.\d+)?$', 'Ingrese un número válido')],default="")
    modalidad = models.CharField("Modalidad:",max_length=15, choices=MODALIDADES,default="")
    nro_cuotas = models.IntegerField()
    nro_operacion = models.IntegerField(default=returnOperacion)
    agencia = models.CharField(default="", max_length=20, choices= AGENCIAS)

    cambioTitularidadField = models.JSONField(default=list,blank=True,null=True)
    # clientes_anteriores = models.ManyToManyField(Cliente, related_name='ventas_anteriores', blank=True)

    adjudicado = models.JSONField(default=dict)
    deBaja = models.JSONField(default=dict)
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
    cuotas = models.JSONField(default=list)


    def crearCuotas(self):
        cuotas = self.cuotas
        fechaDeVenta = datetime.datetime.now()
        contMeses = 0
        contYear = 0

        # if(self.adjudicado):
        #     fechaDeVenta =  fechaDeVenta  + relativedelta(months=+1)


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
        
        for i in range(1,self.nro_cuotas+1):
            fechaDeVenta =  fechaDeVenta + self.contarDiasSegunModalidad(self.modalidad)
            contMeses += 1
            cuotas.append({"cuota" :f'Cuota {i}',
                           "nro_operacion": self.nro_operacion,
                           "status": "Bloqueado",
                           "total": self.importe_x_cuota + (self.importe_x_cuota * (self.PORCENTAJE_ANUALIZADO *contYear))/100,
                           'pagado': 0,
                           'cobrador': "",
                           "fecha_pago": "", 
                           "hora": "", 
                           "metodoPago": "",
                           "descuento": 0,
                           "fechaDeVencimiento":f'{fechaDeVenta.strftime("%d-%m-%Y")}', 
                           "diasRetraso": 0,
                           "pagoParcial":{"status": False, "amount": []}
                           })
            if(contMeses == 12):
                contMeses = 0
                contYear +=1

            self.cuotas = cuotas


        if(self.adjudicado):
            for i in range(1,self.nro_cuotas+1):
                cuota = cuotas[i]
                cuota["interesPorMora"] = 0
                cuota["totalFinal"] = 0

        self.save()

    
    def contarDiasSegunModalidad(self,modalidad):
        hoy = datetime.datetime.now()  # Obtén la fecha actual
        modalidad = modalidad.lower()

        if modalidad == 'diario':
            dias_a_sumar = 1
        elif modalidad == 'semanal':
            dias_a_sumar = 7
        elif modalidad == 'quincenal':
            dias_acuotas_pagadas_sumar = 15
        elif modalidad == 'mensual':
            # Usa relativedelta para sumar un mes
            hoy_mas_un_mes = hoy + relativedelta(months=1)
            # Calcula la diferencia en días
            dias_a_sumar = (hoy_mas_un_mes - hoy).days
        else:
            raise ValueError("Modalidad no válida")

        fecha_resultado = relativedelta(days=dias_a_sumar)
        return fecha_resultado


    def createBaja(self):
        bajaField = self.deBaja
        bajaField["status"] = False
        bajaField["motivo"] = ""
        bajaField["detalleMotivo"] = ""
        bajaField["observacion"] = ""
        bajaField["responsable"] = ""
        self.deBaja = bajaField
        self.save()


    def createAdjudicado(self):
        adjuField = self.adjudicado
        adjuField["status"] = False
        adjuField["tipo"] = ""
        self.adjudicado = adjuField
        self.save()


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
                       "fecha": datetime.datetime.now().strftime("%d-%m-%Y"),
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
                       "fecha": datetime.datetime.now().strftime("%d-%m-%Y"),
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
            print("La operacion "+ str(self.pk) +" esta suspendida")
            self.suspendida = True
            self.save()
        elif(self.suspendida == True and contAtrasados==0):
            print("La operacion "+ str(self.pk)+" esta activa nuevamente")
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


    def desbloquearCuota(self,cuota):
        for i in range(0,int(self.nro_cuotas)):
            if (cuota == self.cuotas[i]["cuota"]):
                self.cuotas[i+1]["status"] = "Pendiente"
                break
        self.save()
        
    
    def pagoTotal(self,cuota,metodoPago,cobrador):

        cuotaSeleccionada = list(filter(lambda x:x["cuota"] == cuota,self.cuotas))
        if(cuotaSeleccionada[0]["status"] != "Pagado"):
            cuotaSeleccionada[0]["fecha_pago"] = datetime.datetime.now().strftime("%d-%m-%Y")
            cuotaSeleccionada[0]["status"] = "Pagado"
            cuotaSeleccionada[0]["pagado"] = cuotaSeleccionada[0]["total"] - cuotaSeleccionada[0]["descuento"]
            cuotaSeleccionada[0]["cobrador"] = cobrador
            cuotaSeleccionada[0]["hora"] = datetime.datetime.now().time().strftime("%H:%M")
            cuotaSeleccionada[0]["metodoPago"] = metodoPago
            self.desbloquearCuota(cuota)
            self.suspenderOperacion()
        else:
            raise ValueError("Esta cuota ya esta pagada")
        
        self.save()
                

    def pagoParcial(self,cuota,metodoPago,amount,cobrador):
        cuotaSeleccionada = list(filter(lambda x:x["cuota"] == cuota,self.cuotas))
        cuotaSeleccionada[0]["pagoParcial"]["status"]= True
        cuotaSeleccionada[0]["pagoParcial"]["amount"].append({"value": int(amount), 
                                                            "date":datetime.datetime.now().strftime("%d-%m-%Y"),
                                                            "hour": datetime.datetime.now().time().strftime("%H:%M"),
                                                            "metodo":metodoPago,
                                                            "cobrador": cobrador})
        
        valores_parciales = cuotaSeleccionada[0].get("pagoParcial", {}).get("amount", [])
        valores_parciales = [item["value"] for item in valores_parciales]
        sumaPagosParciales = sum(valores_parciales)
        cuotaSeleccionada[0]["pagado"] += sumaPagosParciales

            
        if((sumaPagosParciales + int(amount)) < cuotaSeleccionada[0]["total"] - cuotaSeleccionada[0]["descuento"]):
            cuotaSeleccionada[0]["status"] = "Parcial"
        elif(sumaPagosParciales == cuotaSeleccionada[0]["total"] - cuotaSeleccionada[0]["descuento"]):
            cuotaSeleccionada[0]["status"] = "Pagado"
            self.desbloquearCuota(cuota)
            self.suspenderOperacion()
            
        self.save()
            

    def aplicarDescuento(self,cuota,dinero):
        cuotaSeleccionada = list(filter(lambda x:x["cuota"] == cuota,self.cuotas))
        if(cuotaSeleccionada[0]["status"] != "Pagado" and (cuotaSeleccionada[0]["cuota"] == "Cuota 0" or cuotaSeleccionada[0]["cuota"] == "Cuota 1")):
            cuotaSeleccionada[0]["descuento"] += dinero
        else:
            raise ValueError("Solo se puede aplicar descuento a la cuota 0 y 1. En otro caso, esta cuota está pagada")
        self.save()


    def testVencimientoCuotas(self):
        initial = 1
        if(self.adjudicado["status"] == True):
            initial = 0

        for i in range(initial,int(self.nro_cuotas + initial)):
            cuota = self.cuotas[i]["fechaDeVencimiento"]
            if(datetime.datetime.now() > datetime.datetime.strptime(cuota,"%d-%m-%Y") and (self.cuotas[i]["status"] == "Pendiente" or self.cuotas[i]["status"] == "Bloqueado" )):
                self.cuotas[i]["status"] = "Atrasado"
                diasDeRetraso = self.contarDias(datetime.datetime.strptime(cuota,"%d-%m-%Y"))
                self.cuotas[i]["diasRetraso"] = diasDeRetraso
        self.save()


    def addPorcentajeAdjudicacion(self):
        NOW = datetime.datetime.now()
        INTERES = 0.01
        cuotas = self.cuotas

        initial = 1
        if(self.adjudicado["status"] == True):
            initial = 0

        for i in range(initial,int(self.nro_cuotas + initial)):
            fechaVencimiento = cuotas[i]["fechaDeVencimiento"]
            fechaVencimientoFormated = datetime.datetime.strptime(fechaVencimiento,"%d-%m-%Y")
            fechaInicioDeCuota = fechaVencimientoFormated + relativedelta(months=-1)
            
            if(NOW > fechaInicioDeCuota + relativedelta(days=+15)):
                cantidadDias = (NOW - (fechaInicioDeCuota + relativedelta(days=+15))).days
                cuotas[i]["interesPorMora"] = cantidadDias*INTERES
                cuotas[i]["totalFinal"] = cuotas[i]["total"]+(cuotas[i]["total"] * cuotas[i]["interesPorMora"])

            self.cuotas = cuotas
        self.save()


    def contarDias(self,fechaReferente):
        contadorDias = 0
        fechaHoy = datetime.datetime.now().strftime("%d-%m-%Y")
        while fechaReferente != datetime.datetime.strptime(fechaHoy,"%d-%m-%Y"):
            fechaReferente = fechaReferente + relativedelta(days=1)
            contadorDias += 1
        return contadorDias

