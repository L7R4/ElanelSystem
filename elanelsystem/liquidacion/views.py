import os
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import generic
from elanelsystem import settings
from sales.mixins import TestLogin
from users.models import Usuario,Sucursal
from .models import *
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from sales.utils import getAllCampaniaOfYear, getTodasCampaniasDesdeInicio
import datetime
import json
from elanelsystem.utils import printPDF
from .utils import (
    calcular_productividad_supervisor,
    calcular_productividad_vendedor,
    calcular_ventas_supervisor,
    calcular_ventas_vendedor,
    getCuotas1,
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
            context["campanias"] = getTodasCampaniasDesdeInicio()
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
        try:
            form = json.loads(request.body)

            campania=form["campania"]
            sucursal=form["agencia"]
            sucursalObject = Sucursal.objects.get(pseudonimo=sucursal)
            ventas = Ventas.objects.filter(campania=campania, agencia=sucursalObject)
            ventas = [
                venta for venta in ventas
                if len(venta.auditoria) > 0 and venta.auditoria[-1].get("grade") is True
            ]
            datos = request.session.get('liquidacion_data', {})

            
            #region Liquidacion por tipo de colaborador 
            vendedores = []
            supervisores = []
            gerentes = []
            for item in datos:

                if(item["tipo_colaborador"] == "Vendedor"):
                    newLiquidacion = LiquidacionVendedor()
                    newLiquidacion.usuario = Usuario.objects.get(pk=item["id"])
                    newLiquidacion.campania = campania
                    newLiquidacion.cant_ventas = item["info_total_de_comision"]["cant_ventas_propia"]
                    newLiquidacion.productividad = item["info_total_de_comision"]["productividad_propia"]
                    newLiquidacion.total_comisionado = item["comisionTotal"]
                    newLiquidacion.detalle = item["info_total_de_comision"]["detalle"]
                    newLiquidacion.save()
                    vendedores.append(newLiquidacion)

                elif(item["tipo_colaborador"] == "Supervisor"):
                    newLiquidacion = LiquidacionSupervisor()
                    newLiquidacion.usuario = Usuario.objects.get(pk=item["id"])
                    newLiquidacion.campania = campania
                    newLiquidacion.cant_ventas = item["info_total_de_comision"]["cant_ventas_fromRol"]
                    newLiquidacion.productividad = item["info_total_de_comision"]["productividad_fromRol"]
                    newLiquidacion.total_comisionado = item["comisionTotal"]
                    newLiquidacion.detalle = item["info_total_de_comision"]["detalle"]
                    newLiquidacion.save()
                    supervisores.append(newLiquidacion)

                elif(item["tipo_colaborador"] == "Gerente sucursal"):
                    newLiquidacion = LiquidacionGerenteSucursal()
                    newLiquidacion.usuario = Usuario.objects.get(pk=item["id"])
                    newLiquidacion.sucursal = sucursalObject
                    newLiquidacion.campania = campania
                    newLiquidacion.total_comisionado = item["comisionTotal"]
                    newLiquidacion.detalle = item["info_total_de_comision"]["detalle"]
                    newLiquidacion.save()
                    gerentes.append(newLiquidacion)

            #endregion  

            # #region Liquidacion completa
            new_liquidacionCompleta = LiquidacionCompleta()
            new_liquidacionCompleta.fecha = datetime.date.today().strftime("%d/%m/%Y")
            new_liquidacionCompleta.campania = campania
            new_liquidacionCompleta.sucursal = sucursalObject
            new_liquidacionCompleta.total_liquidado = sum([item["comisionTotal"] for item in datos])
            new_liquidacionCompleta.total_proyectado = sum([venta.importe for venta in ventas])
            new_liquidacionCompleta.total_recaudado = new_liquidacionCompleta.total_proyectado - new_liquidacionCompleta.total_liquidado
            new_liquidacionCompleta.cant_ventas = len(ventas)
            new_liquidacionCompleta.save()
            new_liquidacionCompleta.detalle_vendedores.add(*vendedores)
            new_liquidacionCompleta.detalle_supervisores.add(*supervisores)
            new_liquidacionCompleta.detalle_gerentes.add(*gerentes)
            new_liquidacionCompleta.save()
            #endregion
            

                
            response_data = {
                "urlPDF": reverse_lazy('liquidacion:viewPDFLiquidacion', kwargs={"id": new_liquidacionCompleta.id}),
                "urlRedirect": reverse_lazy('liquidacion:liquidacionesPanel'),
                "status": True
            }
            
            return JsonResponse(response_data, safe=False)  
             
        except Exception as e:
            print(e)
            return JsonResponse({"status": False, "message": f"Hubo un error al liquidar"}, safe=False)  


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
        "sucursal": form["sucursal"],
        "campania": campania,
        "comisionTotal": getComisionTotal(item,campania,sucursalObject)["total_comisionado"],
        "info_total_de_comision": getComisionTotal(item,campania,sucursalObject)
        } 
        for item in colaboradores if item.rango != "Admin"]
    
    totalDeComisiones = sum([user["comisionTotal"] for user in colaboradores_list])
    request.session["liquidacion_data"] = colaboradores_list

    return JsonResponse({"colaboradores_data": colaboradores_list, "totalDeComisiones": totalDeComisiones} , safe=False)


