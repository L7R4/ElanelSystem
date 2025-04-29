import re
from django.db import models
from django.forms import ValidationError
# from elanelsystem.utils import obtenerCampaña_atraves_fecha
from users.models import Cliente,Usuario,Sucursal
from products.models import Plan, Products
from django.core.validators import RegexValidator
import json
import datetime
from elanelsystem.utils import obtenerCampaña_atraves_fecha
from django.db import models, connection
from django.db.models import Max
from django.db import transaction
from django.db.models import Sum

from dateutil.relativedelta import relativedelta
from sales.utils import getAllCampaniaOfYear, getCampaniaActual
from django.core.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone

#region C-LISTA-PRECIOS
class CoeficientesListadePrecios(models.Model):
    valor_nominal = models.IntegerField("Valor Nominal:")
    cuota = models.IntegerField("Cuotas:")
    porcentage = models.FloatField("Porcentage:")
#endregion

#region VENTAS
class Ventas(models.Model):

    # Funcion para el siguiente numero de operacion automaticamente
    
    def get_next_operacion():
        """
        Devuelve el siguiente nro_operacion como MAX(nro_operacion)+1,
        o 1 si aún no hay ventas.
        """
        max_n = Ventas.objects.aggregate(
            max_op=Max('nro_operacion')
        )['max_op'] or 0
        return max_n + 1

    def _siguiente_fecha_venc(self, fecha_base, index):
        """Calcula la fecha de vencimiento para la cuota `index`."""
        if self.modalidad == 'Mensual':
            if index == 1:
                dia = 15
                meses = 1 if fecha_base.day <= 25 else 2
                return fecha_base.replace(day=dia) + relativedelta(months=meses)
            return fecha_base + relativedelta(months=1)
        elif self.modalidad == 'Quincenal':
            return fecha_base + relativedelta(days=15)
        elif self.modalidad == 'Semanal':
            return fecha_base + relativedelta(days=7)
        elif self.modalidad == 'Diario':
            return fecha_base + relativedelta(days=1)
        else:
            raise ValueError(f"Modalidad desconocida: {self.modalidad}")
                             
    def _calcular_total_oficial(self, index):
        """Devuelve el total oficial de la cuota `index`, incluyendo interés."""
        if index == 0:
            return int(self.anticipo)
        if index == 1:
            return int(self.primer_cuota)
        # Cuotas 2+ con interés anualizado
        years = (index - 1) // 12
        base = self.importe_x_cuota
        interes = base * (self.PORCENTAJE_ANUALIZADO * years) / 100
        return int(base + interes)
     
    def crearCuotas(self):
        """Inicializa la lista `self.cuotas` con la cuota 0 y las siguientes."""
        fecha_alta = datetime.datetime.strptime(self.fecha, '%d/%m/%Y %H:%M')
        cuotas = []

        # Anticipo (Cuota 0)
        cuota0 = self._armar_cuota(0, fecha_alta)
        cuota0['bloqueada'] = False
        cuotas.append(cuota0)

        # Cuotas 1..n
        fecha_iter = fecha_alta
        for i in range(1, self.nro_cuotas + 1):
            fecha_iter = self._siguiente_fecha_venc(fecha_iter, i)
            cuotas.append(self._armar_cuota(i, fecha_iter))

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
    
    
    #region Campos
    nro_cliente = models.ForeignKey(Cliente,on_delete=models.CASCADE,related_name="ventas_nro_cliente")
    modalidad = models.CharField("Modalidad:",max_length=15, choices=MODALIDADES,default="")
    nro_cuotas = models.IntegerField()
    nro_operacion = models.IntegerField(default=get_next_operacion)
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
    adjudicado = models.JSONField(default=dict,blank=True,null=True)
    deBaja = models.JSONField(default=dict,blank=True,null=True)
    cuotas = models.JSONField(default=list,blank=True,null=True)
    #endregion
    
    def __str__(self):
        return f"Venta N° {self.nro_operacion}"


    #region Validaciones
    def clean(self):
        errors = {}
        validation_methods = [
            # self.validation_modalidad,
            # self.validation_total_a_pagar,
            # self.validation_importe,
            # self.validation_importe_x_cuota,
            # self.validation_tasa_interes,
            # self.validation_intereses_generados,
            # self.validation_anticipo,
            # self.validation_primer_cuota,
            # # self.validation_fecha,
            # # self.validation_paquete,
            # self.validation_campania,
            # # self.validation_nro_operacion   
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
        for i in range(0,int(self.nro_cuotas)):
            if (cuota == self.cuotas[i]["cuota"]):
                self.cuotas[i+1]["bloqueada"] = False
                break
        self.save()
        
    def _get_cuota_dict(self, nro_cuota: int):
        """
        Devuelve la dict de la cuota con número `nro_cuota`
        (donde c['cuota']=='Cuota {nro_cuota}'), o None.
        """
        for c in self.cuotas:
            if int(c['cuota'].split()[-1]) == nro_cuota:
                return c
        return None

    def actualizar_estado_cuota(self, nro_cuota: int):
        """
        Reconstruye el estado de la cuota nro_cuota a partir
        de los registros de PagoCannon, guarda sólo IDs en
        c['pagos'], y desbloquea la siguiente si corresponde.
        """
        from .models import PagoCannon

        cuota = self._get_cuota_dict(nro_cuota)
        if not cuota:
            return

        # 1) sumar todos los pagos de esa cuota
        pagos_qs    = PagoCannon.objects.filter(venta=self, nro_cuota=nro_cuota)
        total_pagos = pagos_qs.aggregate(total=models.Sum('monto'))['total'] or 0

        # 2) actualizar lista de pagos (solo IDs)
        cuota['pagos'] = list(pagos_qs.values_list('id', flat=True))

        # 3) decidir estado según monto pagado vs objetivo
        objetivo = cuota['total'] - cuota['descuento']['monto']
        if total_pagos >= objetivo:
            cuota['status'] = 'Pagado'
            # desbloquear siguiente
            self.desbloquearCuota(cuota['cuota'])
        elif total_pagos > 0:
            cuota['status'] = 'Parcial'
        else:
            cuota['status'] = 'Pendiente'

    def sync_estado_cuotas(self):
        """
        Recorre todas las cuotas de self.cuotas y llama
        a actualizar_estado_cuota() para cada una.
        Luego aplica vencimientos y suspensión.
        """
        for c in self.cuotas:
            nro = int(c['cuota'].split()[-1])
            self.actualizar_estado_cuota(nro)

        self.testVencimientoCuotas()
        self.suspenderOperacion()
    
    def pagarCuota(self,nro_cuota,monto,metodoPago,cobrador,responsable_pago):

        # 1) Obtener el dict de esa cuota en self.cuotas
        cuota_label = f"Cuota {nro_cuota}"
        cuota = next((c for c in self.cuotas if c["cuota"] == cuota_label), None)

        if not cuota:
            raise ValueError(f"No existe {cuota_label} en esta venta.")
        if cuota["status"].lower() == "pagado" or cuota["bloqueada"]:
            raise ValueError("La cuota ya está pagada o bloqueada.")
        
        # 2) Crear el PagoCannon de forma atómica
        with transaction.atomic():
            pago = PagoCannon(
                venta            = self,
                nro_cuota        = nro_cuota,
                monto            = monto,
                metodo_pago      = metodoPago,
                cobrador         = cobrador,
                responsable_pago = responsable_pago,
            )
            pago.save()  # aquí se genera el nro_recibo y campana_de_pago

            # 3) Referenciar el pago en el JSON
            cuota.setdefault("pagos", []).append(pago.id)

        # 4) Recalcular total abonado y estado
        total_pagado = (
            PagoCannon.objects
            .filter(venta=self, nro_cuota=nro_cuota)
            .aggregate(total=Sum('monto'))['total'] or 0
        )
        objetivo = cuota['total'] - cuota['descuento']['monto']
        if total_pagado >= objetivo:
            cuota['status'] = 'Pagado'
            self.desbloquearCuota(cuota_label)
            self.suspenderOperacion()
        elif total_pagado > 0:
            cuota['status'] = 'Parcial'

        self.save()

    def anularCuota(self, nro_cuota):
        """
        Elimina todos los pagos de la cuota indicada y resetea su estado.
        """
        cuota_label = f"Cuota {nro_cuota}"
        cuota = next((c for c in self.cuotas if c["cuota"] == cuota_label), None)
        if not cuota:
            raise ValueError(f"No existe {cuota_label} en esta venta.")

        # 1) Borrar de la base los PagoCannon asociados
        PagoCannon.objects.filter(venta=self, nro_cuota=nro_cuota).delete()

        # 2) Limpiar el JSON y bloquear la siguiente
        cuota["pagos"] = []
        cuota["status"] = "Pendiente"
        cuota["autorizada_para_anular"] = False

        idx = self.cuotas.index(cuota)
        if idx + 1 < len(self.cuotas):
            self.cuotas[idx+1]["bloqueada"] = True

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


class PagoCannon(models.Model):
    

    def now_formatted():
        return timezone.now().strftime("%d/%m/%Y %H:%M")

    nro_recibo = models.CharField(
        "N° de comprobante",
        max_length=30,
        unique=True,
        help_text="Número de recibo o comprobante, debe ser único por pago."
    )

    venta = models.ForeignKey(
        'Ventas',
        on_delete=models.CASCADE,
        related_name='pagos_cannon',
        help_text="Venta a la que pertenece este pago."
    )

    nro_cuota = models.PositiveSmallIntegerField(
        "N° de cuota",
        validators=[MinValueValidator(0)],
        help_text="Cuota a la que aplica este pago (0 = inscripción)."
    )

    fecha = models.CharField(
        "Fecha de pago",
        default=now_formatted,
        max_length=30,
        help_text="Fecha y hora en que se registró el pago."
    )

    campana_de_pago = models.CharField(
        "Campaña de pago",
        max_length=30,
        blank=True,
        help_text="Ej. 'Marzo 2025'. Se calcula en el save()."
    )

    monto = models.PositiveIntegerField(
        "Monto",
        validators=[MinValueValidator(1)],
        help_text="Importe entero del pago, mayor a cero."
    )

    metodo_pago = models.ForeignKey(
        'MetodoPago',
        on_delete=models.SET_NULL,
        related_name='pagos_cannon',
        null=True,
        blank=True,
        help_text="Método de pago utilizado."
    )

    cobrador = models.ForeignKey(
        'CuentaCobranza',
        on_delete=models.SET_NULL,
        related_name='pagos_cannon',
        null=True,
        blank=True,
        help_text="Cuenta o persona que cobra."
    )

    responsable_pago = models.ForeignKey(
        'users.Usuario',
        on_delete=models.SET_NULL,
        related_name='pagos_realizados',
        null=True,
        blank=True,
        help_text="Usuario interno responsable de la carga."
    )

    class Meta:
        ordering = ['-fecha']
        unique_together = [
            ('venta', 'nro_cuota', 'nro_recibo')
        ]
        indexes = [
            models.Index(fields=['venta', 'nro_cuota']),
        ]
        verbose_name = "Pago Cannon"
        verbose_name_plural = "Pagos Cannon"

    def clean(self):
        # 1) Asegurarse de que la cuota exista en la venta
        if self.nro_cuota > self.venta.nro_cuotas:
            from django.core.exceptions import ValidationError
            raise ValidationError({
                'nro_cuota': f"Esta venta tiene solo {self.venta.nro_cuotas} cuotas."
            })

    def save(self, *args, **kwargs):
        # si no vino explícito, lo genero aquí
        if not self.campana_de_pago:
            self.campana_de_pago = obtenerCampaña_atraves_fecha(self.fecha)


        # PostgreSQL tiene un objeto nativo para esto: las sequences. Básicamente, un contador 
        # independiente que puedes invocar con nextval() y que está diseñado para altos volúmenes 
        # y concurrencia.
        if not self.nro_recibo:
            with connection.cursor() as cursor:
                cursor.execute("SELECT nextval('recibo_seq')")
                next_num = cursor.fetchone()[0]
            # formatea a tu gusto, p.e. RC-000001
            self.nro_recibo = f"RC-{next_num:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nro_recibo} – Venta {self.venta.nro_operacion} / Cuota {self.nro_cuota}"
    

class Auditoria(models.Model):
    MOTIVO_CHOICES = (
        ("Motivos personales", "Motivos personales"),
        ("Arrepentimiento", "Arrepentimiento"),
        ("Falta de conocimiento sobre el contrato", "Falta de conocimiento sobre el contrato"),
    )

    def now_formatted():
        return timezone.now().strftime("%d/%m/%Y %H:%M")


    venta = models.ForeignKey(
        'Ventas',
        on_delete=models.CASCADE,
        related_name='auditorias',
        help_text="Venta a la que corresponde este registro de auditoría."
    )
    
    version = models.PositiveIntegerField(
        default=1,
        help_text="Número incremental de la auditoría."
    )

    grade = models.BooleanField(
        default=False,
        help_text="False: Si no aprobo | True: Si aprobo."
    )

    reintegro_dinero = models.BooleanField(
        default=False,
        help_text="Si se reintegro dinero."
    )

    motivo = models.CharField(
        max_length=255,
        choices=MOTIVO_CHOICES,
        blank=True,
        help_text="Motivo de la auditoría.",
        null = True
    )

    comentarios = models.TextField(
        blank=True,
        help_text="Comentarios de la auditoría.",
        null=True
    )

    fecha_hora = models.CharField(
        max_length=20,
        default=now_formatted,
        help_text="Fecha y hora en que se creó este registro."
    )

    class Meta:
        unique_together = [('venta', 'version')]
        ordering = ['venta', 'version']

    def clean(self):
        super().clean()
        # Si no aprobó la auditoría, motivo es obligatorio
        if not self.graded and not self.motivo:
            raise ValidationError({
                'motivo': "Debe informar un motivo cuando la auditoría no ha sido aprobada."
            })

    def __str__(self):
        status = "Aprobada" if self.graded else "Rechazada"
        return f"Auditoría v{self.version} – Venta {self.venta.nro_operacion} ({status})"
    
