from django.forms import ValidationError
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .mixins import TestLogin
from .models import ArqueoCaja, Ventas,CoeficientesListadePrecios,MovimientoExterno
from .forms import FormChangePAck, FormCreateVenta, FormCreateAdjudicacion
from users.forms import CreateClienteForm
from users.models import Cliente, Sucursal,Usuario,Key
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
import locale
import requests
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .utils import printPDF, printPDFinformePostVenta, printPDFtitularidad,printPDFarqueo,filterMovs, filtroMovimientos_fecha,printPDFinforme, searchSucursalFromStrings, sendEmailPDF, clearNameSucursal
from liquidacion.utils import getAdelantos
from collections import defaultdict
import elanelsystem.settings as settings



class Resumen(TestLogin,PermissionRequiredMixin,generic.View):
    permission_required = "sales.my_ver_resumen"
    # login_url = "/ventas/caja/"
    template_name = 'resumen.html'

    def get(self,request,*args,**kwargs):
        print(request.user.get_all_permissions())

        ventas = Ventas.objects.all()
        context = {
            "ventas" : ventas,
        }
        # print(context)
        return render(request, self.template_name, context)
    
    def handle_no_permission(self):
        return redirect("users:list_customers")
        
            
#region API CRM
def requestMovimientosCRM(request):
    cuotas_data = requestCuotas(request)
    movimientosExternos = requestMovimientosExternos(request)
    
    # Combinar datos de cuotas y movimientos externos
    all_movimientos = json.loads(cuotas_data.content) + json.loads(movimientosExternos.content)
    all_movimientosTidy = sorted(all_movimientos, key=lambda x: datetime.datetime.strptime(x['fecha_pago'], '%d/%m/%Y %H:%M'),reverse=True)
   
    response_data ={
        "request": request.GET,
        "movs": all_movimientosTidy
    }
    movs = filterMovs(response_data["movs"],response_data["request"])
    
    # Crear un diccionario por mes y sumar los ingresos
    ingresos_por_mes = defaultdict(float)
    egresos_por_mes = defaultdict(float)
    for mov in movs:
        tipo_movimiento = mov.get('tipoMovimiento')
        monto_pagado = mov.get('pagado', 0)
        fecha_pago = mov.get('fecha_pago')

        if tipo_movimiento == 'Ingreso' and fecha_pago:
            mes = int(fecha_pago.split('-')[1])
            ingresos_por_mes[mes] += monto_pagado
        elif tipo_movimiento == 'Egreso' and fecha_pago:
            mes = int(fecha_pago.split('-')[1])
            egresos_por_mes[mes] += monto_pagado
    # Crear la lista final de sumas por mes
    sumasIngreso_por_mes = [ingresos_por_mes.get(mes, 0) for mes in range(1, 13)]
    sumasEgreso_por_mes = [egresos_por_mes.get(mes, 0) for mes in range(1, 13)]
    
    return JsonResponse({"sumasIngreso_por_mes": sumasIngreso_por_mes,"sumasEgreso_por_mes":sumasEgreso_por_mes}, safe=False)
#endregion
    
class CrearVenta(TestLogin,generic.DetailView):
    model = Cliente
    template_name = "create_sale.html"
    form_class = FormCreateVenta

    def get(self,request,*args, **kwargs):
        self.object = self.get_object()

        customers = Cliente.objects.all()
        products = Products.objects.all()
        sucursalString = clearNameSucursal(request.user.sucursal)  
        usuarios = ""

        if(sucursalString == "Todas, Todas"):
            usuarios = Usuario.objects.filter(rango__in=["Vendedor","Supervisor"])
        else:
            usuarios = Usuario.objects.filter(rango__in=["Vendedor","Supervisor"],sucursal = request.user.sucursal)
            
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
        self.object = self.get_object()
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
                sale.agencia = request.user.sucursal

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
                return redirect("users:cuentaUser",pk= self.get_object().pk)

        return render(request, self.template_name, {'form': form, 'object' : self.get_object()})
    

class DetailSale(TestLogin,generic.DetailView):
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
        
        context["changeTitularidad"] = list(reversed(self.object.cambioTitularidadField))
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
            motivoObservacion = json.loads(request.body)["observacion"]
            responsable = request.user.nombre
            self.object.darBaja("cliente",porcentage,motivoDetalle,motivoObservacion,responsable)
            response_data = {
                'success': True,
                'urlPDF': reverse("sales:bajaPDF", args=[self.object.pk]),
                'urlUser': reverse("users:cuentaUser", args=[self.object.nro_cliente.pk])
            }
           
            return JsonResponse(response_data, safe=False)
            

        # PARA GENERAR EL PDF CON LA BAJA SIN LA CLAVE
        elif(request.method == 'POST' and ("porcentage" == requestKey)):
            porcentage = json.loads(request.body)["porcentage"]
            if(int(porcentage) == porcentageValido):
                motivoDetalle = json.loads(request.body)["motivo"]
                motivoObservacion = json.loads(request.body)["observacion"]
                responsable = request.user.nombre
                self.object.darBaja("cliente",porcentage,motivoDetalle,motivoObservacion,responsable)
                response_data = {
                'success': True,
                'urlPDF': reverse("sales:bajaPDF", args=[self.object.pk]),
                'urlUser': reverse("users:cuentaUser", args=[self.object.nro_cliente.pk])
            }
                return JsonResponse(response_data, safe=False)
            else:
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


