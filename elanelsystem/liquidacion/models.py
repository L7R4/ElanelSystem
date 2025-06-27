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
    # objetivo = models.IntegerField("Objetivo", default=0)

    def __str__(self):
        return str(self.dinero) + "--" + str(self.dirigido)

class Liquidacion(models.Model):
    agencia = models.ForeignKey(Sucursal, on_delete=models.DO_NOTHING, related_name="liquidacion_agencia")
    campania = models.CharField("Campaña", max_length=50)
    fecha = models.CharField("Fecha", max_length=15)
    json_data_liquidacion = models.JSONField(default=list)
