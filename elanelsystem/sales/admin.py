from django.contrib import admin
from .models import Auditoria, PagoCannon, Ventas, MetodoPago,CoeficientesListadePrecios, ArqueoCaja, MovimientoExterno, CuentaCobranza
# admin.site.register(Ventas)
admin.site.register(ArqueoCaja)
admin.site.register(MovimientoExterno)
admin.site.register(CuentaCobranza)
admin.site.register(MetodoPago)
# admin.site.register(PagoCannon)

@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    # Mostrar columnas específicas en el listado
    list_display = ('venta','version', 'grade', 'fecha_hora', 'reintegro_dinero','motivo',"comentarios",)
    
    # Agregar opciones de búsqueda
    search_fields = ('venta__nro_operacion', 'fecha_hora',"comentarios",)
    
    # Agregar filtros
    list_filter = ('grade', 'reintegro_dinero','motivo',)


@admin.register(PagoCannon)
class PagoCannonAdmin(admin.ModelAdmin):
    # Mostrar columnas específicas en el listado
    list_display = ('venta','nro_recibo', 'nro_cuota', 'fecha','campana_de_pago','monto',"metodo_pago","cobrador",)
    
    # Agregar opciones de búsqueda
    search_fields = ('venta__nro_operacion', 'nro_recibo', 'metodo_pago__alias',"campana_de_pago","nro_cuota","cobrador__alias",)
    
    # Agregar filtros
    list_filter = ('metodo_pago__alias',"cobrador__alias",)


@admin.register(CoeficientesListadePrecios)
class CoeficientesAdmin(admin.ModelAdmin):
    list_display = ('valor_nominal', 'cuota', 'porcentage')


@admin.register(Ventas)
class VentasAdmin(admin.ModelAdmin):
    # Mostrar columnas específicas en el listado
    list_display = ('nro_operacion', 'get_cliente', 'get_producto','campania','fecha',"vendedor","supervisor", "importe",)
    
    # Hacer algunas columnas editables directamente desde el listado
    # list_editable = ('modalidad', 'importe', 'total_a_pagar')
    
    # Agregar opciones de búsqueda
    search_fields = ('nro_cliente__nombre', 'producto__nombre', 'fecha',"campania","nro_cuotas",)
    
    # Agregar filtros
    list_filter = ('supervisor', "vendedor", "agencia","campania",)
    
    # Mostrar más información en la vista de detalle
    # readonly_fields = ('nro_operacion', 'cuotas', 'adjudicado', 'deBaja', 'auditoria')
    
    # Personalizar títulos de relaciones para mostrar nombres
    def get_cliente(self, obj):
        return obj.nro_cliente.nombre
    get_cliente.short_description = 'Cliente'

    def get_producto(self, obj):
        return obj.producto.nombre
    get_producto.short_description = 'Producto'
