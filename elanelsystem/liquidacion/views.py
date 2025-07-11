import os
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import generic
from elanelsystem.settings import base as settings 
from users.utils import get_vendedores_a_cargo
from elanelsystem.views import filterDataBy_campania
from sales.mixins import TestLogin
from users.models import Usuario,Sucursal
from .models import *
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from sales.utils import formatear_moneda_sin_centavos, getAllCampaniaOfYear, getTodasCampaniasDesdeInicio, dataStructureCannons, dataStructureClientes, dataStructureVentas, dataStructureMovimientosExternos,deleteFieldsInDataStructures
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import pandas as pd
from io import BytesIO

import datetime
import json
from elanelsystem.utils import obtener_todos_los_contratos, printPDF
from .utils import (
    calcular_cantidad_ventasPropias,
    calcular_productividad_supervisor,
    calcular_ventas_supervisor,
    get_detalle_cuotas1,
    liquidaciones_countFaltas,
    liquidaciones_countTardanzas,
    get_comision_total,
    detalles_ventas_propias,
    detalle_cuota_1_adelantadas,
    detalles_ventas_x_equipo,
    detalles_cuotas_1_a_4,
    detalle_cuotas_0,
)

class LiquidacionesPanel(TestLogin,generic.View):
    
    template_name = 'liquidaciones_panel.html'
    # permission_required = "sales.my_ver_resumen"
    # login_url = "/ventas/caja/"

    def get(self,request,*args,**kwargs):
        context = {}
        return render(request, self.template_name, context)
    


def insertar_ajustes_en_detalle(detalle_actual, ajustes, user_id):
    """
    Inserta los ajustes en el dict del detalle y devuelve también el total ajustado (positivo o negativo).
    """
    ajustes_usuario = [a for a in ajustes if int(a["user_id"]) == int(user_id)]
    total_ajuste = 0

    for ajuste in ajustes_usuario:
        if ajuste["ajuste_tipo"] == "positivo":
            total_ajuste += ajuste["dinero"]
        elif ajuste["ajuste_tipo"] == "negativo":
            total_ajuste -= ajuste["dinero"]

    if ajustes_usuario:
        detalle_actual["ajustes_comision"] = ajustes_usuario
        detalle_actual["total_ajuste_comision"] = total_ajuste

    return detalle_actual, total_ajuste


class LiquidacionesComisiones(TestLogin,generic.View):
    template_name = 'comisiones.html'
    def get(self,request,*args,**kwargs):
            from sales.models import PagoCannon
            context = {}
            pago = PagoCannon.objects.filter(nro_recibo="RC-223583").first()
            # print(f"\n AAAAA\n {pago.id}")
            request.session["ajustes_comisiones"] = [] # Reiniciar posibles ajustes de la comisiones que existan
            # print(len(Ventas.objects.all()))
            context["urlPDFLiquidacion"] = reverse_lazy("liquidacion:viewPDFLiquidacion")
            # context["defaultSucursal"] = Sucursal.objects.first()
            context["sucursales"] = Sucursal.objects.all()
            context["campanias"] = getTodasCampaniasDesdeInicio()
            context["urlRequestColaboradores"] = reverse_lazy('liquidacion:requestColaboradoresWithComisiones')
            # usuarios = Usuario.objects.filter(rango__in=["Vendedor","Supervisor","Gerente sucursal"])
            return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        try:
            form = json.loads(request.body)

            campania = form["campania"]
            sucursal = form["agencia"]
            sucursalObject = Sucursal.objects.get(id=sucursal)

            datos = request.session.get('liquidacion_data', [])

            #1 --- Verificamos que exista datos para la liquidacion ---
            if not datos:
                return JsonResponse({"status": False, "message": "No existen datos para procesar la liquidacion de honorarios."}, safe=False)
                
            
            #2 --- Verificamos que no haya otra liquidacion de ese periodo y agencia ---
            if Liquidacion.objects.filter(campania=campania, agencia=sucursalObject).exists():
                return JsonResponse({"status": False, "message": "Ya existe una liquidación para esta campaña y agencia."}, safe=False)


            #3 --- Crearmos la liquidacion ---
            new_liquidacion = Liquidacion()
            new_liquidacion.agencia = sucursalObject
            new_liquidacion.campania = campania
            new_liquidacion.fecha = datetime.date.today().strftime("%d/%m/%Y")
            new_liquidacion.json_data_liquidacion = datos
            new_liquidacion.save()
          
            

            return JsonResponse({
                "status": True,
                "message": "Liquidacion completada.",
                "urlPDF": reverse_lazy('liquidacion:viewPDFLiquidacion', kwargs={"id": new_liquidacion.id}),
                "urlRedirect": reverse_lazy('liquidacion:liquidacionesPanel')
            })

        except Exception as e:
            print("[ERROR]", e)
            return JsonResponse({"status": False, "message": "Hubo un error al liquidar"}, safe=False)


