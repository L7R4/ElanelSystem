from django.contrib import admin
from .models import Products

@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ("tipo_de_producto","nombre","paquete","importe")
