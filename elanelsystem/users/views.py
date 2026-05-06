
import datetime
import os
import re
from django.conf import settings
from django.contrib.auth.models import Group,Permission
from django.forms import ValidationError
from django.db.models.functions import Cast, Substr
from django.db.models import IntegerField
from django.db.utils import IntegrityError
from django.shortcuts import redirect, render
from django.views import generic
from users.utils import preprocesar_excel_clientes, printPDFNewUSer
from sales.utils import getAllCampaniaOfYear, getCampanasDisponibles, getCampaniaActual
from django.db import transaction
from .models import Usuario,Cliente,Sucursal,Key
from products.models import Products
from sales.models import CuentaCobranza
from sales.models import Ventas,ArqueoCaja,MovimientoExterno,MetodoPago
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.views.decorators.cache import never_cache
from sales.utils import getEstadoVenta
# from .forms import CreateClienteForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import Permission
from sales.mixins import TestLogin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.validators import validate_email
import json
from django.http import HttpResponse, JsonResponse
from datetime import date,timedelta

from dateutil.relativedelta import relativedelta
from elanelsystem.utils import format_date, formatear_columnas, formatear_dd_mm_yyyy_h_m, handle_nan

from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator

import pandas as pd
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.hashers import check_password
#region Usuarios - - - - - - - - - - - - - - - - - - - -
@never_cache
@login_required
@require_GET
def me(request):
    u = request.user
    # Permisos como "app_label.codename" (p.ej. "sales.my_ver_graficos")
    perms = sorted(list(u.get_all_permissions()))
    groups = list(u.groups.values_list('name', flat=True))

    # Si querés enviar sucursales (tu modelo Usuario las tiene):
    try:
        sucursales = list(u.sucursales.values("id", "pseudonimo"))
    except Exception:
        sucursales = []

    data = {
        "id": u.pk,
        "username": getattr(u, "username", ""),
        "name": getattr(u, "nombre", ""),
        "is_staff": u.is_staff,
        "is_superuser": u.is_superuser,
        "groups": groups,
        "perms": perms,
        "sucursales": sucursales,
    }
    # Evitar caching por proxies
    resp = JsonResponse(data)
    resp["Cache-Control"] = "no-store"
    return resp

class ConfiguracionPerfil(TestLogin,generic.View):
    model = Usuario
    template_name = "configurarPerfil.html"

    def get(self,request,*args,**kwargs):
        context = {}
        context["additional_passwords"] = request.user.additional_passwords
        return render(request, self.template_name, context)
    
    def post(self,request,*args, **kwargs):
        try:
            data = json.loads(request.body)
            message = ""
            for key, value in data.items():
                if key == "inputContrasenia":
                    request.user.set_password(value)
                    request.user.c = value
                    message = 'Contraseña de tu usuario actualizada'
                else:
                    request.user.additional_passwords[key]["password"] = value
                    message = f'{request.user.additional_passwords[key]["descripcion"]} actualizada'
            
            request.user.save()
            return JsonResponse({'success': True,"message" : message}, safe=False)
        
        except Exception as e:
            message = f' Hubo un error inesperado al actualizar la contraseña'
            return JsonResponse({'success': False,"message" : message}, safe=False)
            

class CrearUsuario(TestLogin, generic.View):
    model = Usuario
    template_name = "create_user.html"
    roles = Group.objects.all()
    
    sucursales = Sucursal.objects.all()

    def get(self,request,*args, **kwargs):
        context = {}
        sucursales = Sucursal.objects.all()
        context["sucursales"] = sucursales
        context["roles"] = self.roles

        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        form = json.loads(request.body)
        errors = {}
        
        rango = form['rango']
        sucursales_text = form['sucursal']
        sucursales_split = [nombre.strip() for nombre in sucursales_text.split('-')]
        
        email=form['email']
        dni=form['dni']

        usuario = Usuario()

        # Validar el rango
        if rango and not Group.objects.filter(name=rango).exists():
            errors['rango'] = 'Rango invalido.'
        elif rango:
            rango = Group.objects.get(name=rango)


        # Validar la sucursal
        for sucursal in sucursales_split:
            if sucursal and not Sucursal.objects.filter(pseudonimo=sucursal).exists():
                errors['sucursal'] = f'Sucursal {sucursal} invalida.'
                

        # Validar la existencia del DNI
        if dni and Usuario.objects.filter(dni=dni).exists():
            errors['dni'] = 'DNI ya registrado.'
            return JsonResponse({'success': False, 'errors': errors}, safe=False)  


        # Validar la existencia del email
        if email and Usuario.objects.filter(email=email).exists():
            errors['email'] = 'El email ya registrado.'
            return JsonResponse({'success': False, 'errors': errors}, safe=False)  

        elif email:
            try:
                validate_email(email)
            except ValidationError: 
                errors['email'] = 'Email no válido.' 

        
        usuario = self.model.objects.create_user(
            email=form['email'],
            nombre=form['nombre'],
            dni=form['dni'],
            rango=rango,
            password=form['password']
        )

        # Asignar campos adicionales
        usuario.tel = form['tel']
        usuario.domic = form['domic']
        usuario.prov = form['prov']
        usuario.loc = form['loc']
        usuario.cp = form['cp']
        usuario.lugar_nacimiento = form['lugar_nacimiento']
        usuario.fec_nacimiento = form['fec_nacimiento']
        usuario.fec_ingreso = form['fec_ingreso']
        usuario.estado_civil = form['estado_civil']
        usuario.xp_laboral = form['xp_laboral']
        usuario.c = form['password']

        # Para guardar los familiares en caso que haya
        familiares = []
        flag = True
        for key, value in form.items():
            if key.startswith('familia_nombre_') and value:
                numero = key.split("_")[-1]

                # Valido el texto de realacion con el familiar
                relacion = form[f'familia_relacion_{numero}']
                if not re.match(r'^[a-zA-Z\s]*$', relacion):
                    errors[f'familia_relacion_{numero}'] = 'Solo puede contener letras.'
                    flag = False
                
                tel = form[f'familia_tel_{numero}']

                if not re.match(r'^\d+$', tel):
                    errors[f'familia_tel_{numero}'] = 'Solo puede contener numeros.'
                    flag = False

                # Valido el texto de realacion con el familiar
                nombre = value
                if not re.match(r'^[a-zA-Z\s]*$', nombre):
                    errors[f'familia_nombre_{numero}'] = 'Solo puede contener letras.' 
                    flag = False  
                
                familiares.append({
                    'relacion': relacion,
                    'nombre': value,
                    'tel': tel
                })

        if(flag):
            usuario.datos_familiares = familiares
      # ------------------------------------------------------------------------------    

        # Para guardar los vendedores a cargo en caso que haya
        vendedores = []
        for key, value in form.items():
            if key.startswith('idv_') and value:
                
                vendedores.append({
                    'nombre': Usuario.objects.get(email=value).nombre,
                    'email': value,
                })
        usuario.vendedores_a_cargo = vendedores
        # ------------------------------------------------------------------------------       



        try:
            usuario.full_clean(exclude=['password'])
        except ValidationError as e:
            errors.update(e.message_dict)
       
        if len(errors) != 0:
            
            usuario.delete() # Eliminar el usuario creado por la funcion _create_user del modelo UserManager
            return JsonResponse({'success': False, 'errors': errors}, safe=False)  
        else:
            # Asignamos aca porque entonces nos aseguramos que no tengamos errores en los campos y podamos hacer la referencia sin problemas
            for sucursal in sucursales_split:
                sucursal_object = Sucursal.objects.get(pseudonimo=sucursal)
                usuario.sucursales.add(sucursal_object)

            usuario.groups.add(rango)
            usuario.setAdditionalPasswords() # Seteamos las contraseñas adicionales segun los permisos
            usuario.save()

            response_data = {"urlPDF":reverse_lazy('users:newUserPDF',args=[usuario.pk]),"urlRedirect": reverse_lazy('users:list_users'),"success": True}
            return JsonResponse(response_data, safe=False)         
  

def dias_trabajados_en_campania(user, campania_str):
    from elanelsystem.utils import parse_fecha_to_date, obtener_fechas_campania
    """
    Calcula días trabajados dentro de la campaña,
    basándose únicamente en los diferentes fec_ingreso del history.
    Devuelve (snapshot_primero, total_dias).
    """

    inicio_camp, fin_camp = obtener_fechas_campania(campania_str)

    ingresos = []
    for h in user.history.all():
        fecha_ing = parse_fecha_to_date(h.fec_ingreso)
        if fecha_ing and fecha_ing <= fin_camp:
            ingresos.append(h)

    if not ingresos:
        return None, 0
    elif len(ingresos) == 1 and ingresos[0].history_type == "+": # Si solo hay un ingreso y es de tipo +, quiere decir que desde que se registró no salio
        pass
        # print(f"\nUsuario: {user.nombre}, solo tiene un ingreso y no tiene egreso, por lo tanto se considera que estuvo activo todo el tiempo de la campaña")        
    elif len(ingresos) > 1:
        # print(f"\nUsuario: {user.nombre}, solo tiene mas de un ingreso")        
        ingresos = [h for h in ingresos if h.history_type != "+"]

    # 3) Ordenar ascendente por fecha de ingreso
    ingresos.sort(key=lambda h: parse_fecha_to_date(h.fec_ingreso))
    # print(f"\nFechas de ingreso ordenado para {user.nombre}: {[h.fec_egreso for h in ingresos]}\n")

    ultima_version = ingresos[-1]
    # print(f"\nUltima version de {user.nombre} es: {ultima_version.fec_ingreso} - {ultima_version.fec_egreso} - {ultima_version.history_type}\n")
    fecha_ingreso = parse_fecha_to_date(ultima_version.fec_ingreso)
    fecha_egreso = parse_fecha_to_date(ultima_version.fec_egreso) if ultima_version.fec_egreso else datetime.datetime.today().date()


    fecha_inicio_real = max(fecha_ingreso, inicio_camp)
    fecha_fin_real = min(fecha_egreso, fin_camp)
    dias_trabajados_campania = 0
    if fecha_inicio_real > fecha_fin_real:
        dias_trabajados_campania = 0
    else:
        dias_trabajados_campania = (fecha_fin_real - fecha_inicio_real).days + 1

    return ultima_version, dias_trabajados_campania

