from django.db import models
from users.models import Usuario,Sucursal
from sales.models import Ventas
from datetime import datetime
# from .utils import coeficienteCantidadOrdenadoVendedor, coeficienteProductividadOrdenadoVendedor,getDetalleComisionPorCantVentasPropias,getPremioProductividadVentasPropias,getAusenciasTardanzas,getAdelantos,getAsegurado,calcular_ventas,calcular_productividad

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
    vendedor = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    campania = models.IntegerField("Campaña")
    cant_ventas = models.IntegerField("Cantidad de ventas")
    productividad = models.FloatField("Productividad")
    total_comisionado = models.FloatField("Total comisionado")
    detalle = models.JSONField(default=dict)

    def __str__(self):
        return self.vendedor.nombre + "en camapaña" + self.campania + ": Productividad: " + self.productividad + " Ventas: " + self.cant_ventas + " Comision: " + self.total_comisionado  


class LiquidacionSupervisor(models.Model):
    supervisor = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    campania = models.IntegerField("Campaña")
    cant_ventas = models.IntegerField("Cantidad de ventas")
    productividad = models.FloatField("Productividad",default=0)
    total_comisionado = models.FloatField("Total comisionado")
    detalle = models.JSONField(default=dict)

    def __str__(self):
        return self.vendedor.nombre + "en camapaña" + self.campania + ": Productividad: " + self.productividad + " Ventas: " + self.cant_ventas + " Comision: " + self.total_comisionado  
    

class LiquidacionGerenteSucursal(models.Model):
    gerente = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.DO_NOTHING)
    campania = models.IntegerField("Campaña")
    total_comisionado = models.FloatField("Total comisionado")
    detalle = models.JSONField(default=dict)

    def __str__(self):
        return self.gerente.nombre + "en camapaña" + self.campania + ": Total comisionado: " + self.total_comisionado 
        
class LiquidacionAdmin(models.Model):
    admin = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.DO_NOTHING)
    campania = models.IntegerField("Campaña")
    total_comisionado_blanco = models.FloatField("Total comisionado blanco")
    total_comisionado_negro = models.FloatField("Total comisionado negro")


class LiquidacionCompleta(models.Model): 
    fecha = models.CharField("Fecha", max_length=10)
    camapania = models.IntegerField("Camapaña")
    total_recaudado =models.FloatField("Total recaudado",default=0)
    total_liquidado = models.FloatField("Total liquidado",default=0)
    cant_ventas = models.IntegerField("Cantidad de ventas",default=0)
    detalle_vendedores = models.ManyToManyField(LiquidacionVendedor, blank=True)
    detalle_supervisores = models.ManyToManyField(LiquidacionSupervisor, blank=True)
    detalle_gerentes = models.ManyToManyField(LiquidacionGerenteSucursal, blank=True)
    detalle_admins = models.ManyToManyField(LiquidacionAdmin, blank=True)


    def __str__(self):
        return self.dinero + "--" + self.premio
