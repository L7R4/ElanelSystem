from django.contrib import admin
from .models import Plan, Products

@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ("tipo_de_producto","tipodePlan","nombre","plan","activo")
    list_editable = ("activo",)
    search_fields = ("nombre","tipo_de_producto","tipodePlan")

@admin.register(Plan)
class PlansAdmin(admin.ModelAdmin):
    list_display = ("valor_nominal", 'suscripcion', 'primer_cuota', 'c24_porcentage', 'c30_porcentage','c48_porcentage','c60_porcentage') 
