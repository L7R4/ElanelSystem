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

class ConfiguracionLiquidacion(models.Model):
    vigencia_desde = models.DateField("Vigente desde")
    descripcion = models.CharField("Descripción", max_length=100)
    parametros = models.JSONField("Parámetros")

    class Meta:
        ordering = ["-vigencia_desde"]
        verbose_name = "Configuración de liquidación"
        verbose_name_plural = "Configuraciones de liquidación"

    def __str__(self):
        return f"{self.descripcion} (desde {self.vigencia_desde})"


class Liquidacion(models.Model):
    agencia = models.ForeignKey(Sucursal, on_delete=models.DO_NOTHING, related_name="liquidacion_agencia")
    campania = models.CharField("Campaña", max_length=50)
    fecha = models.CharField("Fecha", max_length=15)
    json_data_liquidacion = models.JSONField(default=list)
    cerrada = models.BooleanField("Cerrada", default=False)
    total_liquidado = models.FloatField("Total liquidado", default=0)
    cant_ventas = models.IntegerField("Cantidad de ventas", default=0)
    config_snapshot = models.JSONField("Snapshot de configuración", default=dict)
    version = models.PositiveIntegerField("Versión", default=1)
    es_vigente = models.BooleanField("Es vigente", default=True)
    motivo_reliquidacion = models.TextField("Motivo de reliquidación", blank=True, default="")


class AjusteComision(models.Model):
    TIPO_CHOICES = [("positivo", "Positivo"), ("negativo", "Negativo")]

    usuario     = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="ajustes_comision")
    agencia     = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name="ajustes_comision")
    campania    = models.CharField("Campaña", max_length=50)
    ajuste_tipo = models.CharField("Tipo", max_length=10, choices=TIPO_CHOICES)
    dinero      = models.PositiveIntegerField("Monto")
    observaciones = models.TextField("Observaciones", blank=True, default="")
    creado_en   = models.DateTimeField("Creado en", auto_now_add=True)
    activo      = models.BooleanField("Activo", default=True)

    class Meta:
        ordering = ["creado_en"]
        verbose_name = "Ajuste de comisión"
        verbose_name_plural = "Ajustes de comisión"

    def __str__(self):
        signo = "+" if self.ajuste_tipo == "positivo" else "-"
        return f"{signo}${self.dinero} → {self.usuario.nombre} ({self.campania})"
