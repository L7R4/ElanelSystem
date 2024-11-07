import json
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views import generic
from .models import Plan, Products
import datetime
import os
from django.http import JsonResponse
from dateutil.relativedelta import relativedelta

class Planes(generic.View):
    template_name = "planes.html"
    model = Plan
    def get(self,request,*args,**kwargs):
        planes = Plan.objects.all()
        context = {"planes": planes}
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            precio = data.get('precio')
            paquete = data.get('paquete')
            suscripcion = data.get('suscripcion')
            primer_cuota = data.get('primer_cuota')
            p_24 = data.get('p_24')
            p_30 = data.get('p_30')
            p_48 = data.get('p_48')
            p_60 = data.get('p_60')

            plan = Plan.objects.create(
                valor_nominal=precio,
                tipodePlan=paquete,
                suscripcion=suscripcion,
                primer_cuota=primer_cuota,
                c24_porcentage=p_24,
                c30_porcentage=p_30,
                c48_porcentage=p_48,
                c60_porcentage=p_60,
            )

            # Retornar el nuevo producto en JSON para actualizar la vista
            return JsonResponse({
                'success': True,
                'plan': {
                    "precio": plan.valor_nominal,
                    "paquete": plan.tipodePlan,
                    "suscripcion": plan.suscripcion,
                    "primer_cuota": plan.primer_cuota,
                    "p_24": plan.c24_porcentage,
                    "p_30": plan.c30_porcentage,
                    "p_48": plan.c48_porcentage,
                    "p_60": plan.c60_porcentage,
                }
            })
        except Exception as e:
            print(e)  # Para depuración
            return JsonResponse({
                'success': False,
                'message': str(e)  # Convertimos el error a string
            })

#region Productos
class ViewProducts(generic.View):
    template_name = "products.html"
    model = Products

    def get(self,request,*args,**kwargs):
        products = Products.objects.all()
        motos = Products.objects.filter(tipo_de_producto ="Moto")
        combos = Products.objects.filter(tipo_de_producto ="Electrodomestico")
        prestamos = Products.objects.filter(tipo_de_producto ="Prestamo")
        planes = [{"valor_nominal": plan.valor_nominal, "tipodePlan":plan.tipodePlan} for plan in Plan.objects.all()]

        context = {
            "productos": products,
            "motos": motos,
            "combos": combos,
            "planes": json.dumps(planes),
            "prestamos": prestamos
            }
        

        return render(request, self.template_name, context)
    
    def post(self,request,*args, **kwargs):
        try:
            data = json.loads(request.body)
            tipo = data.get('tipo')
            nombre = data.get('nombre', None)
            plan = Plan.objects.get(valor_nominal=int(data.get('precio')))

            producto = Products.objects.create(
                tipo_de_producto= tipo.capitalize(),
                nombre=nombre if tipo != "solucion" else "$" + str(plan.valor_nominal),
                plan=plan,
            )
            
            # Retornar el nuevo producto en JSON para actualizar la vista
            return JsonResponse({
                'success': True,
                'producto': {
                    'nombre': producto.nombre,
                    'plan': producto.plan.tipodePlan,
                    'precio': producto.plan.valor_nominal
                }
            })
        
        except Exception as e:
            print(e)  # Para depuración
            return JsonResponse({
                'success': False,
                'message': str(e)  # Convertimos el error a string
            })

def requestProducts(request):
    if request.method == 'POST':
        tipo = json.loads(request.body).get('tipoProducto', None)
        productos = Products.objects.filter(tipo_de_producto=tipo) if tipo else []

        productos_list = []
        for producto in productos:
            productos_list.append(
                {"nombre": producto.nombre, 
                "paquete": producto.plan.tipodePlan,
                "primer_cuota": producto.plan.primer_cuota,
                "suscripcion": producto.plan.suscripcion,
                "importe": producto.plan.valor_nominal,
                "c24_porcentage": producto.plan.c24_porcentage,
                "c30_porcentage": producto.plan.c30_porcentage,
                "c48_porcentage": producto.plan.c48_porcentage,
                "c60_porcentage": producto.plan.c60_porcentage,
                })

      
        return JsonResponse({"message": "OK", "productos": productos_list},safe=False)  

#endregion

