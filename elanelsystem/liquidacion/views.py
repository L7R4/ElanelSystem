import os
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import generic
from elanelsystem import settings
from sales.mixins import TestLogin
from sales.utils import printPDFLiquidacion
from users.models import Usuario,Sucursal
from .models import *
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from sales.utils import getAllCampaniaOfYear
import datetime
import json
from .utils import (
    liquidaciones_countFaltas,
    liquidaciones_countTardanzas,
    obtener_ultima_campania,
    searchSucursalFromStrings,
    getComisionTotal,
    getDetalleComisionPorCantVentasPropias
)

class LiquidacionesPanel(TestLogin,generic.View):
    
    template_name = 'liquidaciones_panel.html'
    # permission_required = "sales.my_ver_resumen"
    # login_url = "/ventas/caja/"

    def get(self,request,*args,**kwargs):
        context = {}
        return render(request, self.template_name, context)
    
    
class LiquidacionesComisiones(TestLogin,generic.View):
    template_name = 'comisiones.html'
    def get(self,request,*args,**kwargs):
        # try:
            context = {}
            context["urlPDFLiquidacion"] = reverse_lazy("liquidacion:viewPDFLiquidacion")
            lastCampania = obtener_ultima_campania()
            context["defaultSucursal"] = Sucursal.objects.first()
            context["sucursales"] = Sucursal.objects.all()
            context["campanias"] = getAllCampaniaOfYear()
            context["urlRequestColaboradores"] = reverse_lazy('liquidacion:requestColaboradoresWithComisiones')
            usuarios = Usuario.objects.filter(rango__in=["Vendedor","Supervisor","Gerente sucursal"])
            admins = Usuario.objects.filter(rango = "Admin")
            # context["colaboradores"] = [{"nombre": user.nombre, "comisionTotal":getComisionTotal(user,lastCampania,request.user.sucursal)["total_comisionado"]} for user in usuarios]
            context["admins"] = admins
            # context["totalDeComisiones"] = sum([user["comisionTotal"] for user in context["colaboradores"]])
        
            return render(request, self.template_name, context)
        # except:
        #     context = {}
        #     return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        tipo_colaborador= json.loads(request.body)["tipo_colaborador"]
        datos = request.session.get('liquidacion_data', {})

        # CONTINUAR
        if(tipo_colaborador == "Vendedor"):
            newLiquidacion = LiquidacionVendedor()
            pass
        elif(tipo_colaborador == "Supervisor"):
            newLiquidacion = LiquidacionSupervisor()
            pass
        elif(tipo_colaborador == "Gerente sucursal"):
            newLiquidacion = LiquidacionGerenteSucursal()
            pass
        elif(tipo_colaborador == "Admin"):
            newLiquidacion = LiquidacionAdmin()
            pass



def requestColaboradoresWithComisiones(request):
    form =json.loads(request.body)
    
    sucursalObject = Sucursal.objects.get(pseudonimo = form["sucursal"])
    campania = form["campania"]

    tipo_colaborador = form["tipoColaborador"]
    colaboradores = Usuario.objects.filter(sucursales__in=[sucursalObject])

    rangos = [item.name for item in Group.objects.all()]

    if(tipo_colaborador and tipo_colaborador in rangos):
        colaboradores = colaboradores.filter(rango = tipo_colaborador)

    colaboradores_list = [{
        "tipo_colaborador":item.rango, 
        "nombre": item.nombre, "id": item.pk, 
        "dni":item.dni,
        "detalle": getComisionTotal(item,campania,sucursalObject)["detalle"],
        "comisionTotal": getComisionTotal(item,campania,sucursalObject)["total_comisionado"],
        } 
        for item in colaboradores if item.rango != "Admin"]
    
    totalDeComisiones = sum([user["comisionTotal"] for user in colaboradores_list])
    # request.session["liquidacion_data"] = {"colaboradores_list":colaboradores_list, "sucursal": sucursalString, "fecha":datetime.date.today().strftime("%d-%m-%Y")}
    # return JsonResponse({"colaboradores_data": colaboradores_list,"totalDeComisiones": totalDeComisiones} , safe=False)

    return JsonResponse({"colaboradores_data": colaboradores_list, "totalDeComisiones": totalDeComisiones} , safe=False)