def recalcular_liquidacion_data(request, campania, sucursal_id, tipo_colaborador=None):
    from users.utils import obtener_usuarios_segun_campana
    """
    Función auxiliar que encapsula el cálculo de la liquidación para 
    (campaña, sucursal) y opcionalmente filtra por tipo_colaborador.
    Devuelve: (colaboradores_list, totalDeComisiones)
    """
    sucursalObject = Sucursal.objects.get(id=int(sucursal_id))
    colaboradores = obtener_usuarios_segun_campana(campania, sucursalObject)
    
    rangos = [item.name for item in Group.objects.all()]

    tipo_colaborador_formated = tipo_colaborador.capitalize() if tipo_colaborador else None

    if tipo_colaborador_formated and tipo_colaborador_formated in rangos:
        colaboradores = colaboradores.filter(rango=tipo_colaborador_formated)

    # Tomamos todos los ajustes en sesión
    ajustes_sesion = request.session.get("ajustes_comisiones", [])

    colaboradores_list = []

    for item in colaboradores:
        if item.rango in ["Admin","Administrativa","Administrativo"] or item.is_superuser:
            continue

        # Filtrar los ajustes de este usuario
        ajustes_usuario = [
            a for a in ajustes_sesion
            if int(a["user_id"]) == item.pk
            and a["campania"] == campania
            and a["agencia"] == str(sucursalObject.id)
        ]
        
        comision_data = get_comision_total(item, campania, sucursalObject, ajustes_usuario)

        colaboradores_list.append({
            "tipo_colaborador": item.rango,
            "nombre": item.nombre,
            "id": item.pk,
            "dni": item.dni,
            "sucursal": int(sucursalObject.id),
            "campania": campania,
            "ajustes_comision": ajustes_usuario,
            "comisionTotal": comision_data["comision_total"],
            "info_total_de_comision": comision_data
        })

    totalDeComisiones = sum([user["comisionTotal"] for user in colaboradores_list])
    return (colaboradores_list, totalDeComisiones)


def requestColaboradoresWithComisiones(request):
    form = json.loads(request.body)
    
    sucursalObject = Sucursal.objects.get(id=int(form["sucursal"]))
    campania = form["campania"]
    tipo_colaborador = form["tipoColaborador"]
    
    colaboradores_list, totalDeComisiones = recalcular_liquidacion_data(
        request=request,
        campania=campania,
        sucursal_id=sucursalObject.id,
        tipo_colaborador=tipo_colaborador
    )

    request.session["campania_notCommissionable"] = campania
    request.session["sucursal_notCommissionable"] = sucursalObject.id
    request.session["liquidacion_data"] = colaboradores_list
    request.session.modified = True

    context = {"colaboradores_data": colaboradores_list,
        "totalDeComisiones": str(int(totalDeComisiones))}

    ventas_no_aptas_comisionar = Ventas.objects.filter(campania=campania, agencia=sucursalObject, is_commissionable=False)
    # print(f"[DEBUG] Ventas no aptas para comisionar: {ventas_no_aptas_comisionar}")
    
    if(len(ventas_no_aptas_comisionar) != 0):
        context["messageAlert"] = f"Tienes ventas {len(ventas_no_aptas_comisionar)} ventas no se estan comisionando"
 

    return JsonResponse(context, safe=False)


