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

import datetime
import json
from .utils import (
    liquidaciones_countFaltas,
    liquidaciones_countTardanzas,
    obtener_ultima_campania,
    searchSucursalFromStrings,
    getComisionTotal,
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
        try:
            context = {}
            context["urlPDFLiquidacion"] = reverse_lazy("liquidacion:viewPDFLiquidacion")
            lastCampania = obtener_ultima_campania()
            context["defaultSucursal"] = Sucursal.objects.first()
            context["sucursales"] = Sucursal.objects.all()
            context["urlRequestColaboradores"] = reverse_lazy('liquidacion:requestColaboradores')
            usuarios = Usuario.objects.filter(rango__in=["Vendedor","Supervisor","Gerente sucursal"])
            admins = Usuario.objects.filter(rango = "Admin")
            context["colaboradores"] = [{"nombre": user.nombre, "comisionTotal":getComisionTotal(user,lastCampania,request.user.sucursal)["total_comisionado"]} for user in usuarios]
            context["admins"] = admins
            context["totalDeComisiones"] = sum([user["comisionTotal"] for user in context["colaboradores"]])
        
            return render(request, self.template_name, context)
        except:
            context = {}
            return render(request, self.template_name, context)
    
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



def requestColaboradores(request):
    paramsDict = (request.GET).dict()
    lastCampania = obtener_ultima_campania()

    sucursalDefault = request.user.sucursal.localidad +", "+request.user.sucursal.provincia
    sucursalString = request.GET.get('sucursal',sucursalDefault)
    sucursalObject = searchSucursalFromStrings(sucursalString)

    tipo_colaborador = request.GET.get('tipoColaborador',False)
    colaboradores = Usuario.objects.all()
    rangos = [item.name for item in Group.objects.all()]

    if(sucursalString):
        colaboradores = colaboradores.filter(sucursal = sucursalObject)
    if(tipo_colaborador):
        if(tipo_colaborador not in  rangos):
            colaboradores = Usuario.objects.filter(sucursal = sucursalObject)
        else:
            colaboradores = colaboradores.filter(rango = tipo_colaborador)

    

    colaboradores_list = [{"tipo_colaborador":item.rango, "nombre": item.nombre, "id": item.pk, "dni":item.dni,"comisionTotal": getComisionTotal(item,lastCampania,sucursalObject)["total_comisionado"],"detalle": getComisionTotal(item,lastCampania,sucursalObject)["detalle"]} for item in colaboradores if item.rango != "Admin"]
    
    totalDeComisiones = sum([user["comisionTotal"] for user in colaboradores_list])
    request.session["liquidacion_data"] = {"colaboradores_list":colaboradores_list, "sucursal": sucursalString, "fecha":datetime.date.today().strftime("%d-%m-%Y")}

    return JsonResponse({"data": paramsDict,"colaboradores": colaboradores_list,"totalDeComisiones": totalDeComisiones} , safe=False)

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
        sucursalDelUsuario = request.user.sucursal
        supervisores = Usuario.objects.filter(rango="Supervisor") if str(sucursalDelUsuario) == "Todas, Todas" else Usuario.objects.filter(sucursal=sucursalDelUsuario, rango="Supervisor")

        context = {
            "supervisores": supervisores,
            "amountTardanza": 350,
            "amountFalta": 2000,
            "fecha_hoy":datetime.date.today().strftime("%d-%m-%Y"),
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if(HttpResponse.status_code == 200):
            colaborador= json.loads(request.body)["colaborador"]
            fecha= json.loads(request.body)["fecha"]
            hora= json.loads(request.body)["hora"]
            descuento= json.loads(request.body)["descuento"]
            campania = obtener_ultima_campania()

            colaboradorObject = Usuario.objects.get(email=colaborador)
            colaboradorObject.faltas_tardanzas.append({"fecha":fecha,"hora":hora,"descuento":descuento,"campania":campania})
            colaboradorObject.save()
            
            countFaltas = liquidaciones_countFaltas(colaboradorObject)
            countTardanzas = liquidaciones_countTardanzas(colaboradorObject)

            response_data = {"countFaltas": countFaltas,"countTardanzas": countTardanzas,"fecha":fecha,"hora": hora,"descuento":descuento}
            return JsonResponse(response_data, safe=False)
        else:
            response_data = {"status": "500", "create": False}
            return JsonResponse(response_data, safe=False)
        
