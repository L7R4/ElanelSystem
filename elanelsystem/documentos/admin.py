from django.contrib import admin

from .models import Documento


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ("nombre_original", "categoria", "subido_por", "fecha_subida")
    list_filter = ("categoria",)
    search_fields = ("nombre_original", "descripcion")
