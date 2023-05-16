from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views import generic
from .models import Ventas,CoeficientesListadePrecios
from .forms import FormCreateVenta
from users.models import Cliente,Usuario
from .models import Ventas
from products.models import Products
import json
from django.http import HttpResponseRedirect, HttpResponse


class Resumen(generic.View):
    template_name = 'resumen.html'

    def get(self,request,*args,**kwargs):
        ventas = Ventas.objects.all()
        venta = Ventas.objects.get(pk=1)
        print(venta.nro_cliente.nro_cliente)
        context = {
            "ventas" : ventas,
        }
        # print(context)
        return render(request, self.template_name, context)


class CrearVenta(generic.View):
    model = Ventas
    template_name = "create_sale.html"
    form_class = FormCreateVenta
    
    def get(self,request,*args, **kwargs):
        form = FormCreateVenta
        
        customers = Cliente.objects.all()
        products = Products.objects.all()
        usuarios = Usuario.objects.filter(rango = "Vendedor") | Usuario.objects.filter(rango="Supervisor")
        intereses = CoeficientesListadePrecios.objects.all()
        context ={
            'form' : form,
            'customers': customers, 
            'products': products, 
            'intereses': intereses, 
            'usuarios': usuarios, 
        }

        json_complete=[]

        customers_list = []
        for customer in list(customers):
            data_customer = {}
            data_customer["nro_cliente"] = customer.nro_cliente
            data_customer["nombre"] = customer.nombre
            customers_list.append(data_customer)
        json_complete.append(customers_list)

        products_list = []
        for product in list(products):
            data_product = {}
            data_product["tipo_de_producto"] = product.tipo_de_producto
            data_product["nombre"] = product.nombre
            data_product["paquete"] = product.paquete
            data_product["importe"] = product.importe
            products_list.append(data_product)
        json_complete.append(products_list)
    
        interes_list = []
        for interes in list(intereses):
            data_interes = {}
            data_interes["valor_nominal"] = interes.valor_nominal
            data_interes["cuota"] = interes.cuota
            data_interes["porcentage"] = interes.porcentage
            interes_list.append(data_interes)
        json_complete.append(interes_list)


        users_list = []
        for user in list(usuarios):
            data_users = {}
            data_users["nombre"] = user.nombre
            data_users["rango"] = user.rango
            users_list.append(data_users)
        json_complete.append(users_list)
        data = json.dumps(json_complete)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponse(data, 'application/json')
        
        return render(request,self.template_name,context)

    def post(self, request, *args, **kwargs):
        form =self.form_class(request.POST)
        if form.is_valid():
                sale = Ventas()
                sale.nro_cliente = form.cleaned_data['nro_cliente']
                sale.nombre_completo = form.cleaned_data['nombre_completo']
                sale.nombre_completo = form.cleaned_data['nombre_completo']
                sale.nro_solicitud = form.cleaned_data['nro_solicitud']
                sale.modalidad = form.cleaned_data['modalidad']
                sale.nro_cuotas = form.cleaned_data['nro_cuotas']
                sale.importe = form.cleaned_data['importe']
                sale.tasa_interes = form.cleaned_data['tasa_interes']
                sale.intereses_generados = form.cleaned_data['intereses_generados']
                sale.importe_x_cuota = form.cleaned_data['importe_x_cuota']
                sale.total_a_pagar = form.cleaned_data['total_a_pagar']
                sale.fecha = form.cleaned_data['fecha']
                sale.tipo_producto = form.cleaned_data['tipo_producto']
                sale.producto = form.cleaned_data['producto']
                sale.paquete = form.cleaned_data['paquete']
                sale.nro_orden = form.cleaned_data['nro_orden']
                sale.vendedor = form.cleaned_data['vendedor']
                sale.supervisor = form.cleaned_data['supervisor']
                sale.observaciones = form.cleaned_data['observaciones']
                sale.save()
                return redirect('sales:resumen')
        else:
                print(form.errors)
        return render(request, self.template_name, {'form': form})