class CreateAdjudicacion(TestLogin,generic.DetailView):
    model = Ventas
    template_name = "create_adjudicacionSorteo.html"
    form_class = FormCreateAdjudicacion
    
    def get(self,request,*args, **kwargs):
        self.object = self.get_object()
        url = request.path
        cuotasPagadas = self.object.cuotas_pagadas()

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

        cuotasPagadas = self.object.cuotas_pagadas()
        valoresCuotasPagadas = [item["total"] for item in cuotasPagadas]
        sumaCuotasPagadas = sum(valoresCuotasPagadas)
        url = request.path
        if("sorteo" in url):
            tipo_adjudicacion = "sorteo"
        elif("negociacion" in url):
            tipo_adjudicacion = "negociacion"
            sumaCuotasPagadas = sumaCuotasPagadas * 0.5

       
        
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
                self.object.darBaja("adjudicacion",0,"","",request.user.nombre)

                return redirect("users:cuentaUser",pk= self.get_object().nro_cliente.pk)
        
        
        aumentoPorcentaje = self.object.importe * 0.1 
        importeNuevo = aumentoPorcentaje + self.object.importe
        context = {
            'form': form,
            'object': self.get_object(),
            'tipoProducto': self.object.producto.tipo_de_producto,
            'tipoDeAdjudicacion' : tipo_adjudicacion.upper(),
            'producto': self.object.producto.nombre,
            'importeNuevo': int(importeNuevo),
            'dineroAnticipo' : int(sumaCuotasPagadas)
        }
        return render(request, self.template_name, context)


class ChangePack(TestLogin,generic.DetailView):
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
                self.object.darBaja("cambio de pack",0,"","",request.user.nombre)

                return redirect("users:cuentaUser",pk= self.get_object().nro_cliente.pk)
        context = {
            'form': form,
            'object': self.get_object(),
            'tipoProducto': self.object.producto.tipo_de_producto,
            'producto': self.object.producto.nombre,
        }
        return render(request, self.template_name, context)


def viewsPDFBaja(request,pk):
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
                "observacion" : operacionBaja.deBaja["observacion"],
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

