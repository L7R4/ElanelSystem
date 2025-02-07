from django.db import models
from users.models import Usuario,Sucursal
from sales.models import Ventas
from django.forms import ValidationError

from datetime import datetime
# from .utils import coeficienteCantidadOrdenadoVendedor, coeficienteProductividadOrdenadoVendedor,getDetalleComisionPorCantVentasPropias,getPremioProductividadVentasPropias,getAusenciasTardanzas,getAdelantos,getAsegurado,calcular_ventas,calcular_productividad

class MontoTardanzaAusencia(models.Model):
    monto_tardanza = models.DecimalField(max_digits=6, decimal_places=2, default=350.00)
    monto_ausencia = models.DecimalField(max_digits=6, decimal_places=2, default=2000.00)
    margen_tiempo = models.IntegerField(default=15)  # Ejemplo: 15 minutos

    # class Meta:
    #     verbose_name = "Monto para tardanza y ausencia"
    #     verbose_name_plural = "Montos para tardanzas y ausencias"

    def save(self, *args, **kwargs):
        # Asegurar que solo exista una instancia
        if not self.pk and MontoTardanzaAusencia.objects.exists():
            raise ValidationError("Solo puede existir una instancia de 'Monto para tardanza y ausencia'.")
        super().save(*args, **kwargs)

    @staticmethod
    def get_solo():
        # Obtener la instancia única
        configuracion, created = MontoTardanzaAusencia.objects.get_or_create()
        return configuracion

class Asegurado(models.Model):
    dinero = models.IntegerField("Dinero")
    dirigido = models.CharField("Dirigido", max_length=80)
    objetivo = models.IntegerField("Objetivo", default=0)

    def __str__(self):
        return str(self.dinero) + "--" + str(self.dirigido) + "--" + str(self.objetivo)


class CoeficientePorCantidadSupervisor(models.Model):
    cantidad_minima = models.IntegerField("Cantidad minima", default = 0)
    cantidad_maxima = models.IntegerField("Cantidad maxima", default = 0)
    coeficiente = models.FloatField("Coeficiente")

    def __str__(self):
        return str(self.cantidad_maxima) + "--" + str(self.coeficiente)


class CoeficientePorCantidadVendedor(models.Model):
    cantidad_minima = models.IntegerField("Cantidad minima", default = 0)
    cantidad_maxima = models.IntegerField("Cantidad maxima", default = 0)
    com_48_60 = models.FloatField("48/60 Cuotas")
    com_24_30_motos = models.FloatField("24/30 Cuotas Motos")
    com_24_30_elec_soluc = models.FloatField("24/30 Cuotas Elec/Soluc")


    def __str__(self):
        return str(self.cantidad_maxima) + "--" + str(self.com_48_60) + "--" + str(self.com_24_30_motos) + "--" + str(self.com_24_30_elec_soluc)
    

class CoeficientePorProductividadSupervisor(models.Model):
    dinero = models.FloatField("Dinero")
    coeficiente = models.FloatField("Coeficiente")

    def __str__(self):
        return str(self.dinero) + "--" + str(self.coeficiente)


class CoeficientePorProductividadVendedor(models.Model):
    dinero = models.FloatField("Dinero")
    premio = models.FloatField("Premio")

    def __str__(self):
        return str(self.dinero) + "--" + str(self.premio)


class LiquidacionVendedor(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    campania = models.CharField("Campaña",max_length=50)
    cant_ventas = models.IntegerField("Cantidad de ventas")
    productividad = models.FloatField("Productividad")
    total_comisionado = models.FloatField("Total comisionado")
    detalle = models.JSONField(default=dict)

    def __str__(self):
        return self.usuario.nombre + "en camapaña" + self.campania + ": Productividad: " + str(self.productividad) + " Ventas: " + str(self.cant_ventas) + " Comision: " + str(self.total_comisionado)  


class LiquidacionSupervisor(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    campania = models.CharField("Campaña",max_length=50)

    cant_ventas = models.IntegerField("Cantidad de ventas")
    productividad = models.FloatField("Productividad",default=0)
    total_comisionado = models.FloatField("Total comisionado")
    detalle = models.JSONField(default=dict)

    def __str__(self):
        return self.usuario.nombre + "en camapaña" + self.campania + ": Productividad: " + str(self.productividad) + " Ventas: " + str(self.cant_ventas) + " Comision: " + str(self.total_comisionado)  
    

class LiquidacionGerenteSucursal(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.DO_NOTHING)
    campania = models.CharField("Campaña",max_length=50)
    total_comisionado = models.FloatField("Total comisionado")
    detalle = models.JSONField(default=dict)

    def __str__(self):
        return self.usuario.nombre + "en camapaña" + self.campania + ": Total comisionado: " + str(self.total_comisionado) 

        
class LiquidacionAdmin(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.DO_NOTHING)
    campania = models.CharField("Campaña",max_length=50)
    total_comisionado_blanco = models.FloatField("Total comisionado blanco")
    total_comisionado_negro = models.FloatField("Total comisionado negro")


class LiquidacionCompleta(models.Model): 
    fecha = models.CharField("Fecha", max_length=10)
    campania = models.CharField("Campaña",max_length=50)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.DO_NOTHING, related_name="liquidacion_sucursal")
    total_recaudado = models.FloatField("Total recaudado",default=0)
    total_proyectado = models.FloatField("Total proyectado",default=0)
    total_liquidado = models.FloatField("Total liquidado",default=0)
    cant_ventas = models.IntegerField("Cantidad de ventas",default=0)
    detalle_vendedores = models.ManyToManyField(LiquidacionVendedor, blank=True)
    detalle_supervisores = models.ManyToManyField(LiquidacionSupervisor, blank=True)
    detalle_gerentes = models.ManyToManyField(LiquidacionGerenteSucursal, blank=True)
    detalle_admins = models.ManyToManyField(LiquidacionAdmin, blank=True)


    def __str__(self):
        return self.campania + "--" + self.sucursal.pseudonimo + "--" + str(self.total_liquidado)
