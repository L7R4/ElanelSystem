import datetime
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.views import generic
from django.urls import reverse 
from sales.utils import dataStructureCannons, dataStructureClientes, dataStructureVentas, dataStructureMovimientosExternos,deleteFieldsInDataStructures
from users.models import Sucursal
from sales.utils import exportar_excel
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class IndexLoginView(LoginView):
    template_name = "index.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return redireccionar_por_permisos(self.request.user)
        
    
def redireccionar_por_permisos(usuario):
    
    secciones = {
        # "Resumen": {"permisos": ["sales.my_ver_resumen"], "url": reverse("sales:resumen")},
        "Clientes": {"permisos": ["users.my_ver_clientes"], "url": reverse("users:list_customers")},
        "Caja": {"permisos": ["sales.my_ver_caja"], "url": reverse("sales:caja")},
        # "Reportes": {"permisos": ["sales.my_ver_reportes"], "url": reverse("reporteView")},
        "Colaboradores": {"permisos": ["users.my_ver_colaboradores"], "url": reverse("users:list_users")},
        "Liquidaciones": {"permisos": ["liquidacion.my_ver_liquidaciones"], "url": reverse("liquidacion:liquidacionesPanel")},
        "Administracion": {"permisos": ["users.my_ver_administracion"], "url": reverse("users:panelAdmin")},
        "Planes suspendidos": {"permisos": ["sales.my_ver_planes_suspendidos"], "url": reverse("sales:ventasSuspendidas")},
    }
    # allPermissions = [perm for perm in Permission.objects.all() if perm.codename.startswith('my_')]
    
    secciones_permitidas = {}
    for k, v in secciones.items():
        if any(usuario.has_perm(perm) for perm in v['permisos']):
            secciones_permitidas[k] = v

    for k, v in secciones_permitidas.items():
        return v["url"]


def logout_view(request):
    logout(request)
    return redirect('indexLogin')


class ReportesView(generic.View):
    template_name = 'reportes.html'

    def get(self, request,*args, **kwargs):
        TIPOS_DE_REPORTES = ["cannons", "ventas", "movimientos", "clientes"]
        context = {"tiposDeReportes": TIPOS_DE_REPORTES}
        return render(request,self.template_name,context)
    
    def post(self,request,*args,**kwargs):
        TIPOS_DE_REPORTES = ["Cannons", "Ventas", "Movimientos", "Clientes"]
        context = {"tiposDeReportes": TIPOS_DE_REPORTES}
        querys = request.POST

        typeReporte = request.POST.get("typeReporte")
        sucursal_pseudonimo = request.POST.get("sucursal") if request.POST.get("sucursal") != "" else "Todas"

        if(typeReporte == "Cannons"):
            dataStructure = dataStructureCannons(sucursal_pseudonimo)

            filteredInformation = filterMainManage(querys,dataStructure)
            if isinstance(filteredInformation, HttpResponseBadRequest):
                print(filteredInformation.content.decode())
            else:
                cleanedFilteredInformation = deleteFieldsInDataStructures(filteredInformation,["id_Mov","tipo_Movimiento"])
                return exportar_excel(cleanedFilteredInformation)

        elif(typeReporte == "Ventas"):
            dataStructure = dataStructureVentas(sucursal_pseudonimo)

            filteredInformation = filterMainManage(request,dataStructure)
            if isinstance(filteredInformation, HttpResponseBadRequest):
                print(filteredInformation.content.decode())
            else:
                return exportar_excel(filteredInformation)

        elif(typeReporte == "Movimientos"):
            dataStructure = dataStructureMovimientosExternos(sucursal_pseudonimo)

            filteredInformation = filterMainManage(request,dataStructure)
            if isinstance(filteredInformation, HttpResponseBadRequest):
                print(filteredInformation.content.decode())
            else:
                return exportar_excel(filteredInformation)

        return render(request,self.template_name,context)

# Convierte los valores de cada clave a una lista
def convertirValoresALista(diccValores):
    for key, value in diccValores.items():
        diccValores[key] = [val.strip() for val in value.split("-")]
    return diccValores


