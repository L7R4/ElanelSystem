from django.contrib import admin
from .models import *

admin.site.register(CoeficientePorCantidadSupervisor)
admin.site.register(Asegurado)
admin.site.register(CoeficientePorCantidadVendedor)
admin.site.register(CoeficientePorProductividadVendedor)
admin.site.register(CoeficientePorProductividadSupervisor)

# Register your models here.
