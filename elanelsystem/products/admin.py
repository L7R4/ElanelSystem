from django.contrib import admin
from .models import Plan, Products

@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ("tipo_de_producto","tipodePlan","nombre","plan")

@admin.register(Plan)
class PlansAdmin(admin.ModelAdmin):
    list_display = ("valor_nominal", 'suscripcion', 'primer_cuota', 'c24_porcentage', 'c30_porcentage','c48_porcentage','c60_porcentage') 
