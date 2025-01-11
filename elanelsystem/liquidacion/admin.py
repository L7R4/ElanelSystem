from django.contrib import admin
from .models import *

admin.site.register(CoeficientePorCantidadSupervisor)
admin.site.register(Asegurado)
admin.site.register(CoeficientePorCantidadVendedor)
admin.site.register(CoeficientePorProductividadVendedor)
admin.site.register(CoeficientePorProductividadSupervisor)
admin.site.register(MontoTardanzaAusencia)


admin.site.register(LiquidacionVendedor)
admin.site.register(LiquidacionSupervisor)
admin.site.register(LiquidacionGerenteSucursal)
admin.site.register(LiquidacionAdmin)
admin.site.register(LiquidacionCompleta)




# Register your models here.
