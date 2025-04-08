from django.contrib import admin
from .models import *

admin.site.register(Asegurado)
admin.site.register(MontoTardanzaAusencia)


admin.site.register(LiquidacionVendedor)
admin.site.register(LiquidacionSupervisor)
admin.site.register(LiquidacionGerenteSucursal)
admin.site.register(LiquidacionAdmin)
admin.site.register(LiquidacionCompleta)




# Register your models here.