def crearAjusteComision(request):
    if request.method == "POST":
        body = json.loads(request.body)
        user_id = body.get("user_id")
        ajuste_tipo = body.get("ajuste")
        dinero = body.get("dinero")
        observaciones = body.get("observaciones", "")
        campania = body.get("campania")
        agencia = body.get("agencia")
        tipo_colaborador = body.get("tipoColaborador")

        total_comisiones = int(body.get("total_comisiones", 0))

        if not user_id or not campania or not agencia:
            return JsonResponse({"status": False, "message": "Faltan datos obligatorios"}, status=400)

        # Se arma el ajuste y se guarda en sesión
        ajuste = {
            "user_id": user_id,
            "ajuste_tipo": ajuste_tipo,
            "dinero": int(dinero) if dinero else 0,
            "observaciones": observaciones,
            "campania": campania,
            "agencia": agencia
        }
        ajustes_sesion = request.session.get("ajustes_comisiones", [])
        ajustes_sesion.append(ajuste)
        request.session["ajustes_comisiones"] = ajustes_sesion
        request.session.modified = True

        # -- OPCIONAL: recalculamos la liquidación entera para 
        # actualizar 'liquidacion_data' en la misma sesión --
        # (Si tu interfaz llama a requestColaboradoresWithComisiones luego,
        #  puedes omitir esto. Pero si quieres reflejarlo de inmediato en
        #  'liquidacion_data', se hace así:)
        colaboradores_list, totalDeComisionesRecalc = recalcular_liquidacion_data(
            request=request,
            campania=campania,
            sucursal_id=agencia,
            tipo_colaborador=tipo_colaborador  # O define si usas uno en particular
        )
        request.session["liquidacion_data"] = colaboradores_list
        request.session.modified = True

        # Cálculo de comisión final del usuario con esos nuevos ajustes
        # (si deseas devolverlo inmediatamente al front)
        sucursalObject = Sucursal.objects.get(id=agencia)
        usuario = Usuario.objects.get(pk=user_id)
        datos_comision = get_comision_total(
            usuario, 
            campania, 
            sucursalObject, 
            [ a for a in ajustes_sesion
              if int(a["user_id"]) == int(user_id)
              and a["campania"] == campania
              and a["agencia"] == agencia
            ]
        )
        comision_base = datos_comision["comision_total"]

        return JsonResponse({
            "status": True,
            "message": "Ajuste de comisión creado en sesión.",
            "user_id": user_id,
            "user_name": usuario.nombre,
            "new_comision": comision_base,
            "nuevo_total_comisiones": str(int(totalDeComisionesRecalc)),
            "ajuste_sesion": ajustes_sesion
        })

    else:
        return JsonResponse({"status": False, "message": "Método no permitido"}, status=405)


# def ajustesCoeficiente_gerente_sucursal(request):
#     if request.method == "POST":
#         body = json.loads(request.body)
#         user_id = body.get("user_id")
#         ajuste_tipo = body.get("ajuste")
#         dinero = body.get("dinero")
#         observaciones = body.get("observaciones", "")
#         campania = body.get("campania")
#         agencia = body.get("agencia")
#         tipo_colaborador = body.get("tipoColaborador")

#         total_comisiones = int(body.get("total_comisiones", 0))

#         if not user_id or not campania or not agencia:
#             return JsonResponse({"status": False, "message": "Faltan datos obligatorios"}, status=400)

#         # Se arma el ajuste y se guarda en sesión
#         ajuste = {
#             "user_id": user_id,
#             "ajuste_tipo": ajuste_tipo,
#             "dinero": int(dinero) if dinero else 0,
#             "observaciones": observaciones,
#             "campania": campania,
#             "agencia": agencia
#         }
#         ajustes_sesion = request.session.get("ajustes_comisiones", [])
#         ajustes_sesion.append(ajuste)
#         request.session["ajustes_comisiones"] = ajustes_sesion
#         request.session.modified = True

