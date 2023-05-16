from django.contrib import admin
from .models import Cliente,Usuario
from django.contrib.auth.models import Permission

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nro_cliente', 'nombre', 'dni', 'domic', 'loc', 'prov', 'cod_postal', 'tel', 'fec_nacimiento', 'estado_civil', 'ocupacion')


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rango', 'dni', 'domic', 'prov', 'tel', 'fec_nacimiento')

admin.site.register(Permission)