def viewPDFTitularidad(request,pk,idCambio):
    operacionTitu = Ventas.objects.get(id=pk)
    newCustomer = operacionTitu.cambioTitularidadField[idCambio]["pkNewCustomer"]
    oldCustomer = operacionTitu.cambioTitularidadField[idCambio]["oldCustomer"]

    # Establece el idioma local en español
    locale.setlocale(locale.LC_TIME, 'es_AR.utf8')

    dateNow = datetime.date.today().strftime("%d de %B de %Y")
    context ={
                "fechaNow": dateNow,
                "oldCustomer": oldCustomer,
                "nroOperacion":operacionTitu.nro_operacion,
                "cliente": Cliente.objects.get(id=newCustomer).nombre,
                "domicilio": Cliente.objects.get(id=newCustomer).domic,
                "dni": Cliente.objects.get(id=newCustomer).dni,
                "localidad": Cliente.objects.get(id=newCustomer).loc,
                "provincia": Cliente.objects.get(id=newCustomer).prov,
                "estado_civil" : Cliente.objects.get(id=newCustomer).estado_civil,
                "fecha_nac" : Cliente.objects.get(id=newCustomer).fec_nacimiento,
                "ocupacion" : Cliente.objects.get(id=newCustomer).ocupacion,
                "telefono" : Cliente.objects.get(id=newCustomer).tel,
            }
            
    titularName = "Cambio de titular: " + str(Cliente.objects.get(id=newCustomer).nombre) + str(operacionTitu.nro_orden)
    urlPDF= os.path.join(settings.PDF_STORAGE_DIR, "titularidad.pdf")
    
    printPDFtitularidad(context,request.build_absolute_uri(),urlPDF)

    with open(urlPDF, 'rb') as pdf_file:
        response = HttpResponse(pdf_file,content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename='+titularName+'.pdf'
        return response

def viewPDFArqueo(request,pk):
    
    # Establece el idioma local en español
    locale.setlocale(locale.LC_TIME, 'es_AR.utf8')
    arqueo = ArqueoCaja.objects.get(id=pk)

    # Para pasar los movimientos del dia
    cuotas_data = requestCuotas(request)
    movimientosExternos = requestMovimientosExternos(request)
    
    # Combinar datos de cuotas y movimientos externos
    all_movimientos = json.loads(cuotas_data.content) + json.loads(movimientosExternos.content)
    all_movimientosTidy = sorted(all_movimientos, key=lambda x: datetime.datetime.strptime(x['fecha_pago'], '%d/%m/%Y %H:%M'),reverse=True)
   
    movsToday = list(filter(lambda x: x["fecha_pago"][:10] == arqueo.fecha,all_movimientosTidy))

    movsDetalles = [
        {
            "Moviem.": d.get("tipoMovimiento", "-"),
            "Compro.": "---" if d.get("tipoComprobante") is None or d.get("tipoComprobante") == "null" else d.get("tipoComprobante", "---"),
            "Nro Comprob.": "---" if d.get("nroComprobante") is None or d.get("nroComprobante") == "null" else d.get("nroComprobante", "---"),
            "Denominacion": "---" if d.get("denominacion") is None or d.get("denominacion") == "null" else d.get("denominacion", "---"),
            "T. de ID": "---" if d.get("tipoIdentificacion") is None or d.get("tipoIdentificacion") == "null" else d.get("tipoIdentificacion", "---"),
            "Nro de ID.": "---" if d.get("nroIdentificacion") is None or d.get("nroIdentificacion") == "null" else d.get("nroIdentificacion", "---"),
            "Sucursal": d.get("sucursal", "-"),
            "Moneda": "---" if d.get("tipoMoneda") is None or d.get("tipoMoneda") == "null" else d.get("tipoMoneda", "---"),
            "Dinero": d.get("pagado", "-"),
            "Metodo de pago": d.get("metodoPago", "-"),
            "Ente recau.": d.get("ente", "-"),
            "Concepto": d.get("concepto", "-"),
            "Fecha": d.get("fecha_pago", "-"),
        }
        for d in movsToday
    ]
    
    # Para pasar el resumen de tipos de pagos
    resumenData = {}
    tiposDePago = {"efectivo":"Efectivo",
                       "banco":"Banco", 
                       "posnet":"Posnet", 
                       "merPago":"Mercado Pago", 
                       "transferencia":"Transferencia"}  
        
    montoTotal = 0
    for clave in tiposDePago.keys():
        itemsTypePayment = list(filter(lambda x: x['metodoPago'] == tiposDePago[clave], movsToday))
        montoTypePaymentEgreso = sum([monto['pagado'] for monto in itemsTypePayment if monto['tipoMovimiento'] == 'Egreso'])
        montoTypePaymentIngreso = sum([monto['pagado'] for monto in itemsTypePayment if monto['tipoMovimiento'] == 'Ingreso'])
        montoTypePayment = montoTypePaymentIngreso - montoTypePaymentEgreso
        montoTotal += montoTypePayment 
        resumenData[clave] = montoTypePayment
    resumenData["total"] = montoTotal

    # Para pasar los datos del arqueo 
    arqueoData ={
                "fecha": arqueo.fecha,
                "agencia": arqueo.agencia,
                "responsable":arqueo.responsable,
                "admin": arqueo.admin,
                "totalPlanilla": arqueo.totalPlanilla,
                "totalSegunDiarioCaja": arqueo.totalSegunDiarioCaja,
                "diferencia": arqueo.diferencia,
                "observaciones": arqueo.observaciones,
                "p2000": arqueo.detalle["p2000"],
                "p1000": arqueo.detalle["p1000"],
                "p500": arqueo.detalle["p500"],
                "p200": arqueo.detalle["p200"],
                "p100": arqueo.detalle["p100"],
                "p50": arqueo.detalle["p50"],
                "p20": arqueo.detalle["p20"],
                "p10": arqueo.detalle["p10"],
                "p5": arqueo.detalle["p5"],
                "p2": arqueo.detalle["p2"],
            }
            
    arqueoName = "Arqueo de caja del: " + str(arqueo.fecha)
    urlPDF= os.path.join(settings.PDF_STORAGE_DIR, "arqueo.pdf")
    
    printPDFarqueo({"arqueoData": arqueoData, "movsData": movsDetalles,"resumenData": resumenData},request.build_absolute_uri(),urlPDF)

    # Para enviar PDF
    fechaYHoraHoy = datetime.datetime.today().strftime("%d/%m/%Y %H:%M")

    url_referer = request.META.get('HTTP_REFERER', '')
    if reverse("sales:oldArqueos") not in url_referer:
        sendEmailPDF("",os.path.join(settings.BASE_DIR, 'pdfs/arqueo.pdf'),"Cierre de caja del: " + fechaYHoraHoy)
    


    with open(urlPDF, 'rb') as pdf_file:
        response = HttpResponse(pdf_file,content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename='+arqueoName+'.pdf'
        return response

def requestMovimientosExternos(request):
    cuotas_data = requestCuotas(request)
    movsExternosList = []

    # Obtener movimientos externos
    movsExternos = MovimientoExterno.objects.all()

    # Obtener la longitud de cuotas_data
    cuotas_data_length = len(json.loads(cuotas_data.content)) + 1
    
    for idx,mov in enumerate(movsExternos):
        movDict = {
            "idMov": cuotas_data_length + idx,
            "tipoMovimiento": mov.movimiento,
            "tipoComprobante": mov.tipoComprobante,
            "nroComprobante": mov.nroComprobante,
            "denominacion": mov.denominacion,
            "tipoIdentificacion": mov.tipoIdentificacion,
            "nroIdentificacion": mov.nroIdentificacion,
            "tipoMoneda": mov.tipoMoneda,
            "sucursal": mov.agencia.localidad + ", " + mov.agencia.provincia,
            "pagado": mov.dinero,
            "metodoPago": mov.metodoPago,
            "ente": mov.ente,
            "concepto": mov.concepto,
            "fecha_pago": mov.fecha+" "+ mov.hora
            }
        movsExternosList.append(movDict)
    return JsonResponse(movsExternosList,safe=False)

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
                        movimiento_dataParcial['nro_operacion'] = ventas[i].cuotas[k]["nro_operacion"]
                        nOpe = ventas[i].cuotas[k]["nro_operacion"]
                        nroCliente = Ventas.objects.filter(nro_operacion = nOpe)
                        movimiento_dataParcial['nroCliente'] = nroCliente[0].nro_cliente.nro_cliente
                        movimiento_dataParcial['nombreCliente'] = nroCliente[0].nro_cliente.nombre
                        movimiento_dataParcial["sucursal"] = ventas[i].agencia.localidad + ", " + ventas[i].agencia.provincia

                        idMov +=1
                        movimiento_dataParcial["idMov"] =  idMov
                        movimiento_dataParcial['fecha_pago'] = ventas[i].cuotas[k]["pagoParcial"]["amount"][j]["date"] + " " + ventas[i].cuotas[k]["pagoParcial"]["amount"][j]["hour"]
                        movimiento_dataParcial['pagado'] = ventas[i].cuotas[k]["pagoParcial"]["amount"][j]["value"]
                        movimiento_dataParcial["cobrador"] = ventas[i].cuotas[k]["pagoParcial"]["amount"][j]["cobrador"]
                        movimiento_dataParcial['metodoPago'] = ventas[i].cuotas[k]["pagoParcial"]["amount"][j]["metodo"]
                        movimiento_dataParcial['descuento'] = ventas[i].cuotas[k]["descuento"]
                        movimiento_dataParcial['fechaDeVencimiento'] = ventas[i].cuotas[k]["fechaDeVencimiento"]
                        movimiento_dataParcial['tipoMovimiento'] = "Ingreso"
                        cuotas_data.append(movimiento_dataParcial)
                else:
                    movimiento_dataTotal = {}
                    movimiento_dataTotal['cuota'] = ventas[i].cuotas[k]["cuota"]
                    movimiento_dataTotal['nro_operacion'] = ventas[i].cuotas[k]["nro_operacion"]
                    nOpe = ventas[i].cuotas[k]["nro_operacion"]
                    nroCliente = Ventas.objects.filter(nro_operacion = nOpe)
                    movimiento_dataTotal['nroCliente'] = nroCliente[0].nro_cliente.nro_cliente
                    movimiento_dataTotal['nombreCliente'] = nroCliente[0].nro_cliente.nombre
                    movimiento_dataTotal["sucursal"] = ventas[i].agencia.localidad + ", " + ventas[i].agencia.provincia 

                    idMov +=1
                    movimiento_dataTotal["idMov"] =  idMov
                    movimiento_dataTotal['descuento'] = ventas[i].cuotas[k]["descuento"]
                    movimiento_dataTotal['fechaDeVencimiento'] = ventas[i].cuotas[k]["fechaDeVencimiento"]
                    movimiento_dataTotal['fecha_pago'] = ventas[i].cuotas[k]["fecha_pago"]+ " " + ventas[i].cuotas[k]["hora"]
                    movimiento_dataTotal['pagado'] = ventas[i].cuotas[k]["pagado"]
                    movimiento_dataTotal["cobrador"] = ventas[i].cuotas[k]["cobrador"]
                    movimiento_dataTotal['metodoPago'] = ventas[i].cuotas[k]["metodoPago"]
                    movimiento_dataTotal['tipoMovimiento'] = "Ingreso"
                    cuotas_data.append(movimiento_dataTotal)



    cuotas_data.reverse()
    return JsonResponse(cuotas_data, safe=False)

def viewsPDFInforme(request):
    # Establece el idioma local en español
    # locale.setlocale(locale.LC_TIME, 'es_AR.utf8')
    datos = request.session.get('informe_data', {})

    # Para pasar el detalles de los movs

    datos_modificado = [
        {
            "Moviem.": d.get("tipoMovimiento", "-"),
            "Compro.": "---" if d.get("tipoComprobante") is None or d.get("tipoComprobante") == "null" else d.get("tipoComprobante", "---"),
            "Nro Comprob.": "---" if d.get("nroComprobante") is None or d.get("nroComprobante") == "null" else d.get("nroComprobante", "---"),
            "Denominacion": "---" if d.get("denominacion") is None or d.get("denominacion") == "null" else d.get("denominacion", "---"),
            "T. de ID": "---" if d.get("tipoIdentificacion") is None or d.get("tipoIdentificacion") == "null" else d.get("tipoIdentificacion", "---"),
            "Nro de ID.": "---" if d.get("nroIdentificacion") is None or d.get("nroIdentificacion") == "null" else d.get("nroIdentificacion", "---"),
            "Sucursal": d.get("sucursal", "-"),
            "Moneda": "---" if d.get("tipoMoneda") is None or d.get("tipoMoneda") == "null" else d.get("tipoMoneda", "---"),
            "Dinero": d.get("pagado", "-"),
            "Metodo de pago": d.get("metodoPago", "-"),
            "Ente recau.": d.get("ente", "-"),
            "Concepto": d.get("concepto", "-"),
            "Fecha": d.get("fecha_pago", "-"),
        }
        for d in datos
    ]
    # Para pasar el resumen de tipos de pagos 

    metodosPagosResumen={}
    tiposDePago = {"efectivo":"Efectivo",
                   "banco":"Banco", 
                   "posnet":"Posnet", 
                   "merPago":"Mercado Pago", 
                   "transferencia":"Transferencia"}  
    
    montoTotal = 0
    for clave in tiposDePago.keys():
        itemsTypePayment = list(filter(lambda x: x['metodoPago'] == tiposDePago[clave], datos))
        montoTypePaymentEgreso = sum([monto['pagado'] for monto in itemsTypePayment if monto['tipoMovimiento'] == 'Egreso'])
        montoTypePaymentIngreso = sum([monto['pagado'] for monto in itemsTypePayment if monto['tipoMovimiento'] == 'Ingreso'])
        montoTypePayment = montoTypePaymentIngreso - montoTypePaymentEgreso
        montoTotal += montoTypePayment 
        metodosPagosResumen[clave] = montoTypePayment
    metodosPagosResumen["total"] = montoTotal

    informeName = "Informe"
    urlPDF= os.path.join(settings.PDF_STORAGE_DIR, "liquidacion.pdf")
    
    # printPDFinforme({"data":datos_modificado},request.build_absolute_uri(),urlPDF)
    printPDFinforme({"data":datos_modificado,"metodosPagosResumen":metodosPagosResumen},request.build_absolute_uri(),urlPDF)

    
    with open(urlPDF, 'rb') as pdf_file:
        response = HttpResponse(pdf_file,content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename='+informeName+'.pdf'
        return response


def viewPDFInformeAndSend(request):
    # Para enviar PDF
    fechaYHoraHoy = datetime.datetime.today().strftime("%d/%m/%Y %H:%M")
    sendEmailPDF("valerossi2004@hotmail.com",os.path.join(settings.BASE_DIR, 'pdfs/informe.pdf'),"Informe del: " + fechaYHoraHoy)
    return viewsPDFInforme(request)

    
def requestMovimientos(request):
    cuotas_data = requestCuotas(request)
    movimientosExternos = requestMovimientosExternos(request)
    # Combinar datos de cuotas y movimientos externos
    all_movimientos = json.loads(cuotas_data.content) + json.loads(movimientosExternos.content)
    all_movimientosTidy = sorted(all_movimientos, key=lambda x: datetime.datetime.strptime(x['fecha_pago'], '%d/%m/%Y %H:%M'),reverse=True)
   
    response_data ={
        "request": request.GET,
        "movs": all_movimientosTidy
    }
    movs = filterMovs(response_data["movs"],response_data["request"])


    # PARA PASAR LOS FILTROS ACTIVADOS
    paramsDict = (request.GET).dict()
    FILTROS_EXISTENTES = (
        ("tipoMovimiento","Tipo de movimiento"),
        ("metodoPago", "Metodo de pago"),
        ("fecha_inicial","Fecha inicial"),
        ("fecha_final","Fecha final"),
        ("cobrador","Cobrador"),
        ("sucursal","Sucursal"),
    )
    clearContext = {key: value for key, value in paramsDict.items() if value != '' and key != 'page'}

    # Extrae las tuplas segun los querys filtrados en clearContext
    filtros_activados = list(filter(lambda x: x[0] in clearContext, FILTROS_EXISTENTES))
    
    # Por cada tupla se coloca de llave el valor 1 y se extrae el valor mediante su key de clearContext ( Por eso es [x[0]] )
    # Es lo mismo que decir clearContext["metodoPago"], etc, etc
    filtros = list(map(lambda x: {x[1]: clearContext[x[0]]}, filtros_activados))
    request.session["informe_data"] = movs
   

    # Paginación
    page = request.GET.get('page')
    items_per_page = 10  # Número de elementos por página
    paginator = Paginator(movs, items_per_page)

    try:
        movs = paginator.page(page)
    except PageNotAnInteger:
        movs = paginator.page(1)
    except EmptyPage:
        movs = paginator.page(paginator.num_pages)
    #-----------------------------------------------------

    return JsonResponse({"data": list(movs), "numbers_pages": paginator.num_pages,"filtros":filtros}, safe=False)

def updateDinero(request):
    if request.method == "GET":
        cuotas_data = requestCuotas(request)
        movimientosExternos = requestMovimientosExternos(request)
       
        # Combinar datos de cuotas y movimientos externos
        all_movimientos = json.loads(cuotas_data.content) + json.loads(movimientosExternos.content)
        all_movimientosTidy = sorted(all_movimientos, key=lambda x: datetime.datetime.strptime(x['fecha_pago'], '%d/%m/%Y %H:%M'),reverse=True)
    
        response_data ={
            "request": request.GET,
            "movs": all_movimientosTidy
        }
        movs = filterMovs(response_data["movs"],response_data["request"])


        context={}
        tiposDePago = {"efectivo":"Efectivo",
                       "banco":"Banco", 
                       "posnet":"Posnet", 
                       "merPago":"Mercado Pago", 
                       "transferencia":"Transferencia"}  
        
        montoTotal = 0
        for clave in tiposDePago.keys():
            itemsTypePayment = list(filter(lambda x: x['metodoPago'] == tiposDePago[clave], movs))
            montoTypePaymentEgreso = sum([monto['pagado'] for monto in itemsTypePayment if monto['tipoMovimiento'] == 'Egreso'])
            montoTypePaymentIngreso = sum([monto['pagado'] for monto in itemsTypePayment if monto['tipoMovimiento'] == 'Ingreso'])
            montoTypePayment = montoTypePaymentIngreso - montoTypePaymentEgreso

            montoTotal += montoTypePayment 
            context[clave] = montoTypePayment
        context["total"] = montoTotal


        return JsonResponse(context, safe=False)

def createNewMov(request):
    if request.method == 'POST':
        newMov = MovimientoExterno()
        movimiento = request.POST.get("movimiento")
        if movimiento == 'Ingreso':
            newMov.movimiento=movimiento
            newMov.agencia = request.user.sucursal
            newMov.tipoMoneda = request.POST.get('tipoMoneda')
            newMov.dinero= float(request.POST.get('dinero'))
            newMov.metodoPago= request.POST.get('metodoPago')
            newMov.concepto= request.POST.get('concepto')
            newMov.ente= request.POST.get('ente')
            newMov.fecha=datetime.datetime.today().strftime("%d/%m/%Y")
            newMov.hora = datetime.datetime.now().time().strftime("%H:%M")
        else:
            newMov.movimiento=movimiento
            newMov.agencia = request.user.sucursal
            newMov.tipoIdentificacion=request.POST.get('tipoIdentificacion')
            newMov.nroIdentificacion=request.POST.get('nroIdentificacion')
            newMov.tipoComprobante=request.POST.get('tipoComprobante')
            newMov.nroComprobante=request.POST.get('nroComprobante')
            newMov.denominacion=request.POST.get('denominacion')
            newMov.dinero= float(request.POST.get('dinero'))
            newMov.metodoPago= request.POST.get('metodoPago')
            newMov.concepto= request.POST.get('concepto')
            newMov.ente= request.POST.get('ente')
            newMov.fecha=datetime.datetime.today().strftime("%d/%m/%Y")
            newMov.hora = datetime.datetime.now().time().strftime("%H:%M")
            if(request.POST.get('adelanto_premio') == "premio"):
                newMov.premio= True
            elif(request.POST.get('adelanto_premio') == "adelanto"):
                newMov.adelanto = True
                
        newMov.save()
        return JsonResponse({'status': 'success', 'message': 'Movimiento creado exitosamente'})
        

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


class Caja(TestLogin,generic.View):
    template_name = "caja.html"
    FILTROS_EXISTENTES = (
        ("tipoMovimiento","Tipo de movimiento"),
        ("metodoPago", "Metodo de pago"),
        ("fecha_inicial","Fecha inicial"),
        ("fecha_final","Fecha final"),
        ("cobrador","Cobrador"),
        ("sucursal","Sucursal"),
    )

    def get(self,request,*args, **kwargs):
        context ={}
        context["cobradores"] = Usuario.objects.all()
        context["sucursales"] = Sucursal.objects.all()
        # print(os.path.join(settings.BASE_DIR, "templates/mailPlantilla.html"))
        paramsDict = (request.GET).dict()
        clearContext = {key: value for key, value in paramsDict.items() if value != '' and key != 'page'}

        
        # Extrae las tuplas segun los querys filtrados en clearContext
        filtros_activados = list(filter(lambda x: x[0] in clearContext, self.FILTROS_EXISTENTES))

        # Por cada tupla se coloca de llave el valor 1 y se extrae el valor mediante su key de clearContext ( Por eso es [x[0]] )
        # Es lo mismo que decir clearContext["metodoPago"], etc, etc
        context["filtros"] = list(map(lambda x: {x[1], clearContext[x[0]]}, filtros_activados))


        return render(request, self.template_name, context)
        

class CierreCaja(TestLogin,generic.View):

    template_name = 'cierreDeCaja.html'

    def get(self,request,*args,**kwargs):
        context = {}
        json_data = requestMovimientos(request)
        movsData = json.loads(json_data.content)
        
        today = datetime.date.today().strftime("%d/%m/%Y %H:%M")
        movimientosHoy = filtroMovimientos_fecha(str(today),movsData["data"],str(today))

        # FILTRA LOS MOVIMIENTOS SEGUN SE TIPO DE MOVIMIENTO
        movimientos_Ingreso_Hoy = list(filter(lambda x: x["tipoMovimiento"] == "Ingreso" and x["metodoPago"] == "Efectivo", movimientosHoy))
        movimientos_Egreso_Hoy = list(filter(lambda x:x["tipoMovimiento"] == "Egreso" and x["metodoPago"] == "Efectivo", movimientosHoy))

        # SUMA EL TOTAL DE SEGUN EL TIPO DE MOVIMIENTO
        montoTotal_Ingreso_Hoy = sum([item["pagado"] for item in movimientos_Ingreso_Hoy])
        montoTotal_Egreso_Hoy = sum([item["pagado"] for item in movimientos_Egreso_Hoy])

        if len(movimientosHoy) == 0:
            context["movs"] = 0
        else:
            context["movs"] = int(montoTotal_Ingreso_Hoy - montoTotal_Egreso_Hoy)

        context["sucursal"] = request.user.sucursal
        context["sucursales"] = Sucursal.objects.all()
        context["fecha"] =  datetime.date.today().strftime("%d/%m/%Y")
        context["admin"]= request.user
        
        return render(request, self.template_name, context)
    

    def post(self,request,*args,**kwargs):
        context= {}
        arqueo = ArqueoCaja()
        BILLETES = [2000,1000,500,200,100,50,20,10,5,2]
        
        # OBTIENE LOS DATOS----------------------------------------------------
        sucursal = request.POST.get("sucursal")
        localidad_buscada, provincia_buscada = map(str.strip, sucursal.split(","))
        sucursalObject = Sucursal.objects.get(localidad = localidad_buscada, provincia = provincia_buscada)

        fecha =  datetime.date.today().strftime("%d/%m/%Y")
        admin = request.user
        responsable = request.POST.get("responsable")
        totalSegunDiarioCaja = request.POST.get("saldoSegunCaja")
        observaciones = request.POST.get("observaciones")
        
        total=0
        for b in BILLETES:
            billeteCantidad = request.POST.get("p"+ str(b))
            if(billeteCantidad == ""):
                billeteCantidad = 0
            
            billeteItem = {}
            billeteItem["cantidad"] = int(billeteCantidad)
            billeteItem["importeTotal"] = int(billeteCantidad) * b
            total += int(billeteCantidad) * b
            arqueo.detalle["p"+ str(b)] = billeteItem

        # ---------------------------------------------------------------------

        # COLOCA LOS DATOS ---------------------------------------------------
        
        arqueo.agencia = sucursalObject
        arqueo.fecha = fecha
        arqueo.admin = admin
        arqueo.responsable = responsable
        arqueo.totalPlanilla = total
        arqueo.totalSegunDiarioCaja = float(totalSegunDiarioCaja)
        arqueo.diferencia = total - float(totalSegunDiarioCaja)
        arqueo.observaciones = observaciones
        # ---------------------------------------------------------------------

        arqueo.save()

        response_data = {
            'success': True,
            'urlPDF': reverse("sales:arqueoPDF", args=[ArqueoCaja.objects.latest('pk').pk]),
            'urlCaja': reverse("sales:caja")
        }
        
        return JsonResponse(response_data, safe=False)


class ChangeTitularidad(TestLogin,generic.DetailView):
    template_name = 'changeTitularidad.html'
    model = Ventas


    def get(self,request,*args, **kwargs):
        self.object = self.get_object()
        customers = Cliente.objects.all()
        context = {
            "customers": customers,
            "object": self.object,
        }

        customers_list = []
        for c in customers:
            data_customer = {}
            data_customer["pk"] = c.pk
            data_customer["nombre"] = c.nombre
            data_customer["dni"] = c.dni
            data_customer["tel"] = c.tel
            data_customer["loc"] = c.loc
            data_customer["prov"] = c.prov
            customers_list.append(data_customer)
        data = json.dumps(customers_list)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponse(data, 'application/json')
        return render(request, self.template_name,context)

    def post(self,request,*args,**kwargs):
        self.object = self.get_object()

        if(request.method == 'POST'):
            try:
                newCustomer = request.POST.get("newCustomer")
                dniNewCustomer = Cliente.objects.all().filter(dni=newCustomer)

                # Agrega el antiguo cliente a la lista de clientes anteriores
                # self.object.clientes_anteriores.asdd(self.object.nro_cliente)
                

                # Coloca los datos del cambio de titularidad
                lastCuota = self.object.cuotas_pagadas()
                self.object.createCambioTitularidad(lastCuota[-1],request.user.nombre,self.object.nro_cliente.nombre,dniNewCustomer[0].nombre,self.object.nro_cliente.pk,dniNewCustomer[0].pk)

                # Actualiza el dueño de la venta
                self.object.nro_cliente = dniNewCustomer[0]

                self.object.save()

                return redirect("sales:detail_sale",pk= self.get_object().pk)
            except ValueError as vE:
                customers = Cliente.objects.all()
                context = {
                    "customers": customers,
                    "object": self.object,
                    "error": vE,
                }
                return render(request,self.template_name,context)
   
    
class CrearUsuarioYCambiarTitu(TestLogin,generic.DetailView):
    model = Ventas
    template_name = 'crearclienteycambiar.html'
    form_class = CreateClienteForm

    def get(self, request,*args, **kwargs):
        self.object = self.get_object()
        context = {}
        context["customer_number"] = Cliente.returNro_Cliente
        context["object"] = self.object
        context['form'] = self.form_class

        return render(request, self.template_name, context)
    

    def post(self,request,*args,**kwargs):
        form =self.form_class(request.POST)
        self.object = self.get_object()
        
        if form.is_valid():
                customer = Cliente()
                customer.nro_cliente = form.cleaned_data["nro_cliente"]
                customer.nombre = form.cleaned_data['nombre']
                customer.dni = form.cleaned_data['dni']
                customer.domic = form.cleaned_data['domic']
                customer.loc = form.cleaned_data['loc']
                customer.prov = form.cleaned_data['prov']
                customer.cod_postal = form.cleaned_data['cod_postal']
                customer.tel = form.cleaned_data['tel']
                customer.estado_civil = form.cleaned_data['estado_civil']
                customer.fec_nacimiento = form.cleaned_data['fec_nacimiento']
                customer.ocupacion = form.cleaned_data['ocupacion']
                customer.save()


                # Coloca los datos del cambio de titularidad
                lastCuota = self.object.cuotas_pagadas()
                self.object.createCambioTitularidad(lastCuota[-1],request.user.nombre,self.object.nro_cliente.nombre,customer.nombre,self.object.nro_cliente.pk,customer.pk)
                self.object.nro_cliente = customer
                self.object.save()
                
                return redirect("sales:detail_sale",pk= self.get_object().pk)

        else:
            print(form)
            context = {}
            context["customer_number"] = Cliente.returNro_Cliente
            context["object"] = self.object
            context['form'] = self.form_class
            return render(request, self.template_name, context)


class OldArqueosView(TestLogin,generic.View):
    model = ArqueoCaja
    template_name= "listaDeArqueos.html"

    def get(self,request,*args, **kwargs):
        arqueos = ArqueoCaja.objects.filter(agencia = request.user.sucursal)
        context = {
            "arqueos": reversed(arqueos)
        }
        arqueos_list = []
        for a in arqueos:
            data_arqueo = {}
            data_arqueo["pk"] = a.pk
            data_arqueo["sucursal"] = a.agencia
            data_arqueo["fecha"] = a.fecha
            data_arqueo["admin"] = a.admin
            data_arqueo["responsable"] = a.responsable
            data_arqueo["totalPlanilla"] = a.totalPlanilla
            arqueos_list.append(data_arqueo)

        arqueos_list.reverse()
        data = json.dumps(arqueos_list)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponse(data, 'application/json')
        return render(request, self.template_name,context)
    

class PostVenta(TestLogin,generic.View):
    template_name = 'postVenta.html'

    def get(self,request,campania,*args,**kwargs):
        ventas = Ventas.objects.filter(campania=campania)
        sucursalDefault = searchSucursalFromStrings("Sucursal central")

        auditorias_realidas = Ventas.objects.filter(agencia=sucursalDefault,campania=campania,auditoria__0__realizada=True)
        auditorias_pendientes = Ventas.objects.filter(agencia=sucursalDefault,campania=campania,auditoria__0__realizada=False)

        auditorias_realidas_list = list(auditorias_realidas.values())
        auditorias_aprobadas = len(list(filter(lambda x: x["auditoria"][-1]["grade"] == True,auditorias_realidas_list)))
        auditorias_desaprobadas = len(list(filter(lambda x: x["auditoria"][-1]["grade"] == False,auditorias_realidas_list)))
        

        context = {
            "ventas": ventas,
            "amountVentas": ventas.count(),
            "sucursalDefault": Sucursal.objects.get(pseudonimo="Sucursal central"),
            "sucursales": Sucursal.objects.all(),
            "auditorias_pendientes": len(auditorias_pendientes),
            "auditorias_realizadas": len(auditorias_realidas),
            "auditorias_aprobadas": auditorias_aprobadas,
            "auditorias_desaprobadas": auditorias_desaprobadas,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if(HttpResponse.status_code == 200):
            response_data = {}
            grade = request.POST.get("grade")
            id_venta = request.POST.get("idVenta")
            venta = Ventas.objects.get(pk=id_venta)
            comentarios = request.POST.get("comentarioInput")

            new_dict_auditoria = {}
            ultimaAuditoria = venta.auditoria[-1]
            if grade == "a":
                    new_dict_auditoria["grade"] = True
                    response_data["message"] = "Auditoria aprobada exitosamente"
                    response_data["status"] = True
                    response_data["grade"] = True
                    response_data["gradeString"] = "Aprobada"

            elif grade == "d":
                new_dict_auditoria["grade"]  = False
                response_data["message"] = "Auditoria desaprobada exitosamente"
                response_data["grade"] = False
                response_data["status"] = True
                response_data["gradeString"] = "Desaprobada"

            new_dict_auditoria["realizada"] = True
            new_dict_auditoria["comentarios"] = comentarios
            new_dict_auditoria["fecha_hora"] = datetime.datetime.today().strftime("%d/%m/%Y %H:%M")

            if ultimaAuditoria["version"] == 0:
                new_dict_auditoria["version"] = 1
                venta.auditoria[0] = new_dict_auditoria
            else:
                new_dict_auditoria["version"] = ultimaAuditoria["version"] + 1
                venta.auditoria.append(new_dict_auditoria)
            venta.save()
            
            response_data["comentarioString"] = comentarios
            response_data["fechaString"] = datetime.datetime.today().strftime("%d/%m/%Y %H:%M")
            return JsonResponse(response_data, safe=False)
        else:
            response_data = {"status": False,"message": "Hubo un error al generar la auditoria"}
            return JsonResponse(response_data, safe=False)

     
def requestVentas(request):
    if(request.method == "GET"):
        sucursal = request.GET.get('sucursal')
        campaign = request.GET.get('campania')
        responseData = {"ventas": [],"resumenAuditorias":{"pendientes": 0, "realizadas":0, "aprobadas":0, "desaprobadas":0}}
        
        sucursal = searchSucursalFromStrings(sucursal)
        allVentas = Ventas.objects.filter(campania=campaign, agencia=sucursal)

        auditorias_realidas = allVentas.filter(auditoria__0__realizada=True)
        responseData["resumenAuditorias"]["realizadas"] = len(auditorias_realidas)

        auditorias_pendientes = allVentas.filter(auditoria__0__realizada=False)
        responseData["resumenAuditorias"]["pendientes"] = len(auditorias_pendientes)

        auditorias_realidas_list = list(auditorias_realidas.values())
        auditorias_aprobadas = len(list(filter(lambda x: x["auditoria"][-1]["grade"] == True,auditorias_realidas_list)))
        responseData["resumenAuditorias"]["aprobadas"] = auditorias_aprobadas

        auditorias_desaprobadas = len(list(filter(lambda x: x["auditoria"][-1]["grade"] == False,auditorias_realidas_list)))
        responseData["resumenAuditorias"]["desaprobadas"] = auditorias_desaprobadas

        for v in allVentas:
            ventaToDict = {
                "id": v.pk,
                "nroOrden": v.nro_orden,
                "campania": v.campania,
                "cliente": v.nro_cliente.nombre,
                "dni": v.nro_cliente.dni,
                "fec_insc": v.fecha,
                "tel": v.nro_cliente.tel,
                "cp": v.nro_cliente.cod_postal,
                "prov": v.nro_cliente.prov,
                "loc": v.nro_cliente.loc,
                "direc": v.nro_cliente.domic,
                "vendedor": str(v.vendedor),
                "supervisor": str(v.supervisor),
                "auditoria": v.auditoria,
            }
            responseData["ventas"].append(ventaToDict)
        request.session["postVenta_info"] = responseData

        return JsonResponse(responseData, safe=False)
    
def viewsPDFInformePostVenta(request):
    datos = request.session.get('postVenta_info', {})

    # Para pasar el detalles de los movs
    datos_modificado = [
        {
            "Nro Orden": d.get("nroOrden", "---"),
            "Camp": d.get("campania","---"),
            "Cliente": d.get("cliente","---"),
            "DNI": d.get("dni","---"),
            "Fec insc": d.get("fec_insc","---"),
            "Tel": d.get("tel","---"),
            "CP": d.get("cp", "---"),
            "Prov": d.get("prov","---"),
            "Loc": d.get("loc", "---"),
            "Direc": d.get("direc", "---"),
            "Vendedor": d.get("vendedor", "---"),
            "Supervisor": d.get("supervisor", "---"),
            "Auditoria": d.get("auditoria", "---"),
        }
        for d in datos["ventas"]
    ]

    # CONFIG PARA VER PDF 
    informeName = "Informe Post-Venta"
    urlPDF= os.path.join(settings.PDF_STORAGE_DIR, "postVentaInforme.pdf")
    
    printPDFinformePostVenta({"data":datos_modificado},request.build_absolute_uri(),urlPDF)

    
    with open(urlPDF, 'rb') as pdf_file:
        response = HttpResponse(pdf_file,content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename='+informeName+'.pdf'
        return response
