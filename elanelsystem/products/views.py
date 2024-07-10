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


def requestProducts(request):
    if request.method == 'POST':
        tipo = json.loads(request.body).get('tipoProducto', None)
        productos = Products.objects.filter(tipo_de_producto=tipo) if tipo else []
        productos = [{"nombre": producto.nombre, "importe": producto.importe} for producto in productos]        
        return JsonResponse({"message": "OK", "productos": productos},safe=False)