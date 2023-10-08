import time
from typing import Any, Dict
from django.db import models
from django.forms import ValidationError
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.views import generic
from .models import Ventas,CoeficientesListadePrecios
from .forms import FormChangePAck, FormCreateVenta, FormCreateAdjudicacion
from users.models import Cliente,Usuario,Key
from .models import Ventas
from products.models import Products,Plan
import datetime
import os
import json
import random
import string
from django.shortcuts import reverse
from django.core.serializers import serialize
from dateutil.relativedelta import relativedelta
import requests
from django.core.paginator import Paginator
from .utils import printPDF

import elanelsystem.settings as settings



class Resumen(generic.View):
    template_name = 'resumen.html'

    def get(self,request,*args,**kwargs):
        ventas = Ventas.objects.all()
        context = {
            "ventas" : ventas,
        }
        # print(context)
        return render(request, self.template_name, context)
    
    
class CrearVenta(generic.DetailView):
    model = Cliente
    template_name = "create_sale.html"
    form_class = FormCreateVenta

    def get(self,request,*args, **kwargs):
        self.object = self.get_object()

        customers = Cliente.objects.all()
        products = Products.objects.all()
        usuarios = Usuario.objects.filter(rango = "Vendedor") | Usuario.objects.filter(rango="Supervisor")
        intereses = CoeficientesListadePrecios.objects.all()
        planes = Plan.objects.all()
       

        json_complete=[]


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


        planes_list = []
        for plan in list(planes):
            data_plan = {}
            data_plan["valor_nominal"] = plan.valor_nominal
            data_plan["suscripcion"] = plan.suscripcion
            data_plan["cuota_1"] = plan.cuota_1
            data_plan["tipodePlan"] = plan.tipodePlan
            data_plan["c24"] = plan.c24
            data_plan["c30"] = plan.c30
            data_plan["c48"] = plan.c48
            data_plan["c60"] = plan.c60
            planes_list.append(data_plan)
        json_complete.append(planes_list)
        data = json.dumps(json_complete)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponse(data, 'application/json')
        
        context ={
            'form' : self.form_class,
            "object": self.object,
            'customers': customers, 
            'products': products, 
            'intereses': intereses, 
            'usuarios': usuarios, 
        }
        return render(request,self.template_name,context)
    

    def post(self, request, *args, **kwargs):
        form =self.form_class(request.POST)
        
        if request.POST["nro_cliente"] != self.get_object().nro_cliente:
            raise ValidationError('Hubo un cambio malicioso de numero de cliente')
        
        if form.is_valid():
                sale = Ventas()

                # Para guardar como objeto Cliente
                nro_cliente_instance = Cliente.objects.get(nro_cliente__iexact=request.POST['nro_cliente'])
                sale.nro_cliente = nro_cliente_instance

                sale.nro_solicitud = form.cleaned_data['nro_contrato']
                sale.modalidad = form.cleaned_data['modalidad']
                sale.importe = form.cleaned_data['importe']
                sale.primer_cuota = form.cleaned_data['primer_cuota']
                sale.anticipo = form.cleaned_data['anticipo']
                sale.tasa_interes = form.cleaned_data['tasa_interes']
                sale.intereses_generados = form.cleaned_data['intereses_generados']
                sale.importe_x_cuota = form.cleaned_data['importe_x_cuota']
                sale.nro_cuotas = form.cleaned_data['nro_cuotas']
                sale.total_a_pagar = form.cleaned_data['total_a_pagar']
                sale.fecha = form.cleaned_data['fecha']
                sale.tipo_producto = form.cleaned_data['tipo_producto']
                sale.paquete = form.cleaned_data['paquete']
                sale.nro_orden = form.cleaned_data['nro_orden']

                # Para guardar como objeto Producto
                producto_instance = Products.objects.get(nombre__iexact=form.cleaned_data['producto'])
                sale.producto = producto_instance

                # Para guardar como objeto Usuario
                usuario_instance = Usuario.objects.get(nombre__iexact=form.cleaned_data['vendedor'])
                sale.vendedor = usuario_instance

                # Para guardar como objeto Usuario
                supervisor_instance = Usuario.objects.get(nombre__iexact=form.cleaned_data['supervisor'])
                sale.supervisor = supervisor_instance

                sale.save()
                sale.crearCuotas()
                sale.createBaja()
                sale.createAdjudicado()
                return redirect("users:cuentaUser",pk= self.get_object().pk)

        return render(request, self.template_name, {'form': form, 'object' : self.get_object()})
    