def viewPDFLiquidacion(request):
    datos = request.session.get('liquidacion_data', {})

    # Para pasar el detalles de los movs
    for item in datos:
        datos_modificado = {
                "tipo_colaborador": item.get("tipo_colaborador"),
                "nombre": item.get("nombre"),
                "comisionTotal": item.get("comisionTotal"),
                "detalle": item.get("detalle"),
            
            }
        if(item.tipo_colaborador == "Supervisor"):
            pass
   

    informeName = "Informe"
    urlPDF= os.path.join(settings.PDF_STORAGE_DIR, "liquidacion.pdf")
    
    printPDFLiquidacion({"data":datos_modificado},request.build_absolute_uri(),urlPDF)

    
    with open(urlPDF, 'rb') as pdf_file:
        response = HttpResponse(pdf_file,content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename='+informeName+'.pdf'
        return response

class LiquidacionesRanking(TestLogin,generic.View):
    template_name = 'liquidaciones_ranking.html'

    # permission_required = "sales.my_ver_resumen"
    # login_url = "/ventas/caja/"

    def get(self,request,*args,**kwargs):
        context = {}
        return render(request, self.template_name, context)
    
    
class LiquidacionesDetallesVentas(TestLogin,generic.View):
    template_name = 'detalleVentasLiquidaciones.html'

    # permission_required = "sales.my_ver_resumen"
    # login_url = "/ventas/caja/"

    def get(self,request,*args,**kwargs):
        context = {}
        return render(request, self.template_name, context)
    
    
class LiquidacionesDetallesCuotasAdelantadas(TestLogin,generic.View):
    template_name = 'detalleCuotasAdelantadas.html'

    # permission_required = "sales.my_ver_resumen"
    # login_url = "/ventas/caja/"

    def get(self,request,*args,**kwargs):
        context = {}
        return render(request, self.template_name, context)
    
  
class LiquidacionesAusenciaYTardanzas(TestLogin,generic.View):
    template_name = 'liquidaciones_ausencias_tardanzas.html'

    def get(self,request,*args,**kwargs):

        sucursalDelUsuario = request.user.sucursales.all()[0]
        supervisores = Usuario.objects.filter(rango="Supervisor", sucursales__in=[sucursalDelUsuario])
        sucursalesDisponibles = request.user.sucursales.all()
        rangosDisponibles = ["Vendedor", "Administracion local", "Supervisor", "Gerente sucursal"]
        context = {
            "supervisores": supervisores,
            "sucursales": sucursalesDisponibles,
            "rangos": rangosDisponibles,
            "urlRequestColaboradores": reverse_lazy('liquidacion:requestColaboradores_TardanzasAusencias'),
            "urlNewItem": reverse_lazy('liquidacion:newAusenciaTardanza'),
        }

        return render(request, self.template_name, context)
        
def requestColaboradores_TardanzasAusencias(request):
    form =json.loads(request.body)
    sucursalObject = Sucursal.objects.get(pseudonimo = form["sucursal"])
    rango = form["rango"]
    colaboradores = Usuario.objects.filter(sucursales__in=[sucursalObject],rango=rango)
    # rangosDisponibles = {"Vendedor": "Vendedores/as", "Administracion local": "Administrativos/as", "Supervisor": "Supervisores/as", "Gerente sucursal": "Gerentes/as"  }

    colaboradoresDict = [{
        "nombre": colaborador.nombre,
        "rango": colaborador.rango,
        "email": colaborador.email,
        "vendedoresACargo": colaborador.vendedores_a_cargo,
        "tardanzasAusencias": colaborador.faltas_tardanzas,
        "horaSucursal": sucursalObject.hora_apertura,
        "countFaltas": liquidaciones_countFaltas(colaborador),
        "countTardanzas": liquidaciones_countTardanzas(colaborador),
        "fechaHoy":datetime.date.today().strftime("%d/%m/%Y"),

        } 
        for colaborador in colaboradores]
    return JsonResponse({"colaboradores_data": colaboradoresDict} , safe=False)

def newAusenciaTardanza(request):
    form =json.loads(request.body)
    try:
        colaborador= form["colaborador"]
        fecha= form["fecha"]
        tipoEvento = form["tipoEvento"]
        hora = form["hora"] if tipoEvento == "Tardanza" else ""

        campania = obtener_ultima_campania()
        colaboradorObject = Usuario.objects.get(email=colaborador)

        colaboradorObject.faltas_tardanzas.append({
            "tipoEvento": tipoEvento, 
            "fecha": fecha, 
            "hora": hora, 
            "campania": campania
        })
        colaboradorObject.save()

        response_data = {
            "countFaltas": liquidaciones_countFaltas(colaboradorObject),
            "countTardanzas": liquidaciones_countTardanzas(colaboradorObject),
            "tipoEvento": tipoEvento,
            "fecha": fecha,
            "hora": hora,
            "status": True
        }
        return JsonResponse(response_data, safe=False)
    
    except Exception as e:
        print(e)
        return JsonResponse({"status": False, "errorMessage": "Ocurrio un error al guardar"},safe=False)