class ListaUsers(PermissionRequiredMixin, generic.ListView):
    model = Usuario
    template_name = "list_users.html"
    permission_required = "sales.my_ver_resumen"

    def wants_json(self, request):
        return (
            "application/json" in request.headers.get("Accept", "")
            or request.headers.get("X-Requested-With") == "XMLHttpRequest"
        )

    def get(self, request, *args, **kwargs):
        page_number = int(request.GET.get('page', 1))
        page_size   = int(request.GET.get('page_size', 30))
        search      = request.GET.get('search', '')          
        sucursal_id = request.GET.get('sucursal_id')

        userConnected = request.user
        sucursal_ids = userConnected.sucursales.values_list('id', flat=True)
        users_queryset = Usuario.objects.filter(sucursales__in=sucursal_ids).order_by('nombre')

        if sucursal_id:
            users_queryset = users_queryset.filter(sucursales__id=sucursal_id)

        if search:
            users_queryset = users_queryset.filter(
                Q(nombre__icontains=search) |
                Q(dni__icontains=search) |
                Q(email__icontains=search) |
                Q(tel__icontains=search) |
                Q(rango__icontains=search)
            ).distinct()

        paginator = Paginator(users_queryset, page_size)
        page_obj = paginator.get_page(page_number)

        if self.wants_json(request):
            users_data = []
            for user in page_obj.object_list:
                sucursales_pseudonimos = [s.pseudonimo for s in user.sucursales.all()]
                users_data.append({
                    "id": user.id,
                    "nombre": user.nombre,
                    "dni": user.dni,
                    "email": user.email,
                    "tel": user.tel,
                    "rango": user.rango,
                    "sucursales": sucursales_pseudonimos
                })
            return JsonResponse({
                "results": users_data,
                "total": paginator.count,
            })

        # Render normal HTML
        campaniasDisponibles = getCampanasDisponibles()
        metodosPago = [{"id": metodo.id, "alias": metodo.alias } for metodo in MetodoPago.objects.all()]
        sucursales = [{"id": sucursal.id, "pseudonimo": sucursal.pseudonimo } for sucursal in Sucursal.objects.all() ]
        sucursalesDisponibles = [{"id": sucursal.id, "pseudonimo": sucursal.pseudonimo } for sucursal in request.user.sucursales.all()]
        ente_recaudadores = [{"id":cuenta.id,"alias":cuenta.alias} for cuenta in CuentaCobranza.objects.all()]

        users_data = []
        for user in page_obj.object_list:
            # Obtén los pseudónimos de las sucursales asociadas a cada usuario
            sucursales_pseudonimos = [sucursal.pseudonimo for sucursal in user.sucursales.all()]
            # Agrega el diccionario con la información del usuario y sus sucursales
            users_data.append({
                "id": user.id,
                "nombre": user.nombre,
                "dni": user.dni,
                "email": user.email,
                "tel": user.tel,
                "rango": user.rango,
                "sucursales": sucursales_pseudonimos
            })
            
        context = {
            "users": users_data,
            "urlPostDescuento": reverse_lazy("users:realizarDescuento"),
            "campaniasDisponibles": json.dumps(campaniasDisponibles),
            "sucursalesDisponibles": json.dumps(sucursalesDisponibles),
            "sucursales": sucursales,
            "metodosDePago": json.dumps(metodosPago),
            "ente_recaudadores": json.dumps(ente_recaudadores),
            "page_obj": page_obj,
        }
        return render(request, self.template_name,context)

    def post(self, request, *args, **kwargs):
        # Cargar los filtros desde el body de la solicitud
        form = json.loads(request.body)
        
        # Crear un diccionario para almacenar los filtros dinámicos
        filters = {}
        
        # Filtrar por sucursal si se envía en el request
        if "sucursal" in form and form["sucursal"]:
            filters["sucursales__pseudonimo__icontains"] = form["sucursal"]

        # Aplicar el filtro general de búsqueda
        if "search" in form and form["search"]:
            search_value = form["search"]
            # Usar Q objects para búsqueda en múltiples campos
            search_filter = (
                Q(nombre__icontains=search_value) |
                Q(dni__icontains=search_value) |
                Q(email__icontains=search_value) |
                Q(tel__icontains=search_value) |
                Q(rango__icontains=search_value)
            )

            usuarios = Usuario.objects.filter(**filters).filter(search_filter).distinct()
        else:
            # Si no hay búsqueda, solo aplicar los filtros
            usuarios = Usuario.objects.filter(**filters).distinct()

        page_number = form.get('page', 1)
        per_page = form.get('per_page', 20)
        paginator = Paginator(usuarios, per_page)
        page_obj = paginator.get_page(page_number)

        # Preparar los datos a enviar en la respuesta
        user_data = [
            {
                "id": user.id,
                "nombre": user.nombre,
                "dni": user.dni,
                "email": user.email,
                "tel": user.tel,
                "sucursales": [sucursal.pseudonimo for sucursal in user.sucursales.all()],
                "rango": user.rango,
                "url": reverse('users:detailUser', args=[user.id])
            } for user in usuarios
        ]
        # Retornar los datos filtrados como JSON
        return JsonResponse({
            "users": user_data, 
            "status": True,
            "num_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),                     
        })


class DetailUser(TestLogin, generic.DetailView):
    model = Usuario
    template_name = "detail_user.html"
    roles = Group.objects.all()

    def get(self,request,*args,**kwargs):
        self.object = self.get_object()
        context ={}
        sucursales = Sucursal.objects.all()
        context["sucursales"] = sucursales
        context["roles"] = self.roles

        sucursales_actives = [sucursal.pseudonimo for sucursal in self.object.sucursales.all()]
        context["sucursales_actives"] = ' - '.join(sucursales_actives)
        
        context["familiares"] = self.object.datos_familiares
        context["object"] = self.get_object()
    
        if self.object.rango == "Supervisor":
            vendedores_a_cargo = self.object.vendedores_a_cargo
            vendedores_sucursal = Usuario.objects.filter(sucursales__in=self.object.sucursales.all(), rango="Vendedor")

            # Excluir vendedores que están a cargo
            vendedores_disponibles = vendedores_sucursal.exclude(email__in=[vendedor['email'] for vendedor in vendedores_a_cargo])
            
            context["vendedor_a_cargo"] = vendedores_a_cargo
            context["vendedores"] = vendedores_disponibles

        return render(request, self.template_name, context)
    

    def post(self, request, *args, **kwargs):
        form = json.loads(request.body)
        errors = {}
        
        rango = form['rango']
        sucursales_text = form['sucursal']
        sucursales_split = [nombre.strip() for nombre in sucursales_text.split(' - ')]
        
        email=form['email']
        dni=form['dni']

       # Obtener el usuario existente
        usuario = self.get_object()

        # Validar el rango
        if rango and not Group.objects.filter(name=rango).exists():
            errors['rango'] = 'Rango invalido.'
        elif rango:
            rango = Group.objects.get(name=rango)

        # Validar la sucursal
        for sucursal in sucursales_split:
            if sucursal and not Sucursal.objects.filter(pseudonimo=sucursal).exists():
                errors['sucursal'] = f"Sucursal '{sucursal}' invalida."

        # Validar la existencia del DNI
        if dni and Usuario.objects.filter(dni=dni).exclude(pk=usuario.pk).exists():
            errors['dni'] = 'DNI ya registrado.'

        # Validar la existencia del email
        if email and Usuario.objects.filter(email=email).exclude(pk=usuario.pk).exists():
            errors['email'] = 'El email ya registrado.'
        elif email:
            try:
                validate_email(email)
            except ValidationError: 
                errors['email'] = 'Email no válido.' 

        
        # Asignar campos adicionales
        usuario.email = email
        usuario.nombre=form['nombre']
        usuario.dni=dni
        usuario.rango=rango
        usuario.password=form['password']

        usuario.tel = form['tel']
        usuario.domic = form['domic']
        usuario.prov = form['prov']
        usuario.loc = form['loc']
        usuario.cp = form['cp']
        usuario.lugar_nacimiento = form['lugar_nacimiento']
        usuario.fec_nacimiento = form['fec_nacimiento']
        usuario.fec_ingreso = form['fec_ingreso']
        usuario.estado_civil = form['estado_civil']
        usuario.xp_laboral = form['xp_laboral']
        usuario.c = form['password']

    #region Para guardar los familiares en caso que haya
        familiares = []
        flag = True
        for key, value in form.items():
            if key.startswith('familia_nombre_') and value:
                numero = key.split("_")[-1]
                print(f"Entro")
                # Valido el texto de realacion con el familiar
                relacion = form[f'familia_relacion_{numero}']
                if not re.match(r'^[a-zA-Z\s]*$', relacion):
                    errors[f'familia_relacion_{numero}'] = 'Solo puede contener letras.'
                    flag = False
                
                tel = form[f'familia_tel_{numero}']
                print(f"Tel: {tel}")
                if not re.match(r'^\d+$', tel):
                    errors[f'familia_tel_{numero}'] = 'Solo puede contener numeros.'
                    flag = False

                # Valido el texto de realacion con el familiar
                nombre = value
                if not re.match(r'^[a-zA-Z\s]*$', nombre):
                    errors[f'familia_nombre_{numero}'] = 'Solo puede contener letras.' 
                    flag = False  
                
                familiares.append({
                    'relacion': relacion,
                    'nombre': value,
                    'tel': tel
                })

        if(flag):
            usuario.datos_familiares = familiares
    #endregion ------------------------------------------------------------------------------    

    #region Para guardar los vendedores a cargo en caso que haya
        vendedores = []
        for key, value in form.items():
            if key.startswith('idv_') and value:
                
                vendedores.append({
                    'nombre': Usuario.objects.get(email=value).nombre,
                    'email': value,
                })
        usuario.vendedores_a_cargo = vendedores
    #endregion       



        try:
            usuario.full_clean(exclude=['password'])
        except ValidationError as e:
            errors.update(e.message_dict)
        print(f"Errores: {errors}")
        if len(errors) != 0:
            return JsonResponse({'success': False, 'errors': errors}, safe=False)  
        else:
            # Asignamos aca porque entonces nos aseguramos que no tengamos errores en los campos y podamos hacer la referencia sin problemas
            usuario.sucursales.clear() # Limpiar las sucursales anteriores
            for sucursal in sucursales_split:
                sucursal_object = Sucursal.objects.get(pseudonimo=sucursal)
                usuario.sucursales.add(sucursal_object)

            usuario.groups.add(rango)
            usuario.set_password(form['password'])
            usuario.setAdditionalPasswords() # Seteamos las contraseñas adicionales segun los permisos

            usuario.save()

            response_data = {"urlPDF":reverse_lazy('users:newUserPDF',args=[usuario.pk]),"urlRedirect": reverse_lazy('users:list_users'),"success": True}
            return JsonResponse(response_data, safe=False)         