class DetailSale(generic.DetailView):
    model = Ventas
    template_name = "detail_sale.html"

    def get(self,request,*args,**kwargs):
        context ={}
        self.object = self.get_object()
        sale_target = Ventas.objects.get(pk=self.object.id)
        self.object.testVencimientoCuotas()
        status_cuotas = self.object.cuotas


        if(self.object.adjudicado):
            self.object.addPorcentajeAdjudicacion()


        cuotas = []

        initial = 0
        if(self.object.adjudicado["status"] == True):
            initial = 1
        for i in range (initial,int(sale_target.nro_cuotas+1)):
            cuota = "Cuota " + str(i) 
            cuotas.append(cuota)

        lenght = 5 # Cambia esto a la cantidad de caracteres que deseas generar

        # # Genera una cadena de caracteres aleatorios
        # code = ''.join(random.choice(string.ascii_letters) for _ in range(lenght))
        # context["code"] = code
        context['cuotas'] = cuotas
        context['cobradores'] = Usuario.objects.all()
        context["object"] = self.object
        context["nro_cuotas"] = sale_target.nro_cuotas
        context["urlRedirectPDF"] = reverse("sales:bajaPDF",args=[self.object.pk])

        try:
            if len(self.object.cuotas_pagadas()) >= 6:
                context["porcetageDefault"] = 50
            else:
                context["porcetageDefault"] = 0
        except IndexError as e:
            context["porcetageDefault"] = 0
        
        data = json.dumps(status_cuotas)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponse(data, 'application/json')
        return render(request,self.template_name,context)
    

    
    def post(self,request,*args,**kwargs):
        self.object = self.get_object()
        porcentageValido = 0
        try:
            if len(self.object.cuotas_pagadas()) >= 6:
                porcentageValido = 50
            else:
                porcentageValido = 0
        except IndexError as e:
            porcentageValido = 0
        
        requestKey=""
        try:
            print(json.loads(request.body)["c"])
            requestKey = json.loads(request.body)["c"]
        except KeyError:
            pass

        

        # PARA VALIDAR LA CLAVE DE LA INPUT DE PORCENTAJE DE BAJA
        if(request.method == 'POST' and "clave" in str(request.body)):
            clave = json.loads(request.body)

            correctPassw = Key.objects.all().filter(motivo="baja")[0].password
            passw = int(clave.get("clave"))
           
            if correctPassw == passw: 
                return JsonResponse({'ok': "OK",'c':'LpOim'}, safe=False)

            else:
                return HttpResponseBadRequest('Contraseña invalida', status=406)
        

        # PARA GENERAR EL PDF CON LA BAJA DESPUES DE LA CLAVE
        elif(request.method == 'POST' and ("porcentageLpOim" == requestKey)):
            porcentage = json.loads(request.body)["porcentage"]
            motivoDetalle = json.loads(request.body)["motivo"]
            self.object.darBaja("cliente",porcentage,motivoDetalle)
            response_data = {
                'success': True,
                'urlPDF': reverse("sales:bajaPDF", args=[self.object.pk]),
                'urlUser': reverse("users:cuentaUser", args=[self.object.nro_cliente.pk])
            }
           
            return JsonResponse(response_data, safe=False)
            

        # PARA GENERAR EL PDF CON LA BAJA SIN LA CLAVE
        elif(request.method == 'POST' and ("porcentage" == requestKey)):
            print("asdasd213")

            porcentage = json.loads(request.body)["porcentage"]
            if(int(porcentage) == porcentageValido):
                motivoDetalle = json.loads(request.body)["motivo"]
                self.object.darBaja("cliente",porcentage,motivoDetalle)
                response_data = {
                'success': True,
                'urlPDF': reverse("sales:bajaPDF", args=[self.object.pk]),
                'urlUser': reverse("users:cuentaUser", args=[self.object.nro_cliente.pk])
            }
                return JsonResponse(response_data, safe=False)
            else:
                print("Error")
                return HttpResponseBadRequest('WEPSSSSSSSSSSSS', status=406)
            
        elif request.method == 'POST' and "descuento" not in json.loads(request.body):
            data = json.loads(request.body)
            status = data.get('status')
            cuota = data.get('cuota')
            cobrador = data.get('cobrador')
            metodoPago = data.get('metodoPago')
            if status == "Pagado":
                self.object.pagoTotal(cuota,metodoPago,cobrador)
            elif status == "Parcial":
                amountParcial = data.get('amountParcial')
                self.object.pagoParcial(cuota,metodoPago,amountParcial,cobrador)

        elif(request.method == 'POST' and "descuento" in json.loads(request.body)):
            data = json.loads(request.body)
            cuota = data.get('cuota')
            descuento = data.get('descuento')
            self.object.aplicarDescuento(cuota,int(descuento))

        return redirect('sales:detail_sale',self.object.id)