def filterMainManage(request,dataStructure):
    # Obtenemos los parámetros del POST y la estructura de datos de la sesión
    params_dict = request
    # Limpiamos los parámetros para eliminar campos vacíos y otros no relevantes
    # Claves a excluir del filtrado
    keys_to_exclude = {"page","typeReporte", "csrfmiddlewaretoken"}
    params_dict_clear = {
        key: value
        for key, value in params_dict.items()
        if value.strip() and key not in keys_to_exclude
    }
    
    params_dict_clear = convertirValoresALista(params_dict_clear) # Convertimos los valores  de cada clave a una lista
    print(f"PArametros a filtrar: {params_dict_clear}")
    # print(params_dict_clear)
    # Mapeo de filtros a funciones
    possible_filters = {
        "fecha": filterDataBy_date,
        "metodoPago": filterDataBy_typePayments,
        "cobrador": filterDataBy_enteRecaudadores,
        "tipo_mov": filterDataBy_typeMovements,
        "campania": filterDataBy_campania,
        "campaniaPago": filterDataBy_campaniaPago,

        # "agencia": filterDataBy_agency,
        "mora": filterDataBy_cannonsMora,
        "vendedor": filterDataBy_seller,
        "suspendida": filterDataBy_suspendedSales,
        "postVenta": filterDataBy_postVenta,
    }

    # Aplicamos los filtros en el orden que se reciban en los parámetros

    filtered_data = dataStructure  # Usamos la estructura inicial
    # print(f"Data Structure: - - - - - \ {filtered_data}")

    for filter_name, filter_func in possible_filters.items():
        if filter_name in params_dict_clear:
            # print("WEpsss")
            # print(filter_name)
            # print(f"Filtro : {filter_name}")
            filter_value = params_dict_clear[filter_name]
            # print(f"valor: {filter_value}")
            try:
                filtered_data = filter_func(filtered_data, filter_value)
            except Exception as e:
                # Manejo de errores para filtros
                print(f"Error applying filter {filter_name}: {str(e)}")
                return HttpResponseBadRequest(f"Error applying filter {filter_name}: {str(e)}")

    return filtered_data


class DetallesNegocioView(generic.View):
    template_name = 'detalle_por_datos.html'

    

    def get(self, request, tipo_slug):
        # Obtén los datos del modelo basado en el slug
        sucursal = request.GET.get("agencia") if request.GET.get("agencia") else "Sucursal central"

        MODELOS = {
            'cannons': dataStructureCannons(sucursal),
            'ventas': dataStructureVentas(sucursal),
            'movimientos': dataStructureMovimientosExternos(sucursal),
            'clientes': dataStructureClientes(sucursal),
        }

        datos = MODELOS.get(tipo_slug)
        print(sucursal)
        # Definir atributos a mostrar según el modelo
        if tipo_slug == "ventas":
            attrs = ["nro_operacion", "fecha", "nro_cliente", "nombre_de_cliente", "agencia", "nro_cuotas","campania","importe", "interes_generado","total_a_pagar","dinero_entregado","dinero_restante","cuota_comercial",'producto', 'paquete', 'vendedor', 'supervisor']

        elif tipo_slug == "movimientos":
            attrs = ["nroComprobante", "fecha", "nroIdentificacion", "tipoComprobante", "metodoPago","monto","tipoMoneda", "agencia", "tipo_mov",  "denominacion", "estado", "dias_de_mora", "ente", "campania","concepto"]
            
        elif tipo_slug == "clientes":
            attrs = ["nro_cliente", "nombre", "dnio", "domic", "loc","prov","cod_postal", "tel", "fec_nacimiento",  "agencia", "estado_civil", "ocupacion"]

        elif tipo_slug == "cannons":
            attrs = ["cuota", "fecha", "nro_operacion", "monto", "metodoPago","nro_del_cliente","nombre_del_cliente", "agencia", "tipo_mov",  "fecha_de_vencimiento", "estado", "dias_de_mora", "interes_por_mora", "total_final","cobrador"]

        else:
            attrs = []  # Por defecto no mostrar atributos si no se definen

        # Filtrar los datos según los atributos definidos
        datos_filtrados = [
            {attr: obj[attr] for attr in attrs if attr in obj}
            for obj in datos
        ]

        request.session['datos'] = {'data': datos_filtrados, 'tipo': tipo_slug}


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
                'sucursalDefault': Sucursal.objects.get(pseudonimo="Sucursal central"),
            }
        )
    


