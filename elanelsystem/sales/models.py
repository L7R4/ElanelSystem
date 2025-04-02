import re
from django.db import models
from django.forms import ValidationError
from users.models import Cliente,Usuario,Sucursal
from products.models import Plan, Products
from django.core.validators import RegexValidator
import json
import datetime
from dateutil.relativedelta import relativedelta
from sales.utils import getAllCampaniaOfYear, getCampaniaActual, getCampaniaByFecha, obtener_ultima_campania
from django.core.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

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
        fechaDeAlta = None
    
        fechaDeAlta = datetime.datetime.strptime(self.fecha, '%d/%m/%Y %H:%M')
            
        # Setear la variable fechaDeVencimiento con un tipo fecha
        fechaDeVencimiento = fechaDeAlta
        contMeses = 0
        contYear = 0

        # Cuota 0
        cuotas.append({"cuota" :f'Cuota 0',
                       "nro_operacion": self.nro_operacion,
                       "status": "pendiente",
                       "total": int(self.anticipo),
                       "descuento": {'autorizado': "", 'monto': 0},
                       "bloqueada": True,
                       "fechaDeVencimiento":"", 
                       "diasRetraso": 0,
                       "pagos":[],
                       "autorizada_para_anular": False

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
                    "status": "pendiente",
                    "bloqueada": True,
                    "fechaDeVencimiento" : fechaDeVencimiento.strftime('%d/%m/%Y %H:%M'),
                    "descuento": {'autorizado': "", 'monto': 0},
                    "diasRetraso": 0,
                    "interesPorMora": 0,
                    "campaniaCuota":getCampaniaByFecha(fechaDeVencimiento),
                    "totalFinal": 0,
                    "pagos":[],
                    "autorizada_para_anular": False
                })
            
            if(cuotas[-1]["cuota"] == "Cuota 1"):
               cuotas[-1]["total"]= int(self.primer_cuota)
            else:
               cuotas[-1]["total"]= int(self.importe_x_cuota + (self.importe_x_cuota * (self.PORCENTAJE_ANUALIZADO *contYear))/100)
                


            if(contMeses == 12):
                contMeses = 0
                contYear +=1


        # Me aseguro de que no importa si es adjudicado o no la primera cuota a pagar este desbloqueada
        cuotas[0]["bloqueada"] = False

        self.cuotas = cuotas
        # self.save()
    
    # Modalidades de tiempo de pago
    MODALIDADES = (
        ('Diario', 'Diario'),
        ('Semanal', 'Semanal'),
        ('Quincenal', 'Quincenal'),
        ('Mensual', 'Mensual'),
    )
    
    PORCENTAJE_ANUALIZADO = 15
    
    
    
    #region Campos
    nro_cliente = models.ForeignKey(Cliente,on_delete=models.CASCADE,related_name="ventas_nro_cliente")
    modalidad = models.CharField("Modalidad:",max_length=15, choices=MODALIDADES,default="")
    nro_cuotas = models.IntegerField()
    nro_operacion = models.IntegerField(default=returnOperacion)
    agencia = models.ForeignKey(Sucursal, on_delete=models.DO_NOTHING,blank = True, null = True)
    campania = models.CharField("Campaña:",max_length=50,default="")
    
    suspendida = models.BooleanField(default=False)
    importe = models.FloatField("Importe:",default=0)
    tasa_interes = models.FloatField("Tasa de Interes:",default=0)
    primer_cuota =models.FloatField("Primer cuota:",default=0)
    anticipo =models.IntegerField("Cuota de Inscripcion:",default=0)
    intereses_generados = models.FloatField("Intereses Gen:",default=0)
    importe_x_cuota = models.FloatField("Importe x Cuota:",default=0)
    total_a_pagar = models.FloatField("Total a pagar:",default=0)
    fecha = models.CharField("Fecha:", max_length=30,default="")
    producto = models.ForeignKey(Products,on_delete=models.CASCADE,related_name="ventas_producto",default="")
    paquete = models.CharField(max_length=20,default="")
    vendedor = models.ForeignKey(Usuario,on_delete=models.CASCADE,related_name="ventas_ven_usuario",default="",blank=True,null=True)
    supervisor = models.ForeignKey(Usuario,on_delete=models.CASCADE,related_name="venta_super_usuario",default="",blank=True,null=True)
    observaciones = models.CharField("Obeservaciones:",max_length=255,blank=True,null=True)
    cantidadContratos = models.JSONField("Chances", default=list, blank=True, null=True)

    cambioTitularidadField = models.JSONField(default=list,blank=True,null=True)
    auditoria = models.JSONField(default=list,blank=True,null=True)
    adjudicado = models.JSONField(default=dict,blank=True,null=True)
    deBaja = models.JSONField(default=dict,blank=True,null=True)
    cuotas = models.JSONField(default=list,blank=True,null=True)
    #endregion
    


    #region Validaciones
    def clean(self):
        errors = {}
        validation_methods = [
            self.validation_modalidad,
            self.validation_total_a_pagar,
            self.validation_importe,
            self.validation_importe_x_cuota,
            self.validation_tasa_interes,
            self.validation_intereses_generados,
            self.validation_anticipo,
            self.validation_primer_cuota,
            # self.validation_fecha,
            self.validation_paquete,
            self.validation_campania,
            # self.validation_nro_operacion   
        ]

        for method in validation_methods:
            try:
                method()
            except ValidationError as e:
                errors.update(e.message_dict)

        if errors:
            raise ValidationError(errors)


    def validation_nro_operacion(self):
        lastOperacion = Ventas.objects.last().nro_operacion
        if not self.adjudicado["status"]:
            if(self.nro_operacion != lastOperacion+1):
                raise ValidationError({'nro_operacion': "Número de operacion incorrecto."})


    def validation_modalidad(self):
        if self.modalidad:
            if self.modalidad not in [m[0] for m in self.MODALIDADES]:
                raise ValidationError({'modalidad': 'Modalidad no válida.'}) 

    def validation_primer_cuota(self):
        if not self.adjudicado["status"]:
            if self.primer_cuota <= 0:
                raise ValidationError({'primer_cuota': 'Dinero invalido. Debe ser mayor a 0.'})
    
    def validation_anticipo(self):
        if not self.adjudicado["status"]:
            if self.anticipo <= 0:
                raise ValidationError({'anticipo': 'Dinero invalido. Debe ser mayor a 0.'})
            
    def validation_total_a_pagar(self):
        if not self.adjudicado["status"]:
            if self.total_a_pagar <= 0:
                raise ValidationError({'total_a_pagar': 'Dinero invalido. Debe ser mayor a 0.'})
        else:
            if self.total_a_pagar < 0:
                raise ValidationError({'total_a_pagar': 'Dinero invalido.'})
      
    def validation_importe(self):
        if not self.adjudicado["status"]:
            if self.importe <= 0:
                raise ValidationError({'importe': 'Dinero invalido. Debe ser mayor a 0.'})
        else:
            if self.importe < 0:
                raise ValidationError({'importe': 'Dinero invalido.'})
    
    def validation_intereses_generados(self):
        if not self.adjudicado["status"]:
            if self.intereses_generados <= 0:
                raise ValidationError({'intereses_generados': 'Dinero invalido. Debe ser mayor a 0.'})
        else:
            if self.intereses_generados < 0:
                raise ValidationError({'intereses_generados': 'Dinero invalido.'})
        
    def validation_importe_x_cuota(self):
        if not self.adjudicado["status"]:
            if self.importe_x_cuota <= 0:
                raise ValidationError({'importe_x_cuota': 'Dinero invalido. Debe ser mayor a 0.'})
        else:
            if self.importe_x_cuota < 0:
                raise ValidationError({'importe_x_cuota': 'Dinero invalido.'})
        
    def validation_tasa_interes(self):
        if self.tasa_interes < 0:
            raise ValidationError({'tasa_interes': 'Tasa de interes invalida.'})
        
    def validation_fecha(self):
        if self.fecha:
            if self.fecha and not re.match(r'^\d{2}/\d{2}/\d{4}$', self.fecha):
                raise ValidationError({'fecha': 'Debe estar en el formato DD/MM/AAAA.'})

            try:
                fecha = datetime.datetime.strptime(self.fecha, '%d/%m/%Y')
            except ValueError:
                raise ValidationError({'fecha': 'Fecha inválida.'})

            fecha = datetime.datetime.strptime(self.fecha, '%d/%m/%Y')
            if fecha > datetime.datetime.now():
                raise ValidationError({'fecha': 'Fecha inválida.'})
            self.fecha = self.fecha + " " + datetime.datetime.now().strftime("%H:%M")

    def validation_paquete(self):
        paquetes = Plan.TIPO_PLAN_CHOICES
        if self.paquete not in [m[0] for m in paquetes]:
            raise ValidationError({'paquete': 'Paquete no válido.'})
        
    def validation_campania(self):
        campaniasDelAño = getAllCampaniaOfYear()
        campaniaActual = getCampaniaActual()
        campaniaAnterior = campaniasDelAño[campaniasDelAño.index(campaniaActual) - 1]

        fechaActual = datetime.datetime.now()
        ultimo_dia_mes_pasado = datetime.datetime.now().replace(day=1) - relativedelta(days=1)
        diferencia_dias = (fechaActual - ultimo_dia_mes_pasado).days

        if(self.campania == campaniaAnterior):
            if(diferencia_dias > 5): # Si la diferencia de dias es mayor a 3 dias, no se puede asignar la campania porque ya paso el tiempo limite para dar de alta una venta en la campania anterior
                raise ValidationError({'campania': 'Campaña no válida.'})
        elif(self.campania != campaniaActual):
            raise ValidationError({'campania': 'Campaña no válida.'})

    #endregion


    def setDefaultFields(self):
        self.adjudicado ={
            "status" : False,
            "tipo" : "",
            "autorizado_por": "",
            "contratoAdjudicado": "",
        }
        # self.auditoria =[{
        #     "version":0,
        #     "realizada":False,
        #     "grade":False,
        #     "comentarios":"",
        #     "fecha_hora": "",
        # }]
        self.deBaja ={
            "status" : False,
            "motivo" : "",
            "detalleMotivo" : "",
            "observacion" : "",
            "responsable" : "",
            "nuevaVentaPK": ""
        }


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
                       "fecha": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
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
                       "fecha": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                       "user": user,
                       "oldCustomer":oldCustomer,
                       "pkOldCustomer": pkOldCustomer,
                       "newCustomer":newCustomer,
                       "pkNewCustomer": pkNewCustomer

                    })
        
        # self.save()


    def cuotas_pagadas(self):
        try:
            cuotas = [cuota for cuota in self.cuotas if cuota["status"].lower() == "pagado"]
            if(cuotas[0]["cuota"] == "Cuota 0"):
                cuotas.pop(0)
            return cuotas
        except IndexError as e:
            return []

    def cuotas_parciales(self):
        try:
            cuotas = [cuota for cuota in self.cuotas if cuota["status"].lower() == "parcial"]
            if(cuotas[0]["cuota"] == "Cuota 0"):
                cuotas.pop(0)
            return cuotas
        except IndexError as e:
            return []
    
    
    def darBaja(self,motivo,porcentaje,detalleMotivo,observacion,responsable):
        self.deBaja["status"] = True
        self.deBaja["motivo"] = motivo
        self.deBaja["porcentaje"] = porcentaje
        self.deBaja["observacion"] = observacion
        self.deBaja["detalleMotivo"] = detalleMotivo
        self.deBaja["responsable"] = responsable
        self.deBaja["fecha"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        # self.save()
        

    def planRecupero(self,motivo,responsable,observacion,nuevaVentaPK):
        self.deBaja["status"] = True
        self.deBaja["motivo"] = motivo
        self.deBaja["observacion"] = observacion
        self.deBaja["responsable"] = responsable
        self.deBaja["fecha"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        self.deBaja["nuevaVentaPK"] = nuevaVentaPK
    

    def porcentajeADevolver(self):
        porcentageValido = 0
        if len(self.cuotas_pagadas()) >= 6:
            porcentageValido = 50
        else:
            porcentageValido = 0
        return porcentageValido


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

        cuotas = self.cuotas
        contAtrasados = 0
        
        for i in range(0,len(cuotas)):
            if(cuotas[i]["status"].lower() == "vencido"):
                contAtrasados +=1
        if contAtrasados >=4:
            self.darBaja("falta de pago",0,"Operacion de baja por extenderse 120 dias o mas sin abonar","","")
            self.suspendida = True
            self.save()
        if contAtrasados >= 3:
            self.suspendida = True
            self.save()
        elif(self.suspendida == True and contAtrasados==0):
            self.suspendida = False
            self.save()
    

    def acreditarCuotasPorAnticipo(self, dineroAFavor,responsable):
        cantidad_cuotas = len(self.cuotas) - 1
        print(f'Cantidad de cuotas desde la funcion acreditar: {cantidad_cuotas}')
            # Un for que reccorra de la ultima cuota hasta la cuota 1
        for i in range(cantidad_cuotas,0,-1):
            cuota = self.cuotas[i]
            if dineroAFavor >= cuota["total"]:
                cuota["bloqueada"] = False # Desbloquea la cuota para que se pueda pagar
                self.pagarCuota(cuota["cuota"],cuota["total"],"Credito","",responsable)
                dineroAFavor -= cuota["total"]
            elif dineroAFavor > 0:
                cuota["bloqueada"] = False # Desbloquea la cuota para que se pueda pagar
                self.pagarCuota(cuota["cuota"],dineroAFavor,"Credito","",responsable)
                cuota["bloqueada"] = True # Se vuelve a bloquear la cuota para que no se pueda acceder hasta que haya completado las cuotas anteriores
                dineroAFavor = 0
            else:
                break

        
    def crearAdjudicacion(self,contratoAdjudicado,nroDeVenta,tipo):
        self.cuotas.pop(0) # Elimina la cuota 0
        self.cuotas[0]["status"] = "pendiente" # Cambia el status de la cuota 1 a Pendiente
        self.cuotas[0]["bloqueada"] = False

        self.nro_operacion = nroDeVenta
        self.adjudicado["contratoAdjudicado"] = contratoAdjudicado
        self.adjudicado["status"] = True
        self.adjudicado["tipo"] = tipo

        # self.save()


    #region CuotasManagement
    def desbloquearCuota(self,cuota):
        print(f'Cantidad de cuotas desde la funcion desbloquearCuota {len(self.cuotas)}')
        for i in range(0,int(self.nro_cuotas)):
            if (cuota == self.cuotas[i]["cuota"]):
                self.cuotas[i+1]["bloqueada"] = False
                break
        self.save()
        

    def pagarCuota(self,cuota,monto,metodoPago,cobrador,responsable_pago):
        pago = {}

        cuotaSeleccionada = list(filter(lambda x:x["cuota"] == cuota,self.cuotas))[0]

        if(cuotaSeleccionada["status"].lower() != "pagado" and not cuotaSeleccionada["bloqueada"]):
            pago = {
                "monto": monto,
                "metodoPago": metodoPago,
                "fecha": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                "cobrador": cobrador,
                "responsable_pago": responsable_pago,
                "campaniaPago": getCampaniaActual()
            }
            cuotaSeleccionada["pagos"].append(pago)
            lista_montoDePagos = [item["monto"] for item in cuotaSeleccionada["pagos"]]

            sumaPagos = sum(lista_montoDePagos)

            if sumaPagos == (cuotaSeleccionada["total"] - cuotaSeleccionada["descuento"]["monto"]):
                cuotaSeleccionada["status"] = "pagado"
                self.desbloquearCuota(cuota)
                self.suspenderOperacion()
            else:
                cuotaSeleccionada["status"] = "parcial"

            self.save()

        else:
            raise ValueError("Esta cuota ya esta pagada o esta bloqueada")


    def anularCuota(self,cuotaRequest):
        for cuota in self.cuotas:
            if cuota["cuota"] == cuotaRequest:
                cuota["pagos"] = [pago for pago in cuota["pagos"] if pago["metodoPago"] == "Credito"] # Elimina los pagos realizados pero deja los saldo a favor en la cuota
                
                # Luego de limpiar unicamente los pagos que no son de credito se evalua que no haya ninguno pago por credito en la cuota, 
                # entonces significara se podra colocar el estado de Pendiente, porque no se ha pagado ni parcial ni completamente,
                # sino tendria que mantener su estado actual
                if(len(cuota["pagos"]) == 0): 
                    cuota["status"] = "pendiente"
                    
                cuota["pagos"] = []  # Agregar un flag en la cuota
                cuota["status"] = "pendiente"
                cuota["autorizada_para_anular"] = False

                # Obtenemos la siguiente cuota y la bloqueamos
                cuotaSiguiente = self.cuotas[self.cuotas.index(cuota)+1]
                cuotaSiguiente["bloqueada"] = True
                break

        self.save()


    def aplicarDescuento(self,cuota,dinero,autorizado):
        cuotaSeleccionada = list(filter(lambda x:x["cuota"] == cuota,self.cuotas))[0]
        if(cuotaSeleccionada["status"].lower() != "pagado" and (cuotaSeleccionada["cuota"] == "Cuota 0" or cuotaSeleccionada["cuota"] == "Cuota 1")):
            cuotaSeleccionada["descuento"]['monto'] += dinero
            cuotaSeleccionada["descuento"]['autorizado'] = autorizado
        else:
            raise ValueError("Solo se puede aplicar descuento a la cuota 0 y 1. En otro caso, esta cuota está pagada")
        self.save()


    def testVencimientoCuotas(self):

        for i in range(0, len(self.cuotas)):
            cuota = self.cuotas[i]["fechaDeVencimiento"]
            if self.cuotas[i]["cuota"] != "Cuota 0":
                fechaVencimiento = datetime.datetime.strptime(cuota, "%d/%m/%Y %H:%M")
                fechaActual = datetime.datetime.now()

                if fechaActual > fechaVencimiento and not self.cuotas[i]['status'].lower() == "pagado":
                    self.cuotas[i]["status"] = "vencido"
                    diasDeRetraso = self.contarDias(fechaVencimiento)
                    print(f'La cuota {self.cuotas[i]["cuota"]} esta vencida por {diasDeRetraso} dias')
                    self.cuotas[i]["diasRetraso"] = diasDeRetraso

        self.save()
    #endregion

    def addPorcentajeAdjudicacion(self):
        NOW = datetime.datetime.now()
        INTERES = 0.01
        cuotas = self.cuotas

        for i in range(0,len(self.cuotas)):
            fechaVencimiento = cuotas[i]["fechaDeVencimiento"]
            if self.cuotas[i]["cuota"] != "Cuota 0":
                fechaVencimientoFormated = datetime.datetime.strptime(fechaVencimiento,"%d/%m/%Y %H:%M")
                fechaInicioDeCuota = fechaVencimientoFormated + relativedelta(months=-1)
                
                if(NOW > fechaInicioDeCuota + relativedelta(days=+15)):
                    cantidadDias = (NOW - (fechaInicioDeCuota + relativedelta(days=+15))).days
                    cuotas[i]["interesPorMora"] = cantidadDias*INTERES
                    cuotas[i]["totalFinal"] = cuotas[i]["total"]+(cuotas[i]["total"] * cuotas[i]["interesPorMora"])

            self.cuotas = cuotas
        self.save()


    def contarDias(self,fechaReferente):
        fechaHoy = datetime.datetime.now()
        diferencia = fechaHoy - fechaReferente
        return diferencia.days


class CuentaCobranza(models.Model):
    alias = models.CharField("Alias:",max_length=50)

    def __str__(self):
        return self.alias
    
    def save(self, *args, **kwargs):
        self.alias = self.alias.capitalize()

        super(CuentaCobranza, self).save(*args, **kwargs)
    
    #region Validaciones
    def clean(self):
        errors = {}
        validation_methods = [
            self.validation_alias    
        ]

        for method in validation_methods:
            try:
                method()
            except ValidationError as e:
                errors.update(e.message_dict)

        if errors:
            raise ValidationError(errors)
    

    def validation_alias(self):
        if CuentaCobranza.objects.filter(alias=self.alias).exists():
            raise ValidationError({'alias': "Ya existe una cuenta con ese alias."})
    #endregion       

class MetodoPago(models.Model):
    alias = models.CharField("Alias:",max_length=50)

    def __str__(self):
        return self.alias
    
    def save(self, *args, **kwargs):
        self.alias = self.alias.capitalize()

        super(MetodoPago, self).save(*args, **kwargs)
    
    #region Validacioness
    def clean(self):
        errors = {}
        validation_methods = [
            self.validation_alias    
        ]

        for method in validation_methods:
            try:
                method()
            except ValidationError as e:
                errors.update(e.message_dict)

        if errors:
            raise ValidationError(errors)
    

    def validation_alias(self):
        if MetodoPago.objects.filter(alias=self.alias).exists():
            raise ValidationError({'alias': "Ya existe un metodo de pago con ese alias."})
    #endregion       

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
    movimiento = models.CharField("Movimiento:",max_length=8)
    dinero = models.FloatField("Dinero:")
    metodoPago = models.ForeignKey(MetodoPago,on_delete=models.SET_NULL,related_name="metodo_movs", null=True)
    agencia = models.ForeignKey(Sucursal, on_delete=models.SET_NULL, related_name="agencia_movs", null=True)
    ente = models.ForeignKey(CuentaCobranza, on_delete=models.SET_NULL, related_name="ente_movs", null=True)

    fecha = models.CharField("Fecha:",max_length=16)
    campania = models.CharField("Campaña:",max_length=30)
    concepto = models.CharField("Concepto:",max_length=200)
    premio = models.BooleanField("Premio:", default=False)
    adelanto = models.BooleanField("Adelanto:",default=False)
    observaciones = models.TextField("Observaciones:",blank=True,null=True)


    def clean(self):
        cleaned_data = super().clean()
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