class CreateAdjudicacion(generic.DetailView):
    model = Ventas
    template_name = "create_adjudicacionSorteo.html"
    form_class = FormCreateAdjudicacion
    
    def get(self,request,*args, **kwargs):
        self.object = self.get_object()
        url = request.path
        cuotasPagadas = self.object.cuotas_pagadas()
        print(cuotasPagadas)
        valoresCuotasPagadas = [item["total"] for item in cuotasPagadas]
        sumaCuotasPagadas = sum(valoresCuotasPagadas)
        if("negociacion" in url):
            sumaCuotasPagadas = sumaCuotasPagadas * 0.5
            tipoDeAdjudicacion = "NEGOCIACIÓN"
        else:
            tipoDeAdjudicacion = "SORTEO"
        
        aumentoPorcentaje = self.object.importe * 0.1 
        importeNuevo = aumentoPorcentaje + self.object.importe
       

        customers = Cliente.objects.all()
        products = Products.objects.all()
        usuarios = Usuario.objects.filter(rango = "Vendedor") | Usuario.objects.filter(rango="Supervisor")
        intereses = CoeficientesListadePrecios.objects.all()
        planes = Plan.objects.all()
       

        json_complete=[]


        products_list = []
        for product in list(products):
            data_product = {}
            data_product["tipo_de_producto"] = product.tipo_de_producto
            data_product["nombre"] = product.nombre
            data_product["importe"] = product.importe
            data_product["anticipo"] = sumaCuotasPagadas
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


        data = json.dumps(json_complete)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponse(data, 'application/json')
        
        context = {"venta": self.object,
                   'form' : self.form_class,
                   'url':url,
                   'products': products, 
                   'intereses': intereses,
                   'tipoDeAdjudicacion' : tipoDeAdjudicacion,
                   'importeNuevo': int(importeNuevo),
                   'producto': self.object.producto.nombre,
                   'tipoProducto': self.object.producto.tipo_de_producto,
                   'idCliente': self.object.nro_cliente.nro_cliente,
                   'dineroAnticipo' : int(sumaCuotasPagadas)}
        return render(request,self.template_name,context)
    

    def post(self, request, *args, **kwargs):
        form =self.form_class(request.POST)
        self.object = self.get_object()
        numeroAdjudicacion = self.object.nro_operacion

        url = request.path
        if("sorteo" in url):
            tipo_adjudicacion = "sorteo"
        elif("negociacion" in url):
            tipo_adjudicacion = "negociacion"


        if request.POST["nro_cliente"] != self.get_object().nro_cliente.nro_cliente:
            raise ValidationError('Hubo un cambio malicioso de numero de cliente')
        
        
        if form.is_valid():
                sale = Ventas()

    #             # Para guardar como objeto Cliente
                nro_cliente_instance = Cliente.objects.get(nro_cliente__iexact=request.POST['nro_cliente'])
                sale.nro_cliente = nro_cliente_instance


                sale.nro_solicitud = form.cleaned_data['nro_contrato']
                sale.modalidad = form.cleaned_data['modalidad']
                sale.importe = form.cleaned_data['importe']
                sale.anticipo = form.cleaned_data['anticipo']
                sale.tasa_interes = form.cleaned_data['tasa_interes']
                sale.intereses_generados = form.cleaned_data['intereses_generados']
                sale.importe_x_cuota = form.cleaned_data['importe_x_cuota']
                sale.nro_cuotas = form.cleaned_data['nro_cuotas']
                sale.total_a_pagar = form.cleaned_data['total_a_pagar']
                sale.fecha = form.cleaned_data['fecha']
                sale.tipo_producto = form.cleaned_data['tipo_producto']
                sale.agencia = form.cleaned_data['agencia']

                # Para guardar como objeto Producto
                producto_instance = Products.objects.get(nombre__iexact=form.cleaned_data['producto'])
                sale.producto = producto_instance


                sale.save()
                sale.crearCuotas()
                sale.crearAdjudicacion(numeroAdjudicacion,tipo_adjudicacion)
                self.object.darBaja("adjudicacion")

                return redirect("users:cuentaUser",pk= self.get_object().nro_cliente.pk)

        return render(request, self.template_name, {'form': form, 'object' : self.get_object()})