class ExportarExcelView(generic.View):
    def get(self, request, *args, **kwargs):
        # Obtener los datos filtrados de la sesión
        datos = request.session.get('datos', [])
        print(datos)
        if not datos:
            return HttpResponse("No hay datos para exportar.", status=400)

        # Llamar a la función `exportar_excel` con los datos filtrados
        return exportar_excel(datos)


#region MANEJO DE FILTROS ------------------------------------------------------------------
"""
    Se utiliza en algunas funciones *args porque asi evitamos posibles errores que se producir
    al pasar mas de 1 parametro a aquellas funciones que solo necesitan pasar la dataStructure.
"""

def filterDataBy_date(data_structure, fecha):
    # Verificamos el formato de la fecha y lo dividimos en fechaInicio y fechaFinal
    try:
        fechas = fecha[0].split("—")
        # print(f"La fecha es {fechas}")
        fecha_inicio_str = fechas[0].strip() + " 00:00"
        fecha_final_str = fechas[1].strip() + " 00:00" if len(fechas) > 1 else None
        # print(f'- - - - - - -Fecha final: {fecha_final_str}')
        fecha_inicio = datetime.datetime.strptime(fecha_inicio_str, "%d/%m/%Y %H:%M")
        fecha_final = datetime.datetime.strptime(fecha_final_str, "%d/%m/%Y %H:%M") if fecha_final_str else None
    except ValueError:
        raise ValueError("Invalid date format. Use 'dd/mm/yyyy HH:MM'.")

    data_filtered = []
    
    for item in data_structure:
        fecha_str = item.get("fecha", None).get("data",None)
        if not fecha_str:
            continue

        fecha_obj = datetime.datetime.strptime(fecha_str, "%d/%m/%Y %H:%M")

        if fecha_final:
            if fecha_inicio <= fecha_obj <= fecha_final:
                data_filtered.append(item)
        else:
            if fecha_obj.date() >= fecha_inicio.date():
                data_filtered.append(item)
                
    return data_filtered


def filterDataBy_typePayments(dataStructure, typePayment):
    return list(filter(lambda item:item["metodoPago"]["data"] in typePayment,dataStructure))


def filterDataBy_typeMovements(dataStructure, typeMovement):
    return list(filter(lambda item:item["tipo_mov"]["data"] in typeMovement, dataStructure))

def filterDataBy_campaniaPago(dataStructure, campania):
    return list(filter(lambda item:item["campaniaPago"]["data"] in campania, dataStructure))

def filterDataBy_campania(dataStructure, campania):
    return list(filter(lambda item:item["campania"]["data"] in campania, dataStructure))


def filterDataBy_enteRecaudadores(dataStructure, typeEnteRecaudador):
    return list(filter(
        lambda item: (item.get("cobrador", {}).get("data") in typeEnteRecaudador) or 
                     (item.get("ente", {}).get("data") in typeEnteRecaudador),
        dataStructure
    ))


def filterDataBy_cannonsMora(dataStructure, *args):
    return list(filter(lambda item:item["estado"] == "Atrasado",dataStructure))


def filterDataBy_seller(dataStructure, seller):
    return list(filter(lambda item:item["vendedor"] == seller,dataStructure))


def filterDataBy_suspendedSales(dataStructure, *args):
    pass


def filterDataBy_postVenta(dataStructure, grade):
    return list(filter(lambda item:item["auditoria"][-1] == grade,dataStructure))

#endregion --------------------------------------------------------------------------------

