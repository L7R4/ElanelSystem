from django.contrib import admin
from .models import Ventas,CoeficientesListadePrecios
admin.site.register(Ventas)

@admin.register(CoeficientesListadePrecios)
class CoeficientesAdmin(admin.ModelAdmin):
    list_display = ('valor_nominal', 'cuota', 'porcentage')