class ChangePack(generic.DetailView):
    model = Ventas
    template_name = "change_pack.html"
    form_class = FormChangePAck

    def get(self,request,*args, **kwargs):
        self.object = self.get_object()
        url = request.path

        cuotasPagadas = self.object.cuotas_pagadas()
        valoresCuotasPagadas = [item["pagado"] for item in cuotasPagadas]
        sumaCuotasPagadas = sum(valoresCuotasPagadas)
        products = Products.objects.all()
        intereses = CoeficientesListadePrecios.objects.all()
        usuarios = Usuario.objects.filter(rango = "Vendedor") | Usuario.objects.filter(rango="Supervisor")
       

        json_complete=[]


        products_list = []
        for product in list(products):
            data_product = {}
            data_product["tipo_de_producto"] = product.tipo_de_producto
            data_product["nombre"] = product.nombre
            data_product["importe"] = product.importe
            data_product["paquete"] = product.paquete
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
        
        context = {
                   'form' : self.form_class,
                   'url':url,
                   "object": self.object,
                   'products': products, 
                   'usuarios': usuarios, 
                   'intereses': intereses,
                   'importe': self.object.producto.importe,
                   'producto': self.object.producto.nombre,
                   'paquete': self.object.producto.paquete,
                   'tipoProducto': self.object.producto.tipo_de_producto,  
                   'idCliente': self.object.nro_cliente.nro_cliente,
                   'dineroAnticipo' : int(sumaCuotasPagadas),
                   }
        return render(request,self.template_name,context)
    

    def post(self, request, *args, **kwargs):
        form =self.form_class(request.POST)
        self.object = self.get_object()
        


        if request.POST["nro_cliente"] != self.get_object().nro_cliente.nro_cliente:
            raise ValidationError('Hubo un cambio malicioso de numero de cliente')
        
        
        if form.is_valid():
                sale = Ventas()

    #             # Para guardar como objeto Cliente
                nro_cliente_instance = Cliente.objects.get(nro_cliente__iexact=request.POST['nro_cliente'])
                sale.nro_cliente = nro_cliente_instance


                sale.nro_solicitud = form.cleaned_data['nro_solicitud']
                sale.nro_operacion = self.object.nro_operacion
                sale.nro_orden = form.cleaned_data['nro_orden']
                sale.primer_cuota = self.object.primer_cuota
                sale.modalidad = form.cleaned_data['modalidad']
                sale.importe = form.cleaned_data['importe']
                sale.anticipo = form.cleaned_data['anticipo']
                sale.tasa_interes = form.cleaned_data['tasa_interes']
                sale.intereses_generados = form.cleaned_data['intereses_generados']
                sale.importe_x_cuota = form.cleaned_data['importe_x_cuota']
                sale.nro_cuotas = form.cleaned_data['nro_cuotas']
                sale.paquete = form.cleaned_data['paquete']
                sale.total_a_pagar = form.cleaned_data['total_a_pagar']
                sale.fecha = form.cleaned_data['fecha']
                sale.tipo_producto = form.cleaned_data['tipo_producto']


                # Para guardar como objeto Usuario
                usuario_instance = Usuario.objects.get(nombre__iexact=form.cleaned_data['vendedor'])
                sale.vendedor = usuario_instance

                # Para guardar como objeto Usuario
                supervisor_instance = Usuario.objects.get(nombre__iexact=form.cleaned_data['supervisor'])
                sale.supervisor = supervisor_instance

                # Para guardar como objeto Producto
                producto_instance = Products.objects.get(nombre__iexact=form.cleaned_data['producto'])
                sale.producto = producto_instance


                sale.save()
                sale.crearCuotas()
                sale.createBaja()
                sale.createAdjudicado()            
                self.object.darBaja("cambio de pack")

                return redirect("users:cuentaUser",pk= self.get_object().nro_cliente.pk)

        return render(request, self.template_name, {'form': form, 'object' : self.get_object()})