def preViewPDFLiquidacion(request):
    datos = request.session.get('liquidacion_data', {})
    # Para pasar el detalles de los movs
    contexto = []
    for item in datos:
        contexto.append({
                "tipo_colaborador": item.get("tipo_colaborador"),
                "sucursal": item.get("sucursal"),
                "fecha": datetime.date.today().strftime("%d-%m-%Y"),
                "campania": item.get("campania"),
                "nombre": item.get("nombre"),
                "info_total_de_comision": item.get("info_total_de_comision")
            
            })

    informeName = "Informe"
    urlPDF= os.path.join(settings.PDF_STORAGE_DIR, "liquidacion.pdf")
    printPDF({"data":contexto},request.build_absolute_uri(),urlPDF,"pdfForLiquidacion.html","static/css/pdfLiquidacion.css")

    
    with open(urlPDF, 'rb') as pdf_file:
        response = HttpResponse(pdf_file,content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename='+informeName+'.pdf'
        return response


def viewPDFLiquidacion(request, id):
    # Obtener la liquidación desde la base de datos
    try:
        liquidacion = LiquidacionCompleta.objects.get(id=id)
    except LiquidacionCompleta.DoesNotExist:
        return HttpResponse("Liquidación no encontrada", status=404)
    
    vendedores = liquidacion.detalle_vendedores.all()
    supervisores = liquidacion.detalle_supervisores.all()
    gerentes = liquidacion.detalle_gerentes.all()

    colaboradores = list(vendedores) + list(supervisores) + list(gerentes)

    colaboradores_list = [{
        "tipo_colaborador": item.usuario.rango,
        "nombre": item.usuario.nombre,
        "id": item.usuario.pk, 
        "dni":item.usuario.dni,
        "sucursal": liquidacion.sucursal.pseudonimo,
        "campania": liquidacion.campania,
        "comisionTotal": getComisionTotal(item.usuario,liquidacion.campania,liquidacion.sucursal)["total_comisionado"],
        "info_total_de_comision": getComisionTotal(item.usuario,liquidacion.campania,liquidacion.sucursal)
        } 
        for item in colaboradores]


    contexto = []
    for item in colaboradores_list:
        contexto.append({
                "tipo_colaborador": item.get("tipo_colaborador"),
                "sucursal": item.get("sucursal"),
                "fecha":liquidacion.fecha,
                "campania": item.get("campania"),
                "nombre": item.get("nombre"),
                "info_total_de_comision": item.get("info_total_de_comision")
            })

    informeName = f"Informe_Liquidacion_{liquidacion.id}"
    urlPDF = os.path.join(settings.PDF_STORAGE_DIR, f"liquidacion.pdf")
    print(contexto)
    printPDF({"data": contexto}, request.build_absolute_uri(), urlPDF, "pdfForLiquidacion.html", "static/css/pdfLiquidacion.css")

    
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
        defaultSucursal = Sucursal.objects.first()
        defaultCampania = getTodasCampaniasDesdeInicio()[0]

        sucursal = request.GET.get("agencia",defaultSucursal.pseudonimo)
        campania = request.GET.get("campania", defaultCampania)
        print(request.GET)

        # Obtener por request el tipo de ordenamiento que tendra los elementos
        tipoOrdenamientoVendedores = request.GET.get("tipoOrdenamientoVendedores","cantidadVentas")
        tipoOrdenamientoSupervisores = request.GET.get("tipoOrdenamientoSupervisores","cantidadVentas")


        sucursalObject = Sucursal.objects.filter(pseudonimo=sucursal).first()

        
        context["defaultSucursal"] = defaultSucursal
        context["defaultCampania"] = defaultCampania
        context["defaultOrder"] = "Cantidad de ventas"
        context["sucursales"] = Sucursal.objects.all()
        context["campaniasDisponibles"] = getTodasCampaniasDesdeInicio()

        supervisores = []
        vendedores = []
        totalVentasSucursal_Campania = 0


        # Calcular ventas y productividad de vendedores
        for usuario in Usuario.objects.filter(sucursales__in=[sucursalObject]):
            ventasPropias = calcular_ventas_vendedor(usuario,campania,sucursalObject)
            productividadPropia = calcular_productividad_vendedor(usuario,campania,sucursalObject)
            cuotas1Adelantadas = getCuotas1(usuario,campania,sucursalObject)

            vendedores.append({
                'email_usuario':usuario.email,
                'nombre_usuario':usuario.nombre,
                'rango_usuario': usuario.rango,
                'cantidadVentas':ventasPropias,
                'productividad':productividadPropia,
                'cuotas1Adelantadas':cuotas1Adelantadas["cantidadCuotas1"]
            })

            totalVentasSucursal_Campania += ventasPropias


        # Calcular ventas y productividad de supervisores
        for usuario in Usuario.objects.filter(rango="Supervisor",sucursales__in=[sucursalObject]):
                ventasPorEquipo = calcular_ventas_supervisor(usuario,campania,sucursalObject)
                productividadEquipo = calcular_productividad_supervisor(usuario,campania,sucursalObject)
                vendedoresACargo = usuario.vendedores_a_cargo
                
                # Filtrar y ordenar vendedores a cargo
                # Extraer correos electrónicos de los vendedores a cargo
                vendedoresACargo_emails = [vendedor['email'] for vendedor in usuario.vendedores_a_cargo]

                # Filtrar la lista de vendedores por los correos electrónicos
                vendedoresACargo = [vendedor for vendedor in vendedores if vendedor['email_usuario'] in vendedoresACargo_emails and vendedor["rango_usuario"] == "Vendedor"]

                vendedoresACargo.sort(key=lambda x: x['cantidadVentas'], reverse=True)


                supervisores.append({
                    'email_usuario':usuario.email,
                    'nombre_usuario':usuario.nombre,
                    'cantidadVentas': ventasPorEquipo,
                    'productividad': productividadEquipo,
                    'vendedoresACargo': vendedoresACargo
                })
        

        #Ordenar por cantidad de ventas
        vendedores.sort(key=lambda x: x[tipoOrdenamientoVendedores],reverse=True)
        supervisores.sort(key=lambda x: x[tipoOrdenamientoSupervisores],reverse=True)

        context["vendedores"] = vendedores
        context["supervisores"] = supervisores
        context["totalVentasSucursal_Campania"] = totalVentasSucursal_Campania

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'supervisores': supervisores,
                'vendedores': vendedores,
                'totalVentasSucursal_Campania': totalVentasSucursal_Campania
                },safe=False)
        
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
    

