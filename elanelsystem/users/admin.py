from django.contrib import admin
from .models import Cliente,Usuario,Key,Sucursal,Ausencia,Descuento
from django.contrib.auth.models import Permission

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nro_cliente', 'nombre', 'dni', 'domic', 'loc', 'prov', 'cod_postal', 'tel', 'fec_nacimiento', 'estado_civil', 'ocupacion')
    list_filter = ("agencia_registrada",)
    search_fields = ('nombre', 'dni',)
    

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rango', 'dni', 'domic', 'prov', 'tel', 'fec_nacimiento')

    list_filter = ("sucursales", "suspendido",)

    search_fields = ('nombre', 'dni',)

admin.site.register(Key)
admin.site.register(Sucursal)
admin.site.register(Permission)
admin.site.register(Ausencia)
admin.site.register(Descuento)