def viewsPDFBaja(request,pk):
    time.sleep(5)
    operacionBaja = Ventas.objects.get(id=pk)
    context ={
                "nroContrato":operacionBaja.nro_solicitud,
                "cliente": operacionBaja.nro_cliente.nombre,
                "domicilio": operacionBaja.nro_cliente.domic,
                "localidad": operacionBaja.nro_cliente.loc,
                "pack": operacionBaja.producto.paquete,
                "producto": operacionBaja.producto.nombre,
                "cantCuotasPagadas" : len(operacionBaja.cuotas_pagadas()),
                "cuotas" : operacionBaja.nro_cuotas,
                "motivo" : operacionBaja.deBaja["detalleMotivo"],
                "dineroDevolver" : operacionBaja.calcularDineroADevolver(),
                "fecha" : operacionBaja.deBaja["fecha"],
            }
            
    productoName = str(operacionBaja.producto.nombre)
    urlPDF= os.path.join(settings.PDF_STORAGE_DIR, "baja.pdf")
    
    printPDF(context,request.build_absolute_uri(),urlPDF)

    with open(urlPDF, 'rb') as pdf_file:
        response = HttpResponse(pdf_file,content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename='+productoName+'.pdf'
        return response


def requestCuotas(request):
    ventas = Ventas.objects.all()
    cuotas_data = []
    idMov=0
    for i in range(int(ventas.count())):
        for k in range(len(ventas[i].cuotas)):
            if ventas[i].cuotas[k]["status"] in ["Pagado", "Parcial"]:
                if(ventas[i].cuotas[k]["pagoParcial"]["status"]):
                    for j in range (len(ventas[i].cuotas[k]["pagoParcial"]["amount"])):
                        movimiento_dataParcial ={}
                        movimiento_dataParcial['cuota'] = ventas[i].cuotas[k]["cuota"]
                        movimiento_dataParcial['idVenta'] = ventas[i].cuotas[k]["idVenta"]

                        idMov +=1
                        movimiento_dataParcial["idMov"] =  idMov
                        movimiento_dataParcial['fecha_pago'] = ventas[i].cuotas[k]["pagoParcial"]["amount"][j]["date"]
                        movimiento_dataParcial['hora'] = ventas[i].cuotas[k]["pagoParcial"]["amount"][j]["hour"]
                        movimiento_dataParcial['pagado'] = ventas[i].cuotas[k]["pagoParcial"]["amount"][j]["value"]
                        movimiento_dataParcial["cobrador"] = ventas[i].cuotas[k]["pagoParcial"]["amount"][j]["cobrador"]
                        movimiento_dataParcial['metodoPago'] = ventas[i].cuotas[k]["pagoParcial"]["amount"][j]["metodo"]
                        movimiento_dataParcial['descuento'] = ventas[i].cuotas[k]["descuento"]
                        movimiento_dataParcial['fechaDeVencimiento'] = ventas[i].cuotas[k]["fechaDeVencimiento"]
                        movimiento_dataParcial['tipoMovimiento'] = "ingreso"
                        cuotas_data.append(movimiento_dataParcial)
                else:
                    movimiento_dataTotal = {}
                    movimiento_dataTotal['cuota'] = ventas[i].cuotas[k]["cuota"]
                    movimiento_dataTotal['idVenta'] = ventas[i].cuotas[k]["idVenta"]

                    idMov +=1
                    movimiento_dataTotal["idMov"] =  idMov
                    movimiento_dataTotal['descuento'] = ventas[i].cuotas[k]["descuento"]
                    movimiento_dataTotal['fechaDeVencimiento'] = ventas[i].cuotas[k]["fechaDeVencimiento"]
                    movimiento_dataTotal['fecha_pago'] = ventas[i].cuotas[k]["fecha_pago"]
                    movimiento_dataTotal['hora'] = ventas[i].cuotas[k]["hora"]
                    movimiento_dataTotal['pagado'] = ventas[i].cuotas[k]["pagado"]
                    movimiento_dataTotal["cobrador"] = ventas[i].cuotas[k]["cobrador"]
                    movimiento_dataTotal['metodoPago'] = ventas[i].cuotas[k]["metodoPago"]
                    movimiento_dataTotal['tipoMovimiento'] = "ingreso"
                    cuotas_data.append(movimiento_dataTotal)



    cuotas_data.reverse()
    return JsonResponse(cuotas_data, safe=False)
 
            
        
    #     return movimientosFiltrados


class Caja(generic.View):
    template_name = "caja.html"
    paginate_by = 8
    
    def filtroMovimientos_fecha(self,fechaInicio, context ,fechaFinal):
        fechaInicio_strToDatetime = datetime.datetime.strptime(fechaInicio,"%d-%m-%Y")
        fechaFinal_strToDatetime = datetime.datetime.strptime(fechaFinal,"%d-%m-%Y")
        movimientosFiltrados=[]

        for i in range(0,len(context)):
            x = context[i]["fecha_pago"]
            fecha_strToDatetime = datetime.datetime.strptime(x, "%d-%m-%Y")
            if fechaInicio_strToDatetime <= fecha_strToDatetime <= fechaFinal_strToDatetime:
                movimientosFiltrados.append(context[i])
        return movimientosFiltrados
    

    def get(self,request,*args, **kwargs):
        context ={}
        cobradores = Usuario.objects.all()

    # PARA OBTENER DESDE LA VISTA 'requestCuotas' TODAS LOS MOVIMIENTOS REALIZADOS 

        urlCuotas = reverse('sales:rc')
        base_url = request.build_absolute_uri('/')[:-1]  # Obtiene la URL base del servidor
        full_url = base_url + urlCuotas
        response = requests.get(full_url)
        movimientos =[]
        urlFilters =""
        if response.status_code == 200:
            movimientos = response.json()

            r = request.GET.copy()
            if "page" in r:
                r.pop("page")

            urlFilters = r.urlencode()

            if(len(r.keys()) > 0):
                requestToDict = request.GET.dict()
                context["urlFilters"] ="&"+urlFilters


                # Elimina los elementos con valores vacíos
                clearContext = {key: value for key, value in requestToDict.items() if value != '' and key != 'page'}
                # print(clearContext)
                if("fecha_inicial" in clearContext.keys() and "fecha_final" in clearContext.keys()):
                    contextByDateFiltered= self.filtroMovimientos_fecha(clearContext["fecha_inicial"],movimientos,clearContext["fecha_final"])

                    #Limpar el context del queryDict quitando la fecha inicial y final para que no haya errores para filtrar los otros campos
                    clearContext = {key: value for key, value in clearContext.items() if key not in ('fecha_inicial', 'fecha_final')}
                    movimientos = [item for item in contextByDateFiltered if all(item[key] == value for key, value in clearContext.items())]
                    
                else:
                    #Verifica si el elemento cumple con todas las condiciones del contexto
                    movimientos = [item for item in movimientos if all(item[key] == value for key, value in clearContext.items())]
            else:
                context["urlFilters"] =urlFilters
                
    # ------------------------------------------------------------
        paginator = Paginator(movimientos, self.paginate_by)
        page_number = request.GET.get('page',1)
        page_obj = paginator.get_page(page_number)
        
        context["movsFilters"] = page_obj 
        context["currentPage"] = page_number
        context["all_pages"] = paginator.num_pages
 
    # PARA OBTENER LA CANTIDAD DE DINERO DE CADA TIPO Y SU TOTAL
        tiposDePago = {"efectivo":"Efectivo",
                       "banco":"Banco", 
                       "posnet":"Posnet", 
                       "merPago":"Mercado Pago", 
                       "transferencia":"Transferencia"}  
        montoTotal = 0
        for clave in tiposDePago.keys():
            itemsTypePayment = list(filter(lambda x: x['metodoPago'] == tiposDePago[clave], movimientos))
            montoTypePayment = int(sum([monto['pagado'] for monto in itemsTypePayment]))
            montoTotal += montoTypePayment 
            context[clave] = montoTypePayment
        context["total"] = montoTotal

    # ------------------------------------------------------------


    # PARA OBTENER TODOS LOS COBRADORES Y ENVIARLOS POR FETCH

        listNamesCobradores =[]
        context["cobradores"] = cobradores
        for name in cobradores:
            cobrador ={}
            cobrador["name"] = name.nombre
            listNamesCobradores.append(cobrador)
        data = json.dumps(listNamesCobradores)

    # ------------------------------------------------------------

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
             # Esta es una solicitud AJAX, devuelve solo JSON
            return HttpResponse(data, content_type='application/json')
        else:
            # Esta es una solicitud normal, renderiza la plantilla HTML
            return render(request, self.template_name, context)