#         # -- OPCIONAL: recalculamos la liquidación entera para 
#         # actualizar 'liquidacion_data' en la misma sesión --
#         # (Si tu interfaz llama a requestColaboradoresWithComisiones luego,
#         #  puedes omitir esto. Pero si quieres reflejarlo de inmediato en
#         #  'liquidacion_data', se hace así:)
#         colaboradores_list, totalDeComisionesRecalc = recalcular_liquidacion_data(
#             request=request,
#             campania=campania,
#             sucursal_id=agencia,
#             tipo_colaborador=tipo_colaborador  # O define si usas uno en particular
#         )
#         request.session["liquidacion_data"] = colaboradores_list
#         request.session.modified = True

#         # Cálculo de comisión final del usuario con esos nuevos ajustes
#         # (si deseas devolverlo inmediatamente al front)
#         sucursalObject = Sucursal.objects.get(id=agencia)
#         usuario = Usuario.objects.get(pk=user_id)
#         datos_comision = get_comision_total(
#             usuario, 
#             campania, 
#             sucursalObject, 
#             [ a for a in ajustes_sesion
#               if int(a["user_id"]) == int(user_id)
#               and a["campania"] == campania
#               and a["agencia"] == agencia
#             ]
#         )
#         comision_base = datos_comision["comision_total"]

#         return JsonResponse({
#             "status": True,
#             "message": "Ajuste de comisión creado en sesión.",
#             "user_id": user_id,
#             "user_name": usuario.nombre,
#             "new_comision": comision_base,
#             "nuevo_total_comisiones": str(int(totalDeComisionesRecalc)),
#             "ajuste_sesion": ajustes_sesion
#         })

#     else:
#         return JsonResponse({"status": False, "message": "Método no permitido"}, status=405)


