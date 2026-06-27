from django.contrib import admin
from .models import Auditoria, PagoCannon, Ventas, MetodoPago,CoeficientesListadePrecios, ArqueoCaja, MovimientoExterno, CuentaCobranza
from datetime import datetime
from django.db import connection
from django.db.models import Q, TextField
from django.db.models.functions import Cast
# admin.site.register(Ventas)
admin.site.register(ArqueoCaja)
admin.site.register(MovimientoExterno)
admin.site.register(CuentaCobranza)
admin.site.register(MetodoPago)
# admin.site.register(PagoCannon)

@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    # Mostrar columnas específicas en el listado
    list_display = ('venta','version', 'grade', 'fecha_hora',"comentarios",)
    
    # Agregar opciones de búsqueda
    search_fields = ('venta__nro_operacion', 'fecha_hora',"comentarios",)
    
    # Agregar filtros
    list_filter = ('grade',)


@admin.register(PagoCannon)
class PagoCannonAdmin(admin.ModelAdmin):
    # Mostrar columnas específicas en el listado
    list_display = ('venta',"nombre_cliente", 'nro_recibo', 'nro_cuota', 'fecha','campana_de_pago','monto',"metodo_pago","cobrador",)
    
    # Agregar opciones de búsqueda
    search_fields = ('venta__nro_operacion','venta__nro_cliente__nombre', 'nro_recibo', 'metodo_pago__alias',"campana_de_pago","nro_cuota","cobrador__alias",)
    
    # Agregar filtros
    list_filter = ('nro_cuota','metodo_pago__alias',"cobrador__alias","venta__agencia", "campana_de_pago")


    @admin.display(description='Cliente')
    def nombre_cliente(self, obj):
        for i in range(len(obj.venta.cantidadContratos)):
                print(f"{obj.venta.nro_cliente.nombre.upper() if obj.venta and obj.venta.nro_cliente else '-'}")

        return obj.venta.nro_cliente.nombre if obj.venta and obj.venta.nro_cliente else "-"

@admin.register(CoeficientesListadePrecios)
class CoeficientesAdmin(admin.ModelAdmin):
    list_display = ('valor_nominal', 'cuota', 'porcentage')

# Filtro para años
class YearFilter(admin.SimpleListFilter):
    title = 'Año'
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        # Genera una lista de años desde 2022 hasta el año actual
        current_year = datetime.now().year
        return [(str(year), str(year)) for year in range(2022, current_year + 1)]

    def queryset(self, request, queryset):
        if self.value():
            # Busca fechas que tengan /AÑO en la posición correcta (DD/MM/YYYY)
            return queryset.filter(fecha__regex=rf"\d{{2}}/\d{{2}}/{self.value()}")
        return queryset

CONTRACT_KEYS = ("nroContrato", "nro_contrato", "numero", "nro", "contrato")

class InputFilter(admin.SimpleListFilter):
    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        return ((),)

    def choices(self, changelist):
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice

class NumeroOrdenFilter(InputFilter):
    parameter_name = 'nro_orden'
    title = 'Número de Orden'

    def queryset(self, request, queryset):
        term = self.value()
        if term:
            term = term.strip()
            values_to_try = [term]
            if term.isdigit():
                values_to_try.append(int(term))
            
            from django.db import connection
            from django.db.models import Q, TextField
            from django.db.models.functions import Cast
            
            extra = Q()
            if connection.vendor == "postgresql":
                for v in values_to_try:
                    extra |= Q(cantidadContratos__contains=[v])
                    extra |= Q(**{"cantidadContratos__contains": [{"nro_orden": v}]})
                    extra |= Q(**{"cantidadContratos__contains": {"nro_orden": v}})
            else:
                extra |= Q(Cast('cantidadContratos', TextField()).icontains(term))
                
            return queryset.filter(extra)
        return queryset

@admin.register(Ventas)
class VentasAdmin(admin.ModelAdmin):
    list_display = (
        'nro_operacion', 'get_cliente', 'get_producto', 'campania', 'fecha',
        'vendedor', 'supervisor', 'importe', 'get_contratos'  # 👈 muestra contratos
    )
    search_fields = (
        'nro_operacion', 'nro_cliente__nombre', 'producto__nombre',
        'fecha', 'campania', 'nro_cuotas',
    )
    list_filter = (NumeroOrdenFilter, 'supervisor', "vendedor", "agencia", "campania")

    def get_cliente(self, obj):
        return obj.nro_cliente.nombre
    get_cliente.short_description = 'Cliente'

    def get_producto(self, obj):
        return obj.producto.nombre
    get_producto.short_description = 'Producto'

    def get_contratos(self, obj):
        """
        Muestra números de contrato detectados dentro de `cantidadContratos`
        aceptando lista de ints/strings, lista de dicts o dict plano.
        """
        data = obj.cantidadContratos or []
        found = []

        def push(val):
            if val is None:
                return
            try:
                found.append(str(val).strip())
            except Exception:
                pass

        if isinstance(data, list):
            for el in data:
                if isinstance(el, (int, str)):
                    push(el)
                elif isinstance(el, dict):
                    for k in CONTRACT_KEYS:
                        if k in el:
                            push(el[k]); break
        elif isinstance(data, dict):
            for k in CONTRACT_KEYS:
                if k in data:
                    push(data[k])

        return ", ".join([f for f in found if f]) or "—"
    get_contratos.short_description = "Nº contrato(s)"

    # 🔎 Inyecta búsqueda por contrato dentro del JSON desde el cuadro "Buscar"
    def get_search_results(self, request, queryset, search_term):
        qs, use_distinct = super().get_search_results(request, queryset, search_term)
        term = (search_term or "").strip()
        if not term:
            return qs, use_distinct

        # admitimos "12345" y también "0012345"
        values_to_try = [term]
        if term.isdigit():
            values_to_try.append(int(term))  # exact match numérico
            # Búsqueda exacta por nro_operacion
            qs = qs | queryset.filter(nro_operacion=int(term))

        if connection.vendor == "postgresql":
            extra = Q()

            # Caso A: lista de ints/strings -> [12345] / ["12345"]
            for v in values_to_try:
                extra |= Q(cantidadContratos__contains=[v])

            # Caso B: lista de objetos -> [{"nroContrato": 12345}], etc.
            for key in CONTRACT_KEYS:
                for v in values_to_try:
                    extra |= Q(**{"cantidadContratos__contains": [{key: v}]})

            # Caso C: objeto plano -> {"nroContrato": 12345}
            for key in CONTRACT_KEYS:
                for v in values_to_try:
                    extra |= Q(**{"cantidadContratos__contains": {key: v}})

            qs = qs | queryset.filter(extra)
        else:
            # Fallback genérico (SQLite/MySQL): buscar como texto
            qs = qs | queryset.filter(Cast('cantidadContratos', TextField()).icontains(term))

        return qs, use_distinct