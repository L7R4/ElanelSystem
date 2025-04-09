import os
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import generic
from elanelsystem import settings
from elanelsystem.views import filterDataBy_campania
from sales.mixins import TestLogin
from users.models import Usuario,Sucursal
from .models import *
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from sales.utils import formatear_moneda_sin_centavos, getAllCampaniaOfYear, getTodasCampaniasDesdeInicio, dataStructureCannons, dataStructureClientes, dataStructureVentas, dataStructureMovimientosExternos,deleteFieldsInDataStructures
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import datetime
import json
from elanelsystem.utils import printPDF
from .utils import (
    liquidaciones_countFaltas,
    liquidaciones_countTardanzas,
    obtener_ultima_campania,
    get_comision_total,
    get_detalle_comision_x_cantidad_ventasPropias
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
        # try:
            context = {}
            request.session["ajustes_comisiones"] = [] # Reiniciar posibles ajustes de la comisiones que existan
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

            LiquidacionVendedor.objects.filter(campania=campania, sucursal=sucursalObject).delete()
            LiquidacionSupervisor.objects.filter(campania=campania, sucursal=sucursalObject).delete()
            LiquidacionGerenteSucursal.objects.filter(campania=campania, sucursal=sucursalObject).delete()
            LiquidacionCompleta.objects.filter(campania=campania, sucursal=sucursalObject).delete()

            #region Liquidacion por tipo de colaborador 
            vendedores = []
            supervisores = []
            gerentes = []
            for item in datos:
                user_id = item["id"]
                detalle_sin_ajuste = item["info_total_de_comision"]["detalle"]
                detalle_con_ajustes, total_ajuste = insertar_ajustes_en_detalle(detalle_sin_ajuste, ajustes_sesion, user_id)

                total_comision_ajustada = item["comisionTotal"] + total_ajuste

                if item["tipo_colaborador"] == "Vendedor":
                    new = LiquidacionVendedor(
                        usuario=Usuario.objects.get(pk=user_id),
                        campania=campania,
                        sucursal=sucursalObject,
                        cant_ventas=item["info_total_de_comision"]["cant_ventas_propia"],
                        productividad=item["info_total_de_comision"]["productividad_propia"],
                        total_comisionado=total_comision_ajustada,
                        detalle=detalle_con_ajustes
                    )
                    new.save()
                    vendedores.append(new)

                elif item["tipo_colaborador"] == "Supervisor":
                    new = LiquidacionSupervisor(
                        usuario=Usuario.objects.get(pk=user_id),
                        campania=campania,
                        sucursal=sucursalObject,
                        cant_ventas=item["info_total_de_comision"]["cant_ventas_fromRol"],
                        productividad=item["info_total_de_comision"]["productividad_fromRol"],
                        total_comisionado=total_comision_ajustada,
                        detalle=detalle_con_ajustes
                    )
                    new.save()
                    supervisores.append(new)

                elif item["tipo_colaborador"] == "Gerente sucursal":
                    new = LiquidacionGerenteSucursal(
                        usuario=Usuario.objects.get(pk=user_id),
                        campania=campania,
                        sucursal=sucursalObject,
                        total_comisionado=total_comision_ajustada,
                        detalle=detalle_con_ajustes
                    )
                    new.save()
                    gerentes.append(new)

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
    
    sucursalObject = Sucursal.objects.get(id = int(form["sucursal"]))
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
        "comisionTotal": get_comision_total(item,campania,sucursalObject)["comision_total"],
        "info_total_de_comision": get_comision_total(item,campania,sucursalObject)
        } 
        for item in colaboradores if item.rango != "Admin"]
    
    totalDeComisiones = sum([user["comisionTotal"] for user in colaboradores_list])
    request.session["liquidacion_data"] = colaboradores_list

    return JsonResponse({"colaboradores_data": colaboradores_list, "totalDeComisiones": totalDeComisiones} , safe=False)


def crearAjusteComision(request):
    """
    Crear un ajuste de comisión para un colaborador y almacenarlo en la sesión.
    Estructura de cada ajuste (ejemplo):
    {
      "user_id": <int>,
      "ajuste_tipo": "positivo" o "negativo",
      "dinero": <float>,
      "observaciones": <str>,
      "campania": <str>,
      "agencia": <str>
    }
    """

    if request.method == "POST":
        try:
            # Intentamos parsear el cuerpo como JSON.
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": False, "message": "JSON mal formado"}, status=400)
        
        # Ejemplo de datos que recibes:
        user_id = body.get("user_id")
        ajuste_tipo = body.get("ajuste")
        dinero = body.get("dinero")
        observaciones = body.get("observaciones", "")
        campania = body.get("campania")
        agencia = body.get("agencia")

        print("[DEBUG] crearAjusteComision => Datos recibidos:")
        print("   user_id:", user_id)
        print("   ajuste_tipo:", ajuste_tipo)
        print("   dinero:", dinero)
        print("   observaciones:", observaciones)
        print("   campania:", campania)
        print("   agencia:", agencia)

        # Validamos algo básico
        if not user_id or not campania or not agencia:
            return JsonResponse({"status": False, "message": "Faltan datos obligatorios"}, status=400)

        # Creamos el dict del ajuste
        ajuste = {
            "user_id": user_id,
            "ajuste_tipo": ajuste_tipo,
            "dinero": float(dinero) if dinero else 0.0,
            "observaciones": observaciones,
            "campania": campania,
            "agencia": agencia
        }

        # Recuperamos la lista de ajustes en sesión (o creamos si no existe)
        ajustes_sesion = request.session.get("ajustes_comisiones", [])
        
        # Agregamos este nuevo ajuste a la lista
        ajustes_sesion.append(ajuste)

        # Guardamos de nuevo en la sesión
        request.session["ajustes_comisiones"] = ajustes_sesion

        # Marcamos la sesión como modificada para asegurar que se guarde
        request.session.modified = True

        print("[DEBUG] crearAjusteComision => Ajuste guardado en sesión. Ajustes totales ahora:")
        print(request.session["ajustes_comisiones"])

        sucursalObject = Sucursal.objects.get(pseudonimo=agencia)
        usuario = Usuario.objects.get(pk=user_id)
        datos_comision = get_comision_total(usuario, campania, sucursalObject)

        nueva_comision_total = datos_comision["comision_total"]

        return JsonResponse({
            "status": True,
            "message": "Ajuste de comisión creado en sesión.",
            "user_id": user_id,
            "new_comision": nueva_comision_total
        })
    
    else:
        return JsonResponse({"status": False, "message": "Método no permitido"}, status=405)


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
            # productividadPropia = calcular_productividad_vendedor(usuario,campania,sucursalObject)
            cuotas1Adelantadas = getCuotas1(usuario,campania,sucursalObject)

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
                vendedoresACargo = usuario.vendedores_a_cargo
                
                # Filtrar y ordenar vendedores a cargo
                # Extraer correos electrónicos de los vendedores a cargo
                vendedoresACargo_emails = [vendedor['email'] for vendedor in usuario.vendedores_a_cargo]

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
  