class HistorialLiquidaciones(generic.ListView):
    template_name = 'historialLiquidaciones.html'

    def get(self,request,*args,**kwargs):
        context = {}
        sucursal = request.GET.get("agencia",False)
        campania = request.GET.get("campania", False)

        filtros = {}
        if campania:
            filtros["campania"] = campania

        if sucursal:
            sucursalObject = Sucursal.objects.filter(pseudonimo=sucursal).first()
            filtros["sucursal"] = sucursalObject

        liquidacion_qs = LiquidacionCompleta.objects.all() if not filtros else LiquidacionCompleta.objects.filter(**filtros)
            
        context["sucursales"] = Sucursal.objects.all()
        context["campaniasDisponibles"] = getTodasCampaniasDesdeInicio()

        liquidaciones = [{
            "id": l.id,
            "sucursal": l.sucursal.pseudonimo,
            "campania": l.campania,
            "fecha": l.fecha,
            "cantVentas": l.cant_ventas,
            "totalProyectado": f"${l.total_proyectado}",
            "totalRecaudado": f"${l.total_recaudado}",
            "totalLiquidado": f"${l.total_liquidado}"

        } for l in liquidacion_qs]

        context["liquidaciones"] = liquidaciones

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'liquidaciones': liquidaciones
                },safe=False)
        
        return render(request, self.template_name, context)
    