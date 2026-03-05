from django.contrib import admin
from .models import *

admin.site.register(MontoTardanzaAusencia)
admin.site.register(Liquidacion)
admin.site.register(AjusteComision)

@admin.register(ConfiguracionLiquidacion)
class ConfiguracionLiquidacionAdmin(admin.ModelAdmin):
    list_display = ("descripcion", "vigencia_desde")
    ordering = ("-vigencia_desde",)





# Register your models here.
