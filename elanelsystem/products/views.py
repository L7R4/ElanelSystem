import json
from django.forms import ValidationError
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views import generic
from .models import Plan, Products
import datetime
import os
from django.http import JsonResponse
from dateutil.relativedelta import relativedelta
from django.db.models import Q


class Planes(generic.View):
    template_name = "planes.html"
    model = Plan
    def get(self,request,*args,**kwargs):
        planes = Plan.objects.all().order_by('-valor_nominal')
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
            iconMessage = "/static/images/icons/checkMark.svg"

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
                },
                "message": "Plan creado exitosamente",
                "icon": iconMessage
            })
        except Exception as e:
            iconMessage = "/static/images/icons/error_icon.svg"
            return JsonResponse({
                'success': False,
                "message": "Hubo un error al crear el plan",
                "icon": iconMessage
            })

def deletePlan(request):
    if request.method == 'POST':
        try:
            form = json.loads(request.body)
            
            valorRequest = form.get('valor')
            if(Plan.objects.filter(valor_nominal=valorRequest).exists()):
                Plan.objects.filter(valor_nominal=valorRequest).delete()

                iconMessage = "/static/images/icons/checkMark.svg"
                return JsonResponse({"status":True, "message": "Plan eliminado exitosamente", "icon": iconMessage},safe=False) 
            else:
                iconMessage = "/static/images/icons/error_icon.svg"
                return JsonResponse({"status":False, "message": "Hubo un error al eliminar el plan","icon": iconMessage}, safe=False) 
                

        except Exception as e:
            print(e)
            return JsonResponse({"status":False},safe=False) 

#region Productos
class ViewProducts(generic.View):
    template_name = "products.html"
    model = Products

    def get(self,request,*args,**kwargs):
        products = Products.objects.all()
        motos = Products.objects.filter(tipo_de_producto ="Moto").order_by('plan__valor_nominal')
        combos = Products.objects.filter(tipo_de_producto ="Combo").order_by('plan__valor_nominal')
        prestamos = Products.objects.filter(tipo_de_producto ="Solucion").order_by('plan__valor_nominal')
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
        errors ={}
        try:
            data = json.loads(request.body)
            tipo = data.get('tipo')
            nombre = data.get('nombre', None)
            plan = Plan.objects.get(valor_nominal=int(data.get('precio')))
            print(tipo,nombre)
            producto = Products()
            
            producto.tipo_de_producto= tipo.capitalize()
            producto.nombre=nombre if tipo != "solucion" else "$" + str(plan.valor_nominal)
            producto.plan=plan

            producto.nombre = producto.nombre.title() # Formatear el nombre del producto
            
            try:
                producto.full_clean()
            except ValidationError as e:
                errors.update(e.message_dict)


            if len(errors) != 0:
                print(errors)
                return JsonResponse({
                'success': False,
                'errors': errors
                })
                
            else:
                producto.save()
                return JsonResponse({
                    'success': True,
                    'producto': {
                        'nombre': producto.nombre,
                        'plan': producto.tipodePlan,
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
        productos = Products.objects.filter(tipo_de_producto=tipo).order_by('-plan__valor_nominal') if tipo else []

        productos_list = []
        for producto in productos:
            productos_list.append(
                {
                "id": producto.id,
                "nombre": producto.nombre, 
                "paquete": producto.tipodePlan,
                "primer_cuota": producto.plan.primer_cuota,
                "suscripcion": producto.plan.suscripcion,
                "importe": producto.plan.valor_nominal,
                "c24_porcentage": producto.plan.c24_porcentage,
                "c30_porcentage": producto.plan.c30_porcentage,
                "c48_porcentage": producto.plan.c48_porcentage,
                "c60_porcentage": producto.plan.c60_porcentage,
                })

      
        return JsonResponse({"message": "OK", "productos": productos_list},safe=False)  

def requestProducts2(request):
    query_params = request.GET
    usuarios = Products.objects.all()
    print(query_params)
    # Mapeo de parámetros a condiciones Q
    filter_map = {
        'nombre': 'nombre__icontains',
        'tipo_de_producto': 'tipo_de_producto__icontains',
        # 'plan': 'plan__icontains',
    }

    # Construcción dinámica de filtros
    filters = Q()
    for param, query in filter_map.items():
        if param in query_params:
            filters &= Q(**{query: query_params[param]})

    # Aplicar los filtros al modelo Usuario
    usuarios = Products.objects.filter(filters).distinct()
    print("Usuarios filtrados")
    print(usuarios)
    # Serializar la respuesta
    data = [
        {
            'id': usuario.id,
            'nombre': usuario.nombre,
            'tipo_de_producto': usuario.tipo_de_producto,
            # 'plan': usuario.plan,
        }
        for usuario in usuarios
    ]

    return JsonResponse(data, safe=False)



def deleteProduct(request):
    if request.method == 'POST':
        try:
            form = json.loads(request.body)
            
            nombreRequest = form.get('nombre')
            print(nombreRequest)
            if(Products.objects.filter(nombre=nombreRequest).exists()):
                Products.objects.filter(nombre=nombreRequest).delete()
                return JsonResponse({"status":True},safe=False) 
            else:
                return JsonResponse({"status":False},safe=False) 
                

        except Exception as e:
            print(e)
            return JsonResponse({"status":False},safe=False) 

        # productos_list = []
        # for producto in productos:
        #     productos_list.append(
        #         {"nombre": producto.nombre, 
        #         "paquete": producto.plan.tipodePlan,
        #         "primer_cuota": producto.plan.primer_cuota,
        #         "suscripcion": producto.plan.suscripcion,
        #         "importe": producto.plan.valor_nominal,
        #         "c24_porcentage": producto.plan.c24_porcentage,
        #         "c30_porcentage": producto.plan.c30_porcentage,
        #         "c48_porcentage": producto.plan.c48_porcentage,
        #         "c60_porcentage": producto.plan.c60_porcentage,
        #         })

#endregion

