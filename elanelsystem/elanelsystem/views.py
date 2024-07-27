import datetime
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.views import generic
from django.urls import reverse, reverse_lazy
from users.forms import CustomLoginForm
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from sales.utils import dataStructureCannons, dataStructureVentas, dataStructureMovimientosExternos,deleteFieldsInDataStructures
from users.models import Sucursal, Usuario
from sales.utils import exportar_excel, obtener_ultima_campania

class IndexLoginView(generic.FormView):
    form_class = CustomLoginForm
    template_name = "index.html"

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redireccionar_por_permisos(request.user)
        return super(IndexLoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Si el formulario es válido, inicia sesión en el usuario
        """
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            return redireccionar_por_permisos(user)
        return super(IndexLoginView, self).form_invalid(form)


def redireccionar_por_permisos(usuario):
    
    secciones = {
        # "Resumen": {"permisos": ["sales.my_ver_resumen"], "url": reverse("sales:resumen")},
        "Clientes": {"permisos": ["users.my_ver_clientes"], "url": reverse("users:list_customers")},
        "Caja": {"permisos": ["sales.my_ver_caja"], "url": reverse("sales:caja")},
        "Reportes": {"permisos": ["sales.my_ver_reportes"], "url": reverse("reporteView")},
        "Post Venta": {"permisos": ["sales.my_ver_postventa"], "url": reverse("sales:postVentaList",args=[obtener_ultima_campania()])},
        "Colaboradores": {"permisos": ["users.my_ver_colaboradores"], "url": reverse("users:list_users")},
        "Liquidaciones": {"permisos": ["liquidacion.my_ver_liquidaciones"], "url": reverse("liquidacion:liquidacionesPanel")},
        "Administracion": {"permisos": ["users.my_ver_administracion"], "url": reverse("users:panelAdmin")},
        "Planes suspendidos": {"permisos": ["sales.my_ver_planes_suspendidos"], "url": reverse("sales:ventasSuspendidas")},
    }

    secciones_permitidas = {}
    for k, v in secciones.items():
        if any(usuario.has_perm(perm) for perm in v['permisos']):
            secciones_permitidas[k] = v

    for k, v in secciones_permitidas.items():
        return redirect(v["url"])


def logout_view(request):
    logout(request)
    return redirect('indexLogin')


class ReportesView(generic.View):
    template_name = 'reportes.html'

    def get(self, request,*args, **kwargs):
        TIPOS_DE_REPORTES = ["Cannons", "Ventas", "Movimientos", "Clientes"]
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


def filterMainManage(request,dataStructure):
    # Obtenemos los parámetros del POST y la estructura de datos de la sesión
    print(request)
    params_dict = request
    # Limpiamos los parámetros para eliminar campos vacíos y otros no relevantes
    # Claves a excluir del filtrado
    keys_to_exclude = {"page","typeReporte", "csrfmiddlewaretoken"}
    params_dict_clear = {
        key: value
        for key, value in params_dict.items()
        if value.strip() and key not in keys_to_exclude
    }

    # Mapeo de filtros a funciones
    possible_filters = {
        "fecha": filterDataBy_date,
        "tipo_pago": filterDataBy_typePayments,
        "tipo_mov": filterDataBy_typeMovements,
        # "agencia": filterDataBy_agency,
        "mora": filterDataBy_cannonsMora,
        "vendedor": filterDataBy_seller,
        "suspendida": filterDataBy_suspendedSales,
        "postVenta": filterDataBy_postVenta,
    }

    # Aplicamos los filtros en el orden que se reciban en los parámetros

    filtered_data = dataStructure  # Usamos la estructura inicial

    for filter_name, filter_func in possible_filters.items():
        if filter_name in params_dict_clear:
            filter_value = params_dict_clear[filter_name]
            try:
                filtered_data = filter_func(filtered_data, filter_value)
            except Exception as e:
                # Manejo de errores para filtros
                print(f"Error applying filter {filter_name}: {str(e)}")
                return HttpResponseBadRequest(f"Error applying filter {filter_name}: {str(e)}")

    return filtered_data



#region MANEJO DE FILTROS ------------------------------------------------------------------
"""
    Se utiliza en algunas funciones *args porque asi evitamos posibles errores que se producir
    al pasar mas de 1 parametro a aquellas funciones que solo necesitan pasar la dataStructure.
"""

def filterDataBy_date(data_structure, fecha):
    # Verificamos el formato de la fecha y lo dividimos en fechaInicio y fechaFinal
    try:
        fechas = fecha.split("—")
        fecha_inicio_str = fechas[0].strip() + " 00:00"
        fecha_final_str = fechas[1].strip() + " 00:00" if len(fechas) > 1 else None
        # print(f'- - - - - - -Fecha final: {fecha_final_str}')
        fecha_inicio = datetime.datetime.strptime(fecha_inicio_str, "%d/%m/%Y %H:%M")
        fecha_final = datetime.datetime.strptime(fecha_final_str, "%d/%m/%Y %H:%M") if fecha_final_str else None
    except ValueError:
        raise ValueError("Invalid date format. Use 'dd/mm/yyyy HH:MM'.")

    data_filtered = []
    
    for item in data_structure:
        fecha_str = item.get("fecha", None)
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
    return list(filter(lambda item:item["tipo_pago"] == typePayment,dataStructure))


def filterDataBy_typeMovements(dataStructure, typeMovement):
    return list(filter(lambda item:item["tipo_mov"] == typeMovement, dataStructure))



# def filterDataBy_agency(dataStructure, agency):
#     pass


def filterDataBy_cannonsMora(dataStructure, *args):
    return list(filter(lambda item:item["status"] == "Atrasado",dataStructure))


def filterDataBy_seller(dataStructure, seller):
    return list(filter(lambda item:item["vendedor"] == seller,dataStructure))


def filterDataBy_suspendedSales(dataStructure, *args):
    pass


def filterDataBy_postVenta(dataStructure, grade):
    return list(filter(lambda item:item["auditoria"][-1] == grade,dataStructure))

#endregion --------------------------------------------------------------------------------