def preViewPDFLiquidacion(request):
    datos = request.session.get('liquidacion_data', {})
    print(f"\n\n [DEBUG] Datos de liquidación: \n")
    gerente = [item for item in datos if item["tipo_colaborador"] == "Supervisor"]
    print(gerente)

    # Para pasar el detalles de los movs
    contexto = []
    for item in datos:
        contexto.append({
                "tipo_colaborador": item.get("tipo_colaborador"),
                "sucursal": Sucursal.objects.filter(id = item.get("sucursal")).first().pseudonimo,
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
        liquidacion = Liquidacion.objects.get(id=id)
    except Liquidacion.DoesNotExist:
        return HttpResponse("Liquidación no encontrada", status=404)
    
    datos = liquidacion.json_data_liquidacion

    # Para pasar el detalles de los movs
    contexto = []
    for item in datos:
        contexto.append({
                "tipo_colaborador": item.get("tipo_colaborador"),
                "sucursal": Sucursal.objects.filter(id = item.get("sucursal")).first().pseudonimo,
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



def reciboPDFLiquidacionEspecifico(request):
    informeName = "Informe"
    urlPDF= os.path.join(settings.PDF_STORAGE_DIR, "liquidacion.pdf")
    printPDF({},request.build_absolute_uri(),urlPDF,"pdf_liquidacion_especifico.html","static/css/pdf_liquidacion_especifico.css")

    
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
            ventasPropias = calcular_cantidad_ventasPropias(usuario,campania,sucursalObject)
            # productividadPropia = calcular_productividad_vendedor(usuario,campania,sucursalObject)
            cuotas1Adelantadas = get_detalle_cuotas1(usuario,campania,sucursalObject)

            vendedores.append({
                'email_usuario':usuario.email,
                'nombre_usuario':usuario.nombre,
                'rango_usuario': usuario.rango,
                'cantidadVentas':ventasPropias,
                # 'productividad':productividadPropia,
                'productividad':0,

                'cuotas1Adelantadas':cuotas1Adelantadas["cantidadCuotas1"]
            })

            totalVentasSucursal_Campania += ventasPropias


        # Calcular ventas y productividad de supervisores
        totalSuper ={}
        for usuario in Usuario.objects.filter(rango="Supervisor",sucursales__in=[sucursalObject]):
                ventasPorEquipo = calcular_ventas_supervisor(usuario,campania,sucursalObject)
                productividadEquipo = calcular_productividad_supervisor(usuario,campania,sucursalObject)
                vendedoresACargo = get_vendedores_a_cargo(usuario,campania,sucursalObject)
                
                # Filtrar y ordenar vendedores a cargo
                # Extraer correos electrónicos de los vendedores a cargo
                vendedoresACargo_emails = [vendedor['email'] for vendedor in vendedoresACargo]

                # Filtrar la lista de vendedores por los correos electrónicos
                vendedoresACargo = [vendedor for vendedor in vendedores if vendedor['email_usuario'] in vendedoresACargo_emails and vendedor["rango_usuario"] == "Vendedor"]

                vendedoresACargo.sort(key=lambda x: x['cantidadVentas'], reverse=True)

                cantidadTotal_cuotas1 = sum([vendedor["cuotas1Adelantadas"] for vendedor in vendedoresACargo])

                supervisores.append({
                    'email_usuario':usuario.email,
                    'nombre_usuario':usuario.nombre,
                    'cantidadVentas': ventasPorEquipo,
                    'productividad': productividadEquipo,
                    'cuotas_1_total': cantidadTotal_cuotas1,
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
        # "vendedoresACargo": get_vendedores_a_cargo(colaborador,),
        "tardanzasAusencias": colaborador.faltas_tardanzas,
        "horaSucursal": sucursalObject.hora_apertura,
        "countFaltas": liquidaciones_countFaltas(colaborador),
        "countTardanzas": liquidaciones_countTardanzas(colaborador),
        "fechaHoy":datetime.date.today().strftime("%d/%m/%Y"),

        } 
        for colaborador in colaboradores]
    return JsonResponse({"colaboradores_data": colaboradoresDict} , safe=False)


# def newAusenciaTardanza(request):
#     form =json.loads(request.body)
#     try:
#         colaborador= form["colaborador"]
#         fecha= form["fecha"]
#         tipoEvento = form["tipoEvento"]
#         hora = form["hora"] if tipoEvento == "Tardanza" else ""

#         campania = obtener_ultima_campania()
#         colaboradorObject = Usuario.objects.get(email=colaborador)

#         colaboradorObject.faltas_tardanzas.append({
#             "tipoEvento": tipoEvento, 
#             "fecha": fecha, 
#             "hora": hora, 
#             "campania": campania
#         })
#         colaboradorObject.save()

#         response_data = {
#             "countFaltas": liquidaciones_countFaltas(colaboradorObject),
#             "countTardanzas": liquidaciones_countTardanzas(colaboradorObject),
#             "tipoEvento": tipoEvento,
#             "fecha": fecha,
#             "hora": hora,
#             "status": True
#         }
#         return JsonResponse(response_data, safe=False)
    
#     except Exception as e:
#         print(e)
#         return JsonResponse({"status": False, "errorMessage": "Ocurrio un error al guardar"},safe=False)
    

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


class DetallesComisionesView(generic.View):
    template_name = 'detalle_comisiones.html'

    

    def get(self, request, tipo_slug):
        # Obtén los datos del modelo basado en el slug
        sucursal = request.GET.get("agencia") if request.GET.get("agencia") else str(Sucursal.objects.first().id)
        campania = request.GET.get("campania") if request.GET.get("campania") else ""

        print(request)
        MODELOS = {
            'cuotas_1': dataStructureCannons(sucursal),
            'ventas': dataStructureVentas(sucursal),
        }

        datos = MODELOS.get(tipo_slug)

        # Definir atributos a mostrar según el modelo
        datos = filterDataBy_campania(datos,campania) if campania != "" else datos
        if tipo_slug == "ventas":
            attrs = ["nro_operacion", "fecha", "nro_cliente", "nombre_de_cliente", "agencia", "nro_cuotas","campania", "cantidad_chances","total_por_contrato_formated","importe_formated", "interes_generado_formated","total_a_pagar_formated","dinero_entregado_formated","dinero_restante_formated","cuota_comercial_formated",'producto', 'paquete', 'vendedor', 'supervisor']

        elif tipo_slug == "cuotas_1":
            cuota_comercial = None
            for d in datos:
                if d['cuota']['data'] == "Cuota 2": 
                    cuota_comercial = int(d['cuota_comercial']['data'])

            for d in datos:
                d["cuota_comercial"] = {
                    "data": f"${formatear_moneda_sin_centavos(cuota_comercial)}",
                    "verbose_name": "Cuota Comercial"
                }
                # fecha_pago = datetime.datetime.strptime(formatear_dd_mm_yyyy_h_m(d["fecha"]), "%d/%m/%Y %H:%M").()
                # if(d["fecha"]){

                # }
                d["comision"] = {
                    "data": f"${formatear_moneda_sin_centavos(round(cuota_comercial * 0.10, 0))}",
                    "verbose_name": "Comisión (10%)"
                }
            datos = [cuota for cuota in datos if cuota["cuota"]["data"] == "Cuota 1" and cuota["estado"]["data"] == "Pagado" ]
            # print(datos)
            attrs = ["nro_operacion","agencia","campania","nro_del_cliente", "nombre_del_cliente", "cuota", "fecha_de_vencimiento", "fecha","fecha_inscripcion", "dias_de_diferencia","campaniaPago", "cuota_comercial","comision","metodoPagoAlias","vendedor", "supervisor", "estado"]
        
        else:
            attrs = []  # Por defecto no mostrar atributos si no se definen

        # Filtrar los datos según los atributos definidos
        datos_filtrados = [
            {attr: obj[attr] for attr in attrs if attr in obj}
            for obj in datos
        ]

        # datos_filtrados = []
        request.session['datos'] = {'data': datos_filtrados, 'tipo': tipo_slug}

        print(datos)


        # Paginación
        page = request.GET.get('page', 1)
        paginator = Paginator(datos_filtrados, 20)  # 20 elementos por página

        try:
            data_paginated = paginator.page(page)
        except PageNotAnInteger:
            data_paginated = paginator.page(1)
        except EmptyPage:
            data_paginated = paginator.page(paginator.num_pages)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'data': list(data_paginated),  # Serializa la página actual
                'has_next': data_paginated.has_next(),
                'has_previous': data_paginated.has_previous(),
                'next_page': data_paginated.next_page_number() if data_paginated.has_next() else None,
                'previous_page': data_paginated.previous_page_number() if data_paginated.has_previous() else None,
                'page': data_paginated.number,
                'total_pages': paginator.num_pages,
            })

        # Renderizar la plantilla con los datos y atributos
        return render(
            request, 
            self.template_name, 
            {
                'tipo': tipo_slug,
                'data': data_paginated,
                'sucursales': Sucursal.objects.all(),
                "campanias": getTodasCampaniasDesdeInicio()
                # 'sucursalDefault': Sucursal.objects.first()
            }
        )


def export_excel_detalle_comisionado(request):
    from sales.utils import exportar_excel2
    if request.method == "POST":
        try:
            body       = json.loads(request.body)
            user       = Usuario.objects.get(pk=body["user_id"])
            campania   = body["campania"]
            agencia    = Sucursal.objects.get(pk=body["agencia_id"])
        except Exception as e:
            return JsonResponse({"error": "Parámetros inválidos"}, status=400)
        
        sheets = {}

        # 1) Siempre: Ventas propias
        ventas_propias = detalles_ventas_propias(agencia,campania,user)
    
        sheets["Ventas propias"] = [
            {
                "Agencia": v["agencia"],
                "Contrato": v["contrato"],
                "Cliente": v["nombre_cliente"],
                "Campaña": v["campana"],
                "Fecha inscripcion": v["fecha_inscripcion"],
                "Nro cuotas": v["nro_cuotas"],
                "Importe": v["importe"],
                "Producto": v["producto"],
                "Tipo de producto": v["tipo_producto"],
                "Vendedor": v["vendedor"],
                "Supervisor": v["supervisor"],
            }
            for v in ventas_propias
        ]


        # 2) Siempre: Cuotas 1
        cuotas1 = detalle_cuota_1_adelantadas(agencia,campania,user)
        sheets["Cuotas 1 adelantadas"] = []
        for c in cuotas1: 
            venta= Ventas.objects.filter(id=c["venta_id"]).first()
            dict_data = {
                "Agencia": c["agencia"],
                "Contrato": c["contrato"],
                "Cliente": c["nombre_cliente"],
                "Fecha inscripcion":c["fecha_inscripcion_venta"],
                "Fecha de pago": c["fecha_pago"],
                "Dias de diferencia": c["dias_diff"],
                "Nro cuota": c["nro_cuota"],
                "Importe de pago": c["monto"],
                "Importe cuota comercial": int(venta.cuotas[4]["total"] / len(venta.cantidadContratos)),
                "Producto": c["producto"],
                "Tipo de producto": c["tipo_producto"],
                "Vendedor": c["vendedor"],
                "Supervisor": c["supervisor"],
            }
            sheets["Cuotas 1 adelantadas"].append(dict_data)

        rol = user.rango.lower()

        # 4) Si es supervisor o superior: agrega Ventas del equipo
        if rol == "supervisor":
            ventas_x_equipo = detalles_ventas_x_equipo(agencia,campania,user)
            sheets["Ventas propias"] = [
            {
                "Agencia": v["agencia"],
                "Contrato": v["contrato"],
                "Cliente": v["nombre_cliente"],
                "Campaña": v["campana"],
                "Fecha inscripcion": v["fecha_inscripcion"],
                "Nro cuotas": v["nro_cuotas"],
                "Importe": v["importe"],
                "Producto": v["producto"],
                "Tipo de producto": v["tipo_producto"],
                "Vendedor": v["vendedor"],
                "Supervisor": v["supervisor"],
            }
            for v in ventas_x_equipo
        ]

        # 5) Si es gerente sucursal: agrega dos hojas más
        if rol == "gerente sucursal":

            cuotas_0_x_region = detalle_cuotas_0(user,campania)

            sheets["Cuotas 0"] = [
            {
                "Agencia": c["agencia"],
                "Contrato": c["contrato"],
                "Cliente": c["nombre_cliente"],
                "Fecha inscripcion":c["fecha_inscripcion_venta"],
                "Fecha de pago": c["fecha_pago"],
                "Nro cuota": c["nro_cuota"],
                "Importe": c["monto"],
                "Producto": c["producto"],
                "Tipo de producto": c["tipo_producto"],
                "Vendedor": c["vendedor"],
                "Supervisor": c["supervisor"],
            }
                for c in cuotas_0_x_region
            ]


            cuotas_1a4_x_region = detalles_cuotas_1_a_4(agencia,campania,user)
            sheets["Cuotas 1 - 4"] = []
            for c in cuotas_1a4_x_region:
                venta = Ventas.objects.filter(id=c["venta_id"]).first()
                dict_data = {
                    "Agencia": c["agencia"],
                    "Contrato": c["contrato"],
                    "Cliente": c["nombre_cliente"],
                    "Fecha inscripcion":c["fecha_inscripcion_venta"],
                    "Fecha de pago": c["fecha_pago"],
                    "Nro cuota": c["nro_cuota"],
                    "Importe de pago": c["monto"],
                    "Importe cuota comercial": int(venta.cuotas[4]["total"] / len(venta.cantidadContratos)),
                    "Producto": c["producto"],
                    "Tipo de producto": c["tipo_producto"],
                    "Vendedor": c["vendedor"],
                    "Supervisor": c["supervisor"],
                }

                sheets["Cuotas 1 - 4"].append(dict_data)

        # llamo al formateador central
        filename_prefix = f"Detalle de {user.nombre} _ {campania.replace(' ','')}"
        return exportar_excel2(sheets, filename_prefix)
    
