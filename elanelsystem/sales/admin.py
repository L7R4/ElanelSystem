from django.contrib import admin
from .models import Ventas,CoeficientesListadePrecios, ArqueoCaja, MovimientoExterno, CuentaCobranza
admin.site.register(Ventas)
admin.site.register(ArqueoCaja)
admin.site.register(MovimientoExterno)
admin.site.register(CuentaCobranza)

@admin.register(CoeficientesListadePrecios)
class CoeficientesAdmin(admin.ModelAdmin):
    list_display = ('valor_nominal', 'cuota', 'porcentage')
