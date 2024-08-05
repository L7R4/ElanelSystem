import json
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views import generic
from .models import Plan, Products
import datetime
import os
from django.http import JsonResponse
from dateutil.relativedelta import relativedelta

class CRUDPlanes(generic.View):
    template_name = "planes.html"
    model = Plan
    def get(self,request,*args,**kwargs):
        planes = Plan.objects.all()
        context = {"planes": planes}
        print(context)
        return render(request, self.template_name, context)
    

#region Productos
class ViewProducts(generic.View):
    template_name = "products.html"
    model = Products

    def get(self,request,*args,**kwargs):
        products = Products.objects.all()
        context = {"productos": products}
        print(context)
        return render(request, self.template_name, context)
    
# class PanelSucursales(TestLogin, generic.View):
#     template_name = "panelSucursales.html"
#     # permission_required = "sales.my_ver_resumen"
#     def get(self,request,*args,**kwargs):
#         sucursales = Sucursal.objects.all()
#         context= {
#             "sucursales": sucursales,
#             }
#         return render(request, self.template_name, context)

#     def post(self,request,*args,**kwargs):
#         context = {}
#         pk = request.POST.get("inputID")
#         direccion = request.POST.get("inputDireccion")
#         hora = request.POST.get("inputHora")

#         # Para editar la sucursal 
#         sucursal = Sucursal.objects.get(pk=pk)
#         sucursal.direccion = direccion
#         sucursal.hora_apertura = hora

#         sucursal.save()  
#         response_data = {'message': 'Datos recibidos correctamente'}
#         return JsonResponse(response_data)
    
# def updateSucursal(request):
#     if request.method == "POST":
#         pk = json.loads(request.body)["sucursalPk"]
#         direccion = json.loads(request.body)["direccion"]
#         hora = json.loads(request.body)["horaApertura"]
        
#         sucursal = Sucursal.objects.get(pk=pk)
#         sucursal.direccion = direccion
#         sucursal.hora_apertura = hora
#         sucursal.save()
        
#         response_data = {"message":"Sucursal actualizada con exito!!"}
#         return JsonResponse(response_data)

# def addSucursal(request):
#     if request.method == "POST":
#         provincia = json.loads(request.body)["provincia"]
#         localidad = json.loads(request.body)["localidad"]
#         direccion = json.loads(request.body)["direccion"]
#         hora = json.loads(request.body)["horaApertura"]
        
#         newSucursal = Sucursal()
#         newSucursal.provincia = provincia.title()
#         newSucursal.localidad = localidad.title()
#         newSucursal.direccion = direccion.capitalize()
#         newSucursal.hora_apertura = hora
#         newSucursal.save()
        
#         response_data = {"message":"Sucursal creada exitosamente!!","pk":str(newSucursal.pk),'name': str(newSucursal.pseudonimo), "direccion": str(newSucursal.direccion), "hora": str(newSucursal.hora_apertura)}
#         return JsonResponse(response_data)
    
# def removeSucursal(request):
#     if request.method == "POST":
#         pk = int(json.loads(request.body)["pk"]) 

#         deleteSucursal = Sucursal.objects.get(pk=pk)

#         Usuario.objects.filter(sucursal=deleteSucursal).update(sucursal=None) # Setear en None los usuarios asociados para que no se borren
#         Ventas.objects.filter(agencia=deleteSucursal).update(agencia=None) # Setear en None las ventas asociadas para que no se borren
#         MovimientoExterno.objects.filter(agencia=deleteSucursal).update(agencia=None) # Setear en None los movimientos asociados para que no se borren
#         ArqueoCaja.objects.filter(agencia=deleteSucursal).update(agencia=None) # Setear en None los arqueos asociados para que no se borren

#         deleteSucursal.delete()
        
#         response_data = {"message":"Eliminado correctamente"}
#         return JsonResponse(response_data)

#endregion

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