def viewsPDFNewUser(request,pk):
    import locale
    newUserObject = Usuario.objects.get(pk=pk)
    # Establecer la configuración regional a español
    locale.setlocale(locale.LC_TIME, '')

    fecha = datetime.datetime.strptime(newUserObject.fec_ingreso, '%d/%m/%Y')
    nombre_mes = fecha.strftime('%B')
    

    context ={
                "day": fecha.strftime("%d"),
                "month": fecha.strftime("%m"),
                "name_month": nombre_mes,
                "year": fecha.year,
                "date_today": newUserObject.fec_ingreso,
                "nombreCompleto":newUserObject.nombre,
                "nroCliente": newUserObject.pk,
                "domicilio": newUserObject.domic,
                "localidad": newUserObject.loc,
                "provincia": newUserObject.prov,
                "cp": newUserObject.cp,
                "telefono" : newUserObject.tel,
                "lugar_nacimiento" : newUserObject.lugar_nacimiento,
                "fec_nacimiento" : newUserObject.fec_nacimiento,
                "dni": newUserObject.dni,
                "estado_civil" : newUserObject.estado_civil,
                "xp_laboral" : newUserObject.xp_laboral,
                "datos_familiares" : newUserObject.datos_familiares,
                "agenciaNombre": newUserObject.sucursales.all(),
                # "provincia_localidad_sucursal": newUserObject.sucursal.localidad + "," + newUserObject.sucursal.provincia,
                # "agenciaDireccion": newUserObject.sucursal.direccion,
            }
            
    userName = str(newUserObject.nombre)
    urlPDF= os.path.join(settings.PDF_STORAGE_DIR, "newUser.pdf")
    
    printPDFNewUSer(context,request.build_absolute_uri(),urlPDF)

    with open(urlPDF, 'rb') as pdf_file:
        response = HttpResponse(pdf_file,content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename='+userName+"_ficha"+'.pdf'
        return response
   
    
def requestUsuarios(request):
    request = json.loads(request.body)
    sucursal_filter = [nombre.strip() for nombre in request["sucursal"].split('-')][0]
    sucursal = Sucursal.objects.get(pseudonimo = sucursal_filter) if request["sucursal"] else ""
    user = Usuario.objects.get(pk=request["pkUser"]) if request["pkUser"] else None
    
    usuarios_filtrados_listDict = []

    if request["sucursal"] !="":
        if user != None and user.rango =="Vendedor":
            usuarios_filtrados = Usuario.objects.filter(sucursales = sucursal, rango="Vendedor").exclude(pk=user.pk)
        else:
            usuarios_filtrados = Usuario.objects.filter(sucursales = sucursal, rango="Vendedor")

        usuarios_filtrados_listDict = list({"nombre": item.nombre, "email":item.email} for item in usuarios_filtrados)

    return JsonResponse({"data":usuarios_filtrados_listDict})


def requestUsuarios2(request):
    query_params = request.GET
    usuarios = Usuario.objects.all()
    print(query_params)
    # Mapeo de parámetros a condiciones Q
    filter_map = {
        'nombre': 'nombre__icontains',
        'email': 'email__icontains',
        'rango': 'rango__icontains',
        'dni': 'dni__icontains',
        'tel': 'tel__icontains',
        'prov': 'prov__icontains',
        'loc': 'loc__icontains',
        'sucursal': 'sucursales__id',
    }

    # Construcción dinámica de filtros
    filters = Q()
    for param, query in filter_map.items():
        if param in query_params:
            filters &= Q(**{query: query_params[param]})

    # Aplicar los filtros al modelo Usuario
    usuarios = Usuario.objects.filter(filters).distinct()
    print("Usuarios filtrados")
    print(usuarios)
    # Serializar la respuesta
    data = [
        {
            'id': usuario.id,
            'nombre': usuario.nombre,
            'email': usuario.email,
            'rango': usuario.rango,
            'dni': usuario.dni,
            'tel': usuario.tel,
            'prov': usuario.prov,
            'loc': usuario.loc,
        }
        for usuario in usuarios
    ]

    return JsonResponse(data, safe=False)


def realizarDescuento(request):
    form = json.loads(request.body)
    try:
        usuario = Usuario.objects.get(email = form["usuarioEmail"])
        metodoPago = MetodoPago.objects.filter(id=form["metodoPago"]).first()
        dinero = form["dinero"]
        campania = form["campania"]
        agencia = Sucursal.objects.filter(id=form["agencia"]).first()
        fecha = form["fecha"]
        operationType = form["operationType"]
        denominacion = usuario.nombre
        tipoID = "DNI"
        nroID = usuario.dni
        ente_recaudador = CuentaCobranza.objects.filter(id=form["ente_recaudador"]).first()
        observaciones = form["observaciones"]

        message =""
        # Crear el diccionario de descuento
        data_dict ={
            "metodoPago": metodoPago.alias,
            "dinero": dinero,
            "agencia": agencia.pseudonimo,
            "campania": campania,
            "fecha": fecha,
            "concepto": f"{operationType.capitalize()}: {denominacion}",
            "denominacion":denominacion,
            "tipoID":tipoID,
            "nroID":nroID,
            "ente_recaudador":ente_recaudador.alias,
            "observaciones":observaciones
        }

        newMovimiento = MovimientoExterno()
        newMovimiento.metodoPago = metodoPago
        newMovimiento.dinero = dinero
        newMovimiento.agencia = agencia
        newMovimiento.campania = campania
        newMovimiento.fecha = fecha
        newMovimiento.concepto = f"{operationType.capitalize()}: {denominacion}"
        newMovimiento.denominacion = denominacion
        newMovimiento.tipoIdentificacion = tipoID
        newMovimiento.nroIdentificacion = nroID
        newMovimiento.ente = ente_recaudador
        newMovimiento.observaciones = observaciones
        newMovimiento.movimiento = "egreso"

        if(operationType == "descuento"):
            descuentos_actuales = usuario.descuentos # Obtener la lista actual de descuentos, o inicializarla si está vacía
            descuentos_actuales.append(data_dict) # Agregar el nuevo descuento
            usuario.descuentos = descuentos_actuales # Asignar la lista actualizada al campo descuentos
            usuario.save()
            message = "Adelanto aplicado correctamente"
            newMovimiento.adelanto = True

        elif (operationType == "premio"): 
            premios_actuales = usuario.premios # Obtener la lista actual de descuentos, o inicializarla si está vacía
            premios_actuales.append(data_dict) # Agregar el nuevo descuento
            usuario.premios = premios_actuales # Asignar la lista actualizada al campo descuentos
            usuario.save()
            message = "Premio aplicado correctamente"
            newMovimiento.premio = True
        newMovimiento.save()

        iconMessage = "/static/images/icons/checkMark.svg"
        return JsonResponse({"status": True, "message": message, "iconMessage": iconMessage},safe=False)
    except Exception as e:
        print(e)
        iconMessage = "/static/images/icons/error_icon.svg"
        return JsonResponse({"status": False, "iconMessage": iconMessage, "message": "Ocurrió un error al generar el adelanto/premio"},safe=False)


def importar_usuarios(request):
    if request.method == "POST":

        # Recibir el archivo y el dato adicional 'agencia'
        uploaded_file = request.FILES['file']
        agencia = request.POST.get('agencia')

        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(filename)
        new_number_rows_cont = 0

        try:
            df = pd.read_excel(file_path, sheet_name="Colaboradores")
            agencia_object = Sucursal.objects.get(id=agencia)
            for i, row in df.iterrows():
                dni = handle_nan(row['DNI'])
                all_users_by_agency = Usuario.objects.filter(sucursales__id=agencia_object.id).values_list('dni', flat=True)
                print(f"\nUsuarios de la agencia: {all_users_by_agency}\n")
                if not str(dni) in all_users_by_agency:
                    new_number_rows_cont += 1                        
                    usuario = Usuario()
                    rango_formated = row["Rango"].strip().capitalize()
                    usuario = Usuario.objects.create_user(
                        email=row['Email'],
                        nombre=row['Nombre'],
                        dni=row['DNI'],
                        rango=rango_formated,
                        password=str(row['DNI']) + '_elanel'
                    )
                 
                    # Asignar campos adicionales
                    usuario.tel = handle_nan(row['Telefono'])
                    usuario.domic = handle_nan(row['Domicilio'])
                    usuario.prov = handle_nan(row['Provincia'])
                    usuario.loc = handle_nan(row['Localidad'])
                    usuario.cp = handle_nan(row['CP'])
                    usuario.lugar_nacimiento = handle_nan(row['Lugar de nacimiento'])
                    usuario.fec_nacimiento = format_date(handle_nan(row['Fec-Nacimiento']))
                    usuario.fec_ingreso = format_date(handle_nan(row['Fecha ingreso']))
                    usuario.fec_egreso = format_date(handle_nan(row['Fecha egreso']))
                    usuario.estado_civil = handle_nan(row['Estado civil'])
                    usuario.xp_laboral = handle_nan(row['XP Laboral'])
                    usuario.c = str(row['DNI']) + '_elanel'
                    usuario.groups.add(Group.objects.filter(name=rango_formated).first())
                    sucursal_object = agencia_object
                    usuario.sucursales.add(sucursal_object)
                    usuario.save()
                else:
                    continue

            # Segunda pasada para asignar los vendedores a los supervisores
            for _, row in df.iterrows():
                dni_vendedor = handle_nan(row['DNI'])
                supervisor_dni = handle_nan(row['Supervisor'])

                # Obtener el supervisor basado en su DNI
                supervisor = Usuario.objects.filter(dni=str(supervisor_dni)).first()

                if supervisor:
                    # Obtener el vendedor basado en su DNI
                    vendedor = Usuario.objects.filter(dni=str(dni_vendedor)).first()
                    
                    # Crear el diccionario del vendedor
                    vendedor_data = {
                        'nombre': vendedor.nombre,
                        'email': vendedor.email
                    }

                    # Verificar si el campo vendedores_a_cargo existe o está vacío
                    if not supervisor.vendedores_a_cargo:
                        supervisor.vendedores_a_cargo = []

                    # Agregar el vendedor al campo vendedores_a_cargo del supervisor
                    supervisor.vendedores_a_cargo.append(vendedor_data)

                    # Guardar los cambios en el supervisor
                    supervisor.save()

            # Eliminar el archivo después de procesar
            fs.delete(filename)

            iconMessage = "/static/images/icons/checkMark.svg"
            message = f"Datos importados correctamente. Se agregaron {new_number_rows_cont} usuarios nuevos"
            return JsonResponse({"message": message, "iconMessage": iconMessage, "status": True})

        except Exception as e:
            print(f"Error al importar: {e}")

            iconMessage = "/static/images/icons/error_icon.svg"
            message = "Error al procesar el archivo"
            return JsonResponse({"message": message, "iconMessage": iconMessage, "status": False})


#endregion - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    

#region Clientes - - - - - - - - - - - - - - - - - - - - - - -
class ListaClientes(TestLogin, generic.View):
    template_name = "list_customers.html"

    def get_queryset_base(self, request):
        agencias_disponibles_user = request.user.sucursales.all()
        return Cliente.objects.filter(agencia_registrada__in=agencias_disponibles_user)

    def wants_json(self, request):
        return (
            "application/json" in request.headers.get("Accept", "")
            or request.headers.get("X-Requested-With") == "XMLHttpRequest"
        )

    def get(self, request, *args, **kwargs):
        page_number = int(request.GET.get('page', 1))
        page_size   = int(request.GET.get('page_size', 30))
        search      = request.GET.get('search', '')          
        sucursal_id = request.GET.get('sucursal_id')

        userConnected = request.user
        sucursal_ids = userConnected.sucursales.values_list('id', flat=True)
        customer_queryset = Cliente.objects.filter(agencia_registrada__in=sucursal_ids).order_by('nombre')

        if sucursal_id:
            customer_queryset = customer_queryset.filter(agencia_registrada_id=sucursal_id)

        if search:
            customer_queryset = customer_queryset.filter(
                Q(nro_cliente__icontains=search) |
                Q(nombre__icontains=search) |
                Q(dni__icontains=search) |
                Q(prov__icontains=search) |
                Q(loc__icontains=search) |
                Q(tel__icontains=search) 
            ).distinct()
        customer_queryset = customer_queryset.annotate(nro_cli_num=Cast(Substr('nro_cliente', 5), IntegerField())).order_by('-nro_cli_num', '-nro_cliente')
        paginator = Paginator(customer_queryset, page_size)
        page_obj = paginator.get_page(page_number)

        if self.wants_json(request):
            customers_data = []
            for customer in page_obj.object_list:
                customers_data.append({
                    "id": customer.id,
                    "nro_cliente": customer.nro_cliente,
                    "nombre": customer.nombre,
                    "dni": customer.dni,
                    "loc": customer.loc,
                    "prov": customer.prov,
                    "tel": customer.tel,
                })
            return JsonResponse({
                "results": customers_data,
                "total": paginator.count,
            })

        # Render normal HTML
        campaniasDisponibles = getCampanasDisponibles()
        sucursales = [{"id": sucursal.id, "pseudonimo": sucursal.pseudonimo } for sucursal in Sucursal.objects.all() ]
        sucursalesDisponibles = [{"id": sucursal.id, "pseudonimo": sucursal.pseudonimo } for sucursal in request.user.sucursales.all()]

        customers_data = []
        for customer in page_obj.object_list:
            # Agrega el diccionario con la información del usuario y sus sucursales
            customers_data.append({
                "id": customer.id,
                "nro_cliente": customer.nro_cliente,
                "nombre": customer.nombre,
                "dni": customer.dni,
                "loc": customer.loc,
                "prov": customer.prov,
                "tel": customer.tel,
            })
            
        context = {
            "customers": customers_data,
            "campaniasDisponibles": json.dumps(campaniasDisponibles),
            "sucursalesDisponibles": json.dumps(sucursalesDisponibles),
            "sucursales": sucursales,
            "page_obj": page_obj,
        }
        return render(request, self.template_name,context)


@login_required
def importar_clientes(request):
    if request.method != "POST":
        return render(request, 'importar_clientes.html')

    archivo_excel = request.FILES.get('file')
    agencia_key   = request.POST.get('agencia')

    if not archivo_excel:
        return JsonResponse({"status": False, "message": "Subí un archivo.", "iconMessage": "/static/images/icons/error_icon.svg"}, status=400)

    # ✅ validar agencia
    try:
        sucursal_id = int(agencia_key)
    except (TypeError, ValueError):
        return JsonResponse({"status": False, "message": "Agencia inválida.", "iconMessage": "/static/images/icons/error_icon.svg"}, status=400)

    try:
        sucursal = Sucursal.objects.get(pk=sucursal_id)
    except Sucursal.DoesNotExist:
        return JsonResponse({"status": False, "message": "La agencia no existe.", "iconMessage": "/static/images/icons/error_icon.svg"}, status=404)

    fs = FileSystemStorage()
    filename = fs.save(archivo_excel.name, archivo_excel)
    file_path = fs.path(filename)

    try:
        df = preprocesar_excel_clientes(file_path)
        nuevos = 0
        with transaction.atomic():
            for _, row in df.iterrows():
                nro_cliente = handle_nan(row.get('nro'))
                dni = handle_nan(row.get('dni'))

                if not (nro_cliente or dni):
                    continue

                if Cliente.objects.filter(nro_cliente=nro_cliente, dni=dni).exists():
                    continue

                Cliente.objects.create(
                    nro_cliente        = nro_cliente,
                    nombre             = handle_nan(row.get('cliente')),
                    dni                = dni,
                    agencia_registrada = sucursal,
                )
                nuevos += 1

        fs.delete(filename)
        return JsonResponse({
            "status": True,
            "message": f"Se importaron {nuevos} clientes nuevos.",
            "iconMessage": "/static/images/icons/checkMark.svg"
        })
    except Exception as e:
        fs.delete(filename)
        print("Error al importar clientes:", e)
        return JsonResponse({
            "status": False,
            "message": "Error al procesar el archivo.",
            "iconMessage": "/static/images/icons/error_icon.svg"
        }, status=500)   

class CrearCliente(TestLogin, generic.CreateView):
    model = Cliente
    template_name = 'create_customers.html'

    def get(self, request, *args, **kwargs):
        suc = request.user.sucursales.all()[0]
        context = {"customer_number": Cliente.next_for_agencia(suc)}  # solo display
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        errors = {}
        form = json.loads(request.body)

        suc = request.user.sucursales.all()[0]

        customer = Cliente(
            # NO tomes nro_cliente del form, lo asignamos abajo
            nombre=form['nombre'],
            dni=str(form['dni']),
            domic=form.get('domic', ""),
            loc=form.get('loc', ""),
            prov=form.get('prov', ""),
            cod_postal=str(form.get('cod_postal', "")),
            tel=str(form.get('tel', "")),
            estado_civil=form.get('estado_civil') or None,
            fec_nacimiento=form.get('fec_nacimiento') or "",
            ocupacion=form.get('ocupacion') or None,
            agencia_registrada=suc,
        )

        try:
            with transaction.atomic():
                # 1) Asignar número ANTES de validar
                # Si implementaste assign_nro_cliente_if_needed():
                if hasattr(customer, "assign_nro_cliente_if_needed"):
                    customer.assign_nro_cliente_if_needed()
                else:
                    # Si no, asignalo directo:
                    customer.nro_cliente = Cliente.next_for_agencia(suc)

                # 2) Validar y guardar
                customer.full_clean()
                customer.save()

        except ValidationError as e:
            errors.update(e.message_dict)

        if errors:
            return JsonResponse({'success': False, 'errors': errors}, safe=False)

        response_data = {
            "urlRedirect": reverse_lazy('users:list_customers'),
            "success": True,
            "nro_cliente": customer.nro_cliente,
        }
        return JsonResponse(response_data, safe=False)
    
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch') # Para no guardar el cache cuando se presiona el boton de atras
class CuentaUser(TestLogin, generic.DetailView):
    model = Cliente
    template_name = "cuenta_cliente.html"

    def get(self,request,*args,**kwargs):
        self.object = self.get_object()
        ventas = self.object.ventas_nro_cliente.all()

        for i in range (ventas.count()):
            ventas[i].suspenderOperacion()
        
        productosDelCliente = [venta.producto.nombre for venta in self.object.ventas_nro_cliente.all()]
        productosDelCliente_no_repetidos = list(set(productosDelCliente))
        ventasOrdenadas = ventas.order_by("-adjudicado","deBaja","-nro_operacion")
        context = {"customer": self.object,
                   "ventas": ventasOrdenadas,
                   "productoDelCliente": productosDelCliente_no_repetidos,
                   }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            data = json.loads(request.body or "{}")

            nro_operacion = (data.get("nro_operacion") or "").strip()
            producto_name = (data.get("producto") or "").strip()

            qs = self.object.ventas_nro_cliente.all()

            if nro_operacion:
                qs = qs.filter(nro_operacion=nro_operacion)

            if producto_name:
                prod = Products.objects.filter(nombre=producto_name).first()
                if not prod:
                    return JsonResponse({"status": True, "ventas": []})
                qs = qs.filter(producto=prod)

            ventas = qs

            ventas_list = []
            for v in ventas:
                ventas_list.append({
                    "nro_operacion": v.nro_operacion,
                    "cuotas_pagadas": len(v.cuotas_pagadas()),
                    "nro_ordenes": [c["nro_orden"] for c in v.cantidadContratos],
                    "producto": v.producto.nombre,
                    "tipo_producto": v.producto.tipo_de_producto,
                    "img_tipo_producto": "",
                    "fecha_inscripcion": v.fecha,
                    "estado": getEstadoVenta(v),
                    "importe": v.importe,
                    "detail_url": reverse("sales:detail_sale", args=[v.pk]),
                })

            return JsonResponse({"status": True, "ventas": ventas_list})

        except Exception as error:
            # mientras debugueás:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Error en filtro de ventas de CuentaUser")

            return JsonResponse(
                {
                    "status": False,
                    "message": "Filtro fallido",
                    "detalleError": str(error),
                }
            )


class PanelAdmin(TestLogin,PermissionRequiredMixin,generic.View):
    template_name = "panelAdmin.html"
    permission_required = "sales.my_ver_resumen"
    def get(self,request,*args,**kwargs):
        sucursalesObject = Sucursal.objects.all()
        sucursales = [{"pseudonimo":sucursal.pseudonimo,"id":sucursal.id} for sucursal in sucursalesObject ]
        context= {
            "sucursalesDisponibles": json.dumps(sucursales)
        }
        
        return render(request, self.template_name, context)
#endregion  - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


#region Permisos - - - - - - - - - - - - - - - - - - - - - - 
class PanelPermisos(TestLogin, generic.View):
    template_name = "panelPermisos.html"
    
    def get(self,request,*args,**kwargs):
        context= {}
        allPermissions = [perm for perm in Permission.objects.all() if perm.codename.startswith('my_')]
        allGroups = Group.objects.all()
        context["permisos"] = allPermissions
        context["grupos"] = allGroups

        return render(request, self.template_name, context)


def requestPermisosDeGrupo(request):
    group_name = request.GET.get("group",None)
    group = Group.objects.get(name=group_name)
    active_permissions = [perm.name for perm in group.permissions.all()]
    context = {
        "perms": active_permissions
    }
    return JsonResponse(context,safe=False)


def updatePermisosAGrupo(request):
    if request.method == "POST":

        permissionRequest = json.loads(request.body)["permisos"]
        print(permissionRequest)
        groupRequest = json.loads(request.body)["grupo"]
        # Obtener el grupo
        group = Group.objects.get(name=groupRequest)

        # Limpiar los permisos existentes del grupo
        group.permissions.clear()

        # Agregar los nuevos permisos al grupo
        for perm_name in permissionRequest:
            perm = Permission.objects.get(name=perm_name)
            group.permissions.add(perm)


        context = {
            "perms": "Wepsss"
        }
        return JsonResponse(context,safe=False)
    

def createNewGroup(request):
    if request.method == 'POST':
        # Obtener el nombre del nuevo grupo desde la solicitud
        groupRequest = json.loads(request.body)["newGroup"]
        
        try:
            # Verificar si el grupo ya existe
            if Group.objects.filter(name=groupRequest).exists():
                return JsonResponse({'error': 'Ya existe un grupo con ese nombre.'}, safe=False,status=400)

            # Crear un nuevo grupo
            nuevo_grupo = Group.objects.create(name=groupRequest)
            # print(nuevo_grupo)
            return JsonResponse({'mensaje': f'Grupo "{groupRequest}" creado correctamente.',"group":groupRequest},safe=False)

        except Exception as e:
            return JsonResponse({'error': f'Error al crear el grupo: {str(e)}'}, safe=False ,status=400)
    
    return JsonResponse({'error': 'La solicitud debe ser de tipo POST.'}, safe=False ,status=400)


def deleteGrupo(request):
    if request.method =="POST":
        groupRequest = json.loads(request.body)["grupo"]
        group = Group.objects.get(name=groupRequest)
        group.delete()

        context = {}
        return JsonResponse(context,safe=False)


def requestKey(request):
    try:
        data = json.loads(request.body or "{}")
        raw_pass = data.get("pass", "")
        motivo   = data.get("motivo", "baja")  # si querés seguir recibiéndolo

        if not raw_pass:
            return JsonResponse({'status': False, 'message': 'Contraseña requerida'}, status=400)

        user = request.user
        # Si tu User extiende AbstractBaseUser, podés usar: ok = user.check_password(raw_pass)
        ok = check_password(raw_pass, user.password)

        request.session["statusKeyPorcentajeBaja"] = bool(ok)

        if ok:
            return JsonResponse({'status': True, 'message': 'Contraseña correcta'})
        return JsonResponse({'status': False, 'message': 'Contraseña incorrecta'}, status=401)

    except Exception as e:
        return JsonResponse({'status': False, 'message': str(e)}, status=500)

#endregion  - - - - - - - - - - - - - - - - - - - - - - - - - 


#region Cuenta de Cobro
class PanelCuentaCobro(generic.View):
    template_name = "panelCuentaDeCobro.html"
    def get(self,request,*args,**kwargs):
        cuentas = CuentaCobranza.objects.all()
        context= {
            "cuentas": cuentas,
            }
        return render(request, self.template_name, context)

def addCuenta(request):
    if request.method == "POST":
        print (json.loads(request.body))
        alias = json.loads(request.body)["alias"]
        
        newCuenta = CuentaCobranza()
        newCuenta.alias = alias.capitalize()
        newCuenta.save()
        
        response_data = {"message":"Cuenta creada exitosamente!","alias":alias.capitalize()}
        return JsonResponse(response_data,safe=False)
    
def removeCuenta(request):
    if request.method == "POST":
        alias = json.loads(request.body)["alias"] 

        deleteCuenta = CuentaCobranza.objects.get(alias=alias)
        deleteCuenta.delete()
        
        response_data = {"message":"Cuenta eliminada correctamente"}
        return JsonResponse(response_data,safe=False)


#endregion


#region Sucursales - - - - - - - - - - - - - - - - - - - 

class PanelSucursales(TestLogin, generic.View):
    template_name = "panelSucursales.html"
    # permission_required = "sales.my_ver_resumen"
    def get(self,request,*args,**kwargs):
        sucursales = Sucursal.objects.all()
        gerentes = Usuario.objects.filter(rango="Gerente sucursal")

        context= {
            "sucursales": sucursales,
            'gerentesDisponibles': [{"id":gerente.pk,"nombre":gerente.nombre} for gerente in gerentes],
            }
        return render(request, self.template_name, context)

    def post(self,request,*args,**kwargs):
        context = {}
        pk = request.POST.get("inputID")
        direccion = request.POST.get("inputDireccion")
        hora = request.POST.get("inputHora")
        gerente = request.POST.get("gerente")


        # Para editar la sucursal 
        sucursal = Sucursal.objects.get(pk=pk)
        sucursal.direccion = direccion
        sucursal.hora_apertura = hora
        sucursal.gerente = Usuario.objects.filter(nombre=gerente).first()

        sucursal.save()  
        response_data = {'message': 'Datos recibidos correctamente'}
        return JsonResponse(response_data)
    
def updateSucursal(request):
    if request.method == "POST":
        try: 
            pk = json.loads(request.body)["sucursalPk"]
            direccion = json.loads(request.body)["direccion"]
            hora = json.loads(request.body)["horaApertura"]
            gerente = json.loads(request.body)["gerente"]
            


            sucursal = Sucursal.objects.get(pk=pk)
            sucursal.direccion = direccion
            sucursal.hora_apertura = hora
            sucursal.gerente = Usuario.objects.filter(pk=gerente).first()
            sucursal.save()


            iconMessage = "/static/images/icons/checkMark.svg"
            response_data = {"message":"Sucursal actualizada con exito","iconMessage":iconMessage, "status": True}
            return JsonResponse(response_data)
        except Exception as e:
            print(e)
            iconMessage = "/static/images/icons/error_icon.svg"
            response_data = {"message":"Hubo un error al crear la sucursal", "iconMessage":iconMessage, "status": False}
            return JsonResponse(response_data)

def addSucursal(request):
    if request.method == "POST":
        try:
            provincia = json.loads(request.body)["provincia"]
            localidad = json.loads(request.body)["localidad"]
            direccion = json.loads(request.body)["direccion"]
            hora = json.loads(request.body)["horaApertura"]
            gerente = json.loads(request.body)["gerente"]
            
            newSucursal = Sucursal()
            newSucursal.provincia = provincia.title()
            newSucursal.localidad = localidad.title()
            newSucursal.direccion = direccion.capitalize()
            newSucursal.gerente = Usuario.objects.filter(pk=gerente).first()
            newSucursal.hora_apertura = hora
            newSucursal.save()

            iconMessage = "/static/images/icons/checkMark.svg"
            response_data = {"message":"Sucursal creada exitosamente","iconMessage":iconMessage, "status": True, "pk":str(newSucursal.pk),'name': str(newSucursal.pseudonimo), "direccion": str(newSucursal.direccion), "hora": str(newSucursal.hora_apertura),"gerente": {"id":newSucursal.gerente.pk,"nombre":newSucursal.gerente.nombre}}
            return JsonResponse(response_data)
        
        except Exception as e:
            print(e)
            iconMessage = "/static/images/icons/error_icon.svg"
            response_data = {"message":"Hubo un error al crear la sucursal", "iconMessage":iconMessage, "status": False}
            return JsonResponse(response_data)
        
    
def removeSucursal(request):
    if request.method == "POST":
        try:
            pk = int(json.loads(request.body)["pk"]) 

            deleteSucursal = Sucursal.objects.get(pk=pk)

            # Eliminar la relación ManyToMany correctamente
            usuarios_asociados = Usuario.objects.filter(sucursales=deleteSucursal)
            for usuario in usuarios_asociados:
                usuario.sucursales.remove(deleteSucursal)
                
            Ventas.objects.filter(agencia=deleteSucursal).update(agencia=None) # Setear en None las ventas asociadas para que no se borren
            MovimientoExterno.objects.filter(agencia=deleteSucursal).update(agencia=None) # Setear en None los movimientos asociados para que no se borren
            ArqueoCaja.objects.filter(agencia=deleteSucursal).update(agencia=None) # Setear en None los arqueos asociados para que no se borren

            deleteSucursal.delete()
            iconMessage = "/static/images/icons/checkMark.svg"
            response_data = {"message":"Agencia eliminada correctamente","iconMessage":iconMessage, "status": True}
            return JsonResponse(response_data)
        
        except Exception as e:
            iconMessage = "/static/images/icons/error_icon.svg"
            response_data = {"message":"Hubo un error al eliminar la agencia", "iconMessage":iconMessage, "status": False}
            return JsonResponse(response_data)

#endregion  - - - - - - - - - - - - - - - - - - - - - - - -

@login_required
def preview_import_colaboradores(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get('file')
        agencia_id = request.POST.get('agencia')

        if not uploaded_file or not agencia_id:
            return JsonResponse({"status": False, "message": "Faltan datos (archivo o agencia)."})

        try:
            agencia = Sucursal.objects.get(pk=agencia_id)
        except (Sucursal.DoesNotExist, ValueError):
            return JsonResponse({"status": False, "message": "Agencia no encontrada."})

        try:
            try:
                df_raw = pd.read_excel(uploaded_file, sheet_name="DATOS", header=None)
            except ValueError:
                # Si no existe DATOS, intentar por defecto
                df_raw = pd.read_excel(uploaded_file, header=None)

            header_row_idx = 0
            for i, row in df_raw.iterrows():
                row_str = " ".join([str(c).lower() for c in row.values if pd.notna(c)])
                if "vendedor" in row_str and "supervisor" in row_str and "dni" in row_str:
                    header_row_idx = i
                    break
            
            df_raw.columns = df_raw.iloc[header_row_idx]
            df = df_raw.iloc[header_row_idx + 1:].reset_index(drop=True)
            df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]
            
            col_vendedor, col_vendedor_alta, col_vendedor_baja = None, None, None
            col_dni, col_alias, col_cbu, col_entidad = None, None, None, None

            columns_list = list(df.columns)
            for i, col in enumerate(columns_list):
                c_lower = str(col).lower().strip()
                if c_lower == "vendedor":
                    col_vendedor = i
                    if i + 1 < len(columns_list) and "alta" in str(columns_list[i+1]).lower(): col_vendedor_alta = i+1
                    if i + 2 < len(columns_list) and "baja" in str(columns_list[i+2]).lower(): col_vendedor_baja = i+2
                elif c_lower == "dni": col_dni = i
                elif "alias" in c_lower:
                    if col_alias is None: col_alias = i
                elif "cbu" in c_lower or "cvu" in c_lower:
                    if col_cbu is None: col_cbu = i
                elif "entidad" in c_lower or "banco" in c_lower:
                    if col_entidad is None: col_entidad = i

            if col_vendedor is None:
                return JsonResponse({"status": False, "message": "El excel debe contener la columna VENDEDOR."})

            vendedores_to_update = []
            supervisores_to_update = []
            gerentes_to_update = []
            users_to_create = []

            processed_names = set()

            def safe_date(val):
                if pd.isna(val) or str(val).lower() in ["nan", "none", "", "np", "n/p"]: return ""
                if isinstance(val, pd.Timestamp): return val.strftime("%d/%m/%Y")
                val_str = str(val).strip()
                if " " in val_str:
                    try: return datetime.datetime.strptime(val_str.split(" ")[0], "%Y-%m-%d").strftime("%d/%m/%Y")
                    except: pass
                if "-" in val_str:
                    try: return pd.to_datetime(val_str).strftime("%d/%m/%Y")
                    except: pass
                # A veces pandas lee la fecha como Excel epoch int
                try: 
                    if str(val_str).isdigit():
                        return pd.to_datetime('1899-12-30') + pd.to_timedelta(int(val_str), 'D')
                except: pass
                return val_str

            for index, row in df.iterrows():
                def get_val(idx):
                    if idx is None: return ""
                    return row.iloc[idx]

                nombre_vendedor = " ".join(str(get_val(col_vendedor)).split()).title()
                if not nombre_vendedor or nombre_vendedor.lower() in ["nan", "none", "", "np", "n/p"]:
                    continue
                
                if nombre_vendedor in processed_names:
                    continue
                processed_names.add(nombre_vendedor)
                
                f_alta_vendedor = safe_date(get_val(col_vendedor_alta))
                f_baja_vendedor = safe_date(get_val(col_vendedor_baja))

                dni_excel = str(get_val(col_dni)).strip()
                if dni_excel.endswith(".0"): dni_excel = dni_excel[:-2]
                if dni_excel.lower() in ["nan", "none"]: dni_excel = ""
                
                alias_excel = str(get_val(col_alias)).strip()
                cbu_excel = str(get_val(col_cbu)).strip()
                entidad_excel = str(get_val(col_entidad)).strip()
                
                if alias_excel.lower() in ["nan", "none", "nan.0"]: alias_excel = ""
                if cbu_excel.lower() in ["nan", "none", "nan.0", "nan.00"]: cbu_excel = ""
                if entidad_excel.lower() in ["nan", "none", "nan.0"]: entidad_excel = ""
                
                if cbu_excel.endswith(".0"): cbu_excel = cbu_excel[:-2]
                cbu_excel = cbu_excel.replace(" ", "").replace("-", "")[:22]
                alias_excel = alias_excel[:50]
                entidad_excel = entidad_excel[:100]

                match = Usuario.objects.filter(nombre__iexact=nombre_vendedor, sucursales=agencia).first()
                if not match: match = Usuario.objects.filter(nombre__iexact=nombre_vendedor).first()
                
                if match:
                    changed_fields = []
                    if dni_excel and match.dni != dni_excel: changed_fields.append("dni")
                    if alias_excel and match.alias != alias_excel: changed_fields.append("alias")
                    if cbu_excel and match.cbu != cbu_excel: changed_fields.append("cbu")
                    if entidad_excel and match.entidad_bancaria != entidad_excel: changed_fields.append("entidad_bancaria")
                    if f_alta_vendedor and match.fec_ingreso != f_alta_vendedor: changed_fields.append("fec_ingreso")
                    if f_baja_vendedor and match.fec_egreso != f_baja_vendedor: changed_fields.append("fec_egreso")

                    needs_update = len(changed_fields) > 0

                    if needs_update or not match.dni or not match.alias or not match.cbu or not match.fec_ingreso:
                        obj = {
                            "index": len(processed_names),
                            "user_id": match.pk,
                            "nombre": match.nombre,
                            "rango": match.rango,
                            "dni": dni_excel or match.dni,
                            "alias": alias_excel or match.alias,
                            "cbu": cbu_excel or match.cbu,
                            "entidad_bancaria": entidad_excel or match.entidad_bancaria,
                            "fec_ingreso": f_alta_vendedor or match.fec_ingreso,
                            "fec_egreso": f_baja_vendedor or match.fec_egreso,
                            "agencia_actual": ", ".join([s.pseudonimo for s in match.sucursales.all()]),
                            "changed": changed_fields
                        }
                        if match.rango == "Supervisor": supervisores_to_update.append(obj)
                        elif match.rango == "Gerente sucursal": gerentes_to_update.append(obj)
                        else: vendedores_to_update.append(obj)
                else:
                    users_to_create.append({
                        "index": len(processed_names),
                        "nombre": nombre_vendedor,
                        "dni": dni_excel,
                        "alias": alias_excel,
                        "cbu": cbu_excel,
                        "entidad_bancaria": entidad_excel,
                        "fec_ingreso": f_alta_vendedor,
                        "fec_egreso": f_baja_vendedor,
                        "rango": "Vendedor"
                    })

            return JsonResponse({
                "status": True, 
                "vendedores": vendedores_to_update,
                "supervisores": supervisores_to_update,
                "gerentes": gerentes_to_update,
                "nuevos": users_to_create
            })

        except Exception as e:
            return JsonResponse({"status": False, "message": str(e)})

    return JsonResponse({"status": False, "message": "Método HTTP no permitido."})

@login_required
def clean_excel_preview(request):
    if request.method == "POST":
        try:
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return JsonResponse({"status": False, "message": "No se subió ningún archivo."})

            # Intentar abrir con openpyxl por defecto
            try:
                xl = pd.ExcelFile(uploaded_file, engine='openpyxl')
            except Exception as e:
                # Si falla, intentar sin motor explícito (podría ser .xls)
                try:
                    xl = pd.ExcelFile(uploaded_file)
                except Exception as e2:
                    return JsonResponse({"status": False, "message": f"No se pudo abrir el archivo Excel: {str(e2)}"})

            sheet_names = xl.sheet_names
            
            # Normalizar nombres de hojas (quitar espacios y pasar a mayúsculas)
            normalized_sheets = {s.strip().upper(): s for s in sheet_names}
            
            required_sheets = {
                "ESTADO": ["ESTADO", "ESTADOS"],
                "RESUMEN": ["RESUMEN"],
                "CLIENTES": ["CLIENTES", "CLIENTE"],
                "DATOS": ["DATOS"]
            }
            
            results = {}
            for key, variants in required_sheets.items():
                found = False
                for variant in variants:
                    if variant.upper() in normalized_sheets:
                        results[key] = {
                            "found": True,
                            "real_name": normalized_sheets[variant.upper()]
                        }
                        found = True
                        break
                if not found:
                    results[key] = {"found": False, "real_name": None}
            
            return JsonResponse({"status": True, "sheets": results})
        except Exception as e:
            return JsonResponse({"status": False, "message": f"Error interno: {str(e)}"})
    return JsonResponse({"status": False, "message": "Método no permitido."})

@login_required
def clean_excel_execute(request):
    if request.method == "POST":
        try:
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return JsonResponse({"status": False, "message": "No se subió ningún archivo."})

            # Intentar determinar el motor
            engine = 'openpyxl' if uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xlsm') else None

            try:
                xl = pd.ExcelFile(uploaded_file, engine=engine)
            except Exception as e:
                xl = pd.ExcelFile(uploaded_file)

            sheet_names = xl.sheet_names
            normalized_sheets = {s.strip().upper(): s for s in sheet_names}
            
            output_sheets_map = {
                "ESTADO": ["ESTADO", "ESTADOS"],
                "RESUMEN": ["RESUMEN"],
                "CLIENTES": ["CLIENTES", "CLIENTE"],
                "DATOS": ["DATOS"]
            }
            
            import io
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for out_name, variants in output_sheets_map.items():
                    real_name = None
                    for v in variants:
                        if v.upper() in normalized_sheets:
                            real_name = normalized_sheets[v.upper()]
                            break
                    
                    if real_name:
                        # Para leer los datos, usamos el mismo objeto de archivo
                        # Aseguramos que el puntero esté al inicio si es necesario
                        uploaded_file.seek(0)
                        
                        # Usar engine_kwargs solo si el motor es openpyxl
                        engine_kwargs = {"data_only": True} if engine == 'openpyxl' else {}
                        
                        df = pd.read_excel(
                            uploaded_file, 
                            sheet_name=real_name, 
                            dtype=str, 
                            engine=engine,
                            engine_kwargs=engine_kwargs
                        )
                        df = df.fillna("")
                    else:
                        df = pd.DataFrame()
                    
                    df.to_excel(writer, sheet_name=out_name, index=False)
            
            output.seek(0)
            
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            base_name, _ = os.path.splitext(uploaded_file.name)
            response['Content-Disposition'] = f'attachment; filename="clean_{base_name}.xlsx"'
            return response
            
        except Exception as e:
            return JsonResponse({"status": False, "message": f"Error al procesar: {str(e)}"})
    return JsonResponse({"status": False, "message": "Método no permitido."})

@login_required
@transaction.atomic
def confirm_import_colaboradores(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            agencia_id = data.get("agencia")
            if not agencia_id:
                return JsonResponse({"status": False, "message": "Falta seleccionar la agencia."})
            agencia = Sucursal.objects.get(pk=agencia_id)
            
            updates = data.get("updates", [])
            creates = data.get("creates", [])
            
            # Phase 1: Create and Update
            for c in updates:
                user = Usuario.objects.filter(pk=c["user_id"]).first()
                if user:
                    user.dni = str(c.get("dni", "")).strip()[:12]
                    user.alias = str(c.get("alias", "")).strip()[:50]
                    cbu_raw = str(c.get("cbu", "")).strip()
                    if cbu_raw.endswith(".0"): cbu_raw = cbu_raw[:-2]
                    user.cbu = cbu_raw.replace(" ", "").replace("-", "")[:22]
                    user.entidad_bancaria = str(c.get("entidad_bancaria", "")).strip()[:100]
                    
                    user.fec_ingreso = str(c.get("fec_ingreso", "")).strip()[:10]
                    user.save() # Trigger model hook before assigning egreso
                    
                    user.fec_egreso = str(c.get("fec_egreso", "")).strip()[:10]
                    user.suspendido = True if user.fec_egreso else False
                    
                    if not user.sucursales.filter(pk=agencia.pk).exists():
                        user.sucursales.add(agencia)
                        
                    user.save()
            
            for c in creates:
                nombre = str(c.get("nombre", "")).strip().title()
                if not nombre: continue
                dni_excel = str(c.get("dni", "")).strip()[:12]
                rango_str = str(c.get("rango", "Vendedor")).strip()
                base_email = f"{nombre.replace(' ', '').lower()}@gmail.com"
                
                try: rango_group = Group.objects.get(name=rango_str)
                except Group.DoesNotExist: rango_group = Group.objects.get(name="Vendedor")
                
                # Verify DNI
                if dni_excel and Usuario.objects.filter(dni=dni_excel).exists():
                    dni_excel = ""
                
                # Ensure unique email
                if Usuario.objects.filter(email=base_email).exists():
                    import uuid
                    base_email = f"{nombre.replace(' ', '').lower()}{str(uuid.uuid4())[:4]}@gmail.com"
                
                new_user = Usuario.objects.create_user(
                    email=base_email,
                    nombre=nombre,
                    dni=dni_excel,
                    rango=rango_str,
                    password="klf781CL"
                )
                
                new_user.c = "klf781CL"
                new_user.alias = str(c.get("alias", "")).strip()[:50]
                cbu_raw = str(c.get("cbu", "")).strip()
                if cbu_raw.endswith(".0"): cbu_raw = cbu_raw[:-2]
                new_user.cbu = cbu_raw.replace(" ", "").replace("-", "")[:22]
                new_user.entidad_bancaria = str(c.get("entidad_bancaria", "")).strip()[:100]
                
                new_user.fec_ingreso = str(c.get("fec_ingreso", "")).strip()[:10]
                new_user.save() # Trigger model hook before assigning egreso
                
                new_user.fec_egreso = str(c.get("fec_egreso", "")).strip()[:10]
                new_user.suspendido = True if new_user.fec_egreso else False
                
                new_user.sucursales.add(agencia)
                new_user.groups.add(rango_group)
                new_user.setAdditionalPasswords()
                new_user.save()

            return JsonResponse({"status": True, "message": "Datos de colaboradores guardados y actualizados correctamente."})
        except Exception as e:
            return JsonResponse({"status": False, "message": str(e)})
            
    return JsonResponse({"status": False, "message": "Método HTTP no permitido."})

@login_required
def sync_payment_dates_execute(request):
    if request.method == "POST":
        try:
            file_actual = request.FILES.get('file_actual')
            file_backup = request.FILES.get('file_backup')
            if not file_actual or not file_backup:
                return JsonResponse({"status": False, "message": "Faltan archivos para procesar."})

            engine_backup = 'openpyxl' if file_backup.name.endswith(('.xlsx', '.xlsm')) else None
            engine_actual = 'openpyxl' if file_actual.name.endswith(('.xlsx', '.xlsm')) else None

            try:
                xl_backup = pd.ExcelFile(file_backup, engine=engine_backup)
            except Exception:
                xl_backup = pd.ExcelFile(file_backup)

            import re
            
            def normalize_txt(s):
                if s is None or str(s).lower() == 'nan': return ""
                return re.sub(r'[^a-z0-9]', '', str(s).lower())
                
            key_columns = ["Cod.Cli", "Nombre y Apell", "cuotas", "ID Venta", "NRO DE ORDEN"]
            norm_key_cols = [normalize_txt(c) for c in key_columns]
            
            # --- Encontrar hoja en Backup donde esten las columnas ---
            sheet_datos_backup = None
            for s_name in xl_backup.sheet_names:
                if s_name.strip().upper() in ["ESTADO", "ESTADOS"]:
                    sheet_datos_backup = s_name
                    break
                    
            if not sheet_datos_backup:
                return JsonResponse({"status": False, "message": "El archivo Backup debe contener alguna hoja llamada ESTADO o ESTADOS."})

            df_raw = pd.read_excel(file_backup, sheet_name=sheet_datos_backup, header=None, dtype=str, engine=engine_backup)
            df_raw = df_raw.fillna("")
            
            header_idx_backup = -1
            vistos_backup = []
            
            for idx, row in df_raw.head(30).iterrows():
                row_vals = [normalize_txt(v) for v in row.values]
                vistos_backup.append([str(v) for v in row.values if str(v).strip()])
                
                found_all = True
                for col in norm_key_cols:
                    if not any((col in v or v in col) for v in row_vals if v):
                        found_all = False
                        break
                        
                if found_all:
                    header_idx_backup = idx
                    break
                
            if header_idx_backup == -1:
                return JsonResponse({"status": False, "message": f"No se encontraron las columnas clave en la hoja {sheet_datos_backup} del Backup. Vistas guardadas: {vistos_backup[:4]}"})

            file_backup.seek(0)
            df_backup = pd.read_excel(file_backup, sheet_name=sheet_datos_backup, header=header_idx_backup, dtype=str, engine=engine_backup)
            df_backup = df_backup.fillna("")
            
            col_map_backup = {}
            for expected in norm_key_cols:
                exact_match = None
                fuzzy_match = None
                for c in df_backup.columns:
                    c_norm = normalize_txt(c)
                    if c_norm == expected:
                        exact_match = c
                        break
                    elif c_norm and (expected in c_norm or c_norm in expected):
                        fuzzy_match = c
                col_map_backup[expected] = exact_match if exact_match else fuzzy_match
            
            fecha_col = None
            for c in df_backup.columns:
                c_norm = normalize_txt(c)
                if c_norm and ('fechadepago' in c_norm):
                    fecha_col = c
                    break
                    
            if not fecha_col:
                return JsonResponse({"status": False, "message": f"La columna 'Fecha de Pago' no se detectó en la hoja detectada ({sheet_datos_backup}) del Backup."})

            def clean_key_val(val):
                if val is None or str(val).strip().lower() in ['nan', 'none', '']: return ""
                v = str(val).strip().replace('.0', '').lower()
                return ' '.join(v.split())

            backup_dict = {}
            for _, row in df_backup.iterrows():
                row_key = []
                for expected in norm_key_cols:
                    exact_col = col_map_backup.get(expected)
                    if exact_col:
                        row_key.append(clean_key_val(row[exact_col]))
                    else:
                        row_key.append("")
                
                k = tuple(row_key)
                val = str(row[fecha_col]).strip()
                if val and val.lower() != 'nan':
                    backup_dict[k] = val
                    
            print(f"\n==============================================")
            print(f"✅ DEBUG: DATOS EXTRAIDOS DEL BACKUP")
            print(f"==============================================")
            print(f"✔️  Mapeo de Columnas: {col_map_backup}")
            print(f"✔️  Columna de Fecha Detectada: {fecha_col}")
            print(f"✔️  Total Fechas de Backup en Memoria: {len(backup_dict)}")
            ejemplos_backup = list(backup_dict.items())[:2] if backup_dict else []
            print(f"✔️  Ejemplo 2 Filas en Backup: {ejemplos_backup}")
            print(f"==============================================\n")

            # Procesar el archivo Actual usando win32com para hacer puente nativo con Excel y evadir errores de openpyxl
            import tempfile
            import os
            try:
                import pythoncom
                import win32com.client
            except ImportError:
                return JsonResponse({"status": False, "message": "Falta la librería pywin32 para procesar archivos con macros. Corre pip install pywin32"})
            
            ext = os.path.splitext(file_actual.name)[1].lower()
            if not ext: ext = ".xlsx"
            
            file_actual.seek(0)
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(file_actual.read())
                tmp_actual_path = tmp.name

            updated_count = 0
            pythoncom.CoInitialize()
            excel = None
            wb_actual = None
            try:
                excel = win32com.client.DispatchEx("Excel.Application")
                excel.Visible = False
                excel.DisplayAlerts = False
                excel.AskToUpdateLinks = False
                excel.EnableEvents = False  # MUY IMPORTANTE: Suprime popups de VBA como el Worksheet_Change
                
                wb_actual = excel.Workbooks.Open(tmp_actual_path, UpdateLinks=0, ReadOnly=False)
                excel.Calculation = -4135  # Apagar recálculo automático mientras iteramos (Acelera 1000x)
                
                sheet_actual = None
                for sh in wb_actual.Sheets:
                    if str(sh.Name).strip().upper() in ["ESTADO", "ESTADOS"]:
                        sheet_actual = sh
                        break
                        
                if not sheet_actual:
                    raise Exception("El archivo Actual debe contener la hoja ESTADO o ESTADOS.")
                    
                try:
                    sheet_actual.Unprotect("12841")
                except Exception as e:
                    print(f"DEBUG: No se pudo desproteger la hoja: {e}")

                max_c = min(sheet_actual.UsedRange.Columns.Count, 200)
                max_r_header = min(sheet_actual.UsedRange.Rows.Count, 50)
                if max_c < 1 or max_r_header < 1:
                    raise Exception("La hoja de estado parece vacía.")
                    
                header_vals = sheet_actual.Range(sheet_actual.Cells(1, 1), sheet_actual.Cells(max_r_header, max_c)).Value
                if not isinstance(header_vals, tuple):
                    header_vals = ((header_vals,),)
                    
                header_row = -1
                col_map_actual = {}
                vistos_actual = []
                
                for r_idx, row_tuple in enumerate(header_vals):
                    r = r_idx + 1 
                    row_vals = {}
                    vistos_row = []
                    for c_idx, val in enumerate(row_tuple):
                        c = c_idx + 1
                        if val is not None:
                            val_norm = normalize_txt(val)
                            row_vals[val_norm] = c
                            vistos_row.append(str(val))
                    if vistos_row: vistos_actual.append(vistos_row)
                            
                    found_all = True
                    for expected in norm_key_cols:
                        if not any((expected in v or v in expected) for v in row_vals.keys() if v):
                            found_all = False
                            break
                            
                    if found_all:
                        header_row = r
                        for expected in norm_key_cols:
                            exact_m = None
                            fuzzy_m = None
                            for v, c_idx in row_vals.items():
                                if v == expected:
                                    exact_m = c_idx
                                    break
                                elif v and (expected in v or v in expected):
                                    fuzzy_m = c_idx
                            col_map_actual[expected] = exact_m if exact_m else fuzzy_m
                                    
                        fecha_c_idx = None
                        for v, c_idx in row_vals.items():
                            if v and ('fechadepago' in v):
                                fecha_c_idx = c_idx
                                break
                        if fecha_c_idx:
                            col_map_actual['fechadepago'] = fecha_c_idx
                        break
                        
                if header_row == -1:
                    raise Exception(f"No se encontraron las columnas clave. Vistas: {str(vistos_actual[:4])}")
                    
                if 'fechadepago' not in col_map_actual:
                    fecha_col_idx = sheet_actual.UsedRange.Columns.Count + 1
                    sheet_actual.Cells(header_row, fecha_col_idx).Value = "Fecha de Pago"
                    col_map_actual['fechadepago'] = fecha_col_idx
                else:
                    fecha_col_idx = col_map_actual['fechadepago']
                    
                total_rows = sheet_actual.UsedRange.Rows.Count
                start_r = header_row + 1
                end_r = min(total_rows, 200000)
                
                actual_keys_debug = []
                
                if start_r <= end_r:
                    # Leer bloque de una vez es infinitamente mas rapido para iterar
                    block_vals = sheet_actual.Range(sheet_actual.Cells(start_r, 1), sheet_actual.Cells(end_r, sheet_actual.UsedRange.Columns.Count)).Value
                    if not isinstance(block_vals, tuple):
                        block_vals = ((block_vals,),)
                        
                    # Extraer LA COLUMNA de fechas actual exactamente como esta
                    rng_fechas = sheet_actual.Range(sheet_actual.Cells(start_r, fecha_col_idx), sheet_actual.Cells(end_r, fecha_col_idx))
                    fechas_vals = rng_fechas.Value
                    if not isinstance(fechas_vals, tuple):
                        fechas_vals = ((fechas_vals,),)
                    fechas_mutables = [list(r) for r in fechas_vals]
                        
                    matches_debug = []
                    clientes_actualizados_log = []
                    
                    for block_r_idx, row_tuple in enumerate(block_vals):
                        r = start_r + block_r_idx
                        row_key = []
                        for expected in norm_key_cols:
                            c_idx = col_map_actual.get(expected)
                            if c_idx and c_idx <= len(row_tuple):
                                row_key.append(clean_key_val(row_tuple[c_idx - 1]))
                            else:
                                row_key.append("")
                                
                        k_tuple = tuple(row_key)
                        if any(row_key):
                            if len(actual_keys_debug) < 2:
                                actual_keys_debug.append(k_tuple)
                        
                        current_val = fechas_mutables[block_r_idx][0]
                        current_str = str(current_val).strip() if current_val is not None else ""
                        if current_str.lower() in ['nan', 'none']: 
                            current_str = ""
                            
                        # Si la fila tiene sentido y la fecha actual está Vacia, inyectamos la de Backup dinamicamente
                        if any(row_key) and not current_str and k_tuple in backup_dict:
                            fechas_mutables[block_r_idx][0] = backup_dict[k_tuple]
                            updated_count += 1
                            if len(matches_debug) < 5:
                                matches_debug.append((r, k_tuple, backup_dict[k_tuple]))
                                
                            nombre_cliente = k_tuple[1] if len(k_tuple) > 1 else str(k_tuple)
                            clientes_actualizados_log.append(f"{nombre_cliente} se agregó la Fecha: {backup_dict[k_tuple]}")
                            
                    if updated_count > 0:
                        # Asegurar el marshalling COM exigiendo una tupla de tuplas e ignorando Nones puros
                        for fix_r in range(len(fechas_mutables)):
                            val_t = fechas_mutables[fix_r][0]
                            if val_t is None or str(val_t).lower() in ['nan', 'none']:
                                fechas_mutables[fix_r][0] = ""
                            else:
                                v_n = str(val_t)
                                if "+00:00" in v_n: v_n = v_n.split("+")[0].strip()
                                if " 00:00:00" in v_n: v_n = v_n.replace(" 00:00:00", "").strip()
                                fechas_mutables[fix_r][0] = v_n
                                
                        safe_array = tuple(tuple(row) for row in fechas_mutables)
                        # INYECCIÓN ATÓMICA ULTRA RÁPIDA DE MILISEGUNDOS
                        rng_fechas = sheet_actual.Range(sheet_actual.Cells(start_r, fecha_col_idx), sheet_actual.Cells(end_r, fecha_col_idx))
                        rng_fechas.Value = safe_array
                            
                    print(f"\n==============================================")
                    print(f"✅ DEBUG: DATOS EXTRAIDOS DEL ACTUAL")
                    print(f"==============================================")
                    print(f"✔️  Fila del Encabezado (Actual): {header_row}")
                    print(f"✔️  Mapeo de Columnas (ID Columna): {col_map_actual}")
                    print(f"✔️  Columna donde escribirá ID: {fecha_col_idx}")
                    print(f"✔️  Ejemplo 2 Filas evaluadas: {actual_keys_debug}")
                    print(f"✔️  Primeros 5 Exitos (Fila, Clave, Fecha Asignada):")
                    for m in matches_debug:
                        print(f"     -> {m}")
                    print(f"\n✔️  LISTADO COMPLETO DE CLIENTES ACTUALIZADOS:")
                    for cli_log in clientes_actualizados_log:
                        print(f"     * {cli_log}")
                    print(f"\n✔️  Filas Actualizadas Total: {updated_count}")
                    print(f"==============================================\n")
                            
                try:
                    sheet_actual.Protect("12841")
                except Exception:
                    pass
                    
                excel.Calculation = -4105 # xlCalculationAutomatic 
                wb_actual.Save()
                wb_actual.Close(False)
                wb_actual = None
                
            except Exception as e:
                return JsonResponse({"status": False, "message": f"Error modificando el Excel nativo (COM): {str(e)}"})
            finally:
                try:
                    if wb_actual: wb_actual.Close(False)
                except: pass
                try:
                    if excel is not None: excel.Quit()
                except: pass
                
            with open(tmp_actual_path, "rb") as f:
                output_data = f.read()
            os.remove(tmp_actual_path)
            
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            if ext == '.xlsm':
                content_type = 'application/vnd.ms-excel.sheet.macroEnabled.12'

            response = HttpResponse(
                output_data,
                content_type=content_type
            )
            base_name, _ = os.path.splitext(file_actual.name)
            response['Content-Disposition'] = f'attachment; filename="synced_{base_name}{ext}"'
            response['Access-Control-Expose-Headers'] = 'X-Sync-Count'
            response['X-Sync-Count'] = str(updated_count)
            return response

        except Exception as e:
            return JsonResponse({"status": False, "message": f"Error al procesar: {str(e)}"})
            
    return JsonResponse({"status": False, "message": "Método HTTP no permitido."})