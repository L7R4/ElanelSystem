
import datetime
import os
import re
from django.conf import settings
from django.contrib.auth.models import Group,Permission
from django.forms import ValidationError
from django.db.utils import IntegrityError
from django.shortcuts import redirect, render
from django.views import generic

from users.utils import printPDFNewUSer

from .models import Usuario,Cliente,Sucursal,Key
from products.models import Products
from sales.models import CuentaCobranza
from sales.models import Ventas,ArqueoCaja,MovimientoExterno
from sales.utils import getEstadoVenta
# from .forms import CreateClienteForm
from django.urls import reverse_lazy
from django.contrib.auth.models import Permission
from sales.mixins import TestLogin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.validators import validate_email
import json
from django.http import HttpResponse, JsonResponse


from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator
#region Usuarios - - - - - - - - - - - - - - - - - - - -

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
        print(sucursales_split)
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
  
class ListaUsers(TestLogin,PermissionRequiredMixin,generic.ListView):
    model = Usuario
    template_name = "list_users.html"
    permission_required = "sales.my_ver_resumen"
    def get(self,request,*args, **kwargs):
        users = Usuario.objects.all()
        context = {
            "users": users
        }
        users_list = []
        for c in users:
            data_user = {}
            data_user["pk"] = c.pk
            data_user["nombre"] = c.nombre
            data_user["dni"] = c.dni
            data_user["email"] = c.email
            # data_user["sucursal"] = str(c.sucursal)
            data_user["tel"] = c.tel
            data_user["rango"] = c.rango
            users_list.append(data_user)
        data = json.dumps(users_list)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponse(data, 'application/json')
        return render(request, self.template_name,context)

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

    
#endregion - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    

#region Clientes - - - - - - - - - - - - - - - - - - - - - - -
class ListaClientes(TestLogin, generic.View):
    model = Cliente
    template_name= "list_customers.html"

    def get(self,request,*args, **kwargs):
        customers = Cliente.objects.filter(agencia_registrada = request.user.sucursales.all()[0])
        context = {
            "customers": customers
        }
        customers_list = []
        for c in customers:
            data_customer = {}
            data_customer["nombre"] = c.nombre
            data_customer["dni"] = c.dni
            data_customer["tel"] = c.tel
            data_customer["loc"] = c.loc
            data_customer["prov"] = c.prov
            customers_list.append(data_customer)
       

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'response':customers_list},safe=False)
        return render(request, self.template_name,context)

   
class CrearCliente(TestLogin, generic.CreateView):
    model = Cliente
    template_name = 'create_customers.html'


    def get(self, request,*args, **kwargs):
        context = {}
        context["customer_number"] = Cliente.returNro_Cliente
        return render(request, self.template_name, context)
    

    def post(self,request,*args,**kwargs):
        errors = {}
        form = json.loads(request.body)
        
        customer = Cliente()
        customer.nro_cliente = form["nro_cliente"]
        customer.nombre = form['nombre']
        customer.dni = str(form['dni'])
        customer.domic = form['domic']
        customer.loc = form['loc']
        customer.prov = form['prov']
        customer.cod_postal = str(form['cod_postal'])
        customer.tel = str(form['tel'])
        customer.estado_civil = form['estado_civil']
        customer.fec_nacimiento = form['fec_nacimiento']
        customer.ocupacion = form['ocupacion']
        customer.agencia_registrada = request.user.sucursales.all()[0]

        try:
            customer.full_clean()
        except ValidationError as e:
            errors.update(e.message_dict)
              

        if len(errors) != 0:
            print(errors)
            return JsonResponse({'success': False, 'errors': errors}, safe=False)  
        else:
            customer.save()

            response_data = {"urlRedirect": reverse_lazy('users:list_customers'),"success": True}
            return JsonResponse(response_data, safe=False)     

@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch') # Para no guardar el cache cuando se presiona el boton de atras
class CuentaUser(TestLogin, generic.DetailView):
    model = Cliente
    template_name = "cuenta_cliente.html"

    def get(self,request,*args,**kwargs):
        # planes = Plan.objects.all()
        self.object = self.get_object()
        # print(self.object.agencia_registrada)
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
    
    def post(self,request,*args,**kwargs):
        try:

            form = json.loads(request.body)

            # Obtenemos los valores de las claves del JSON o None si no existen
            nro_operacion = form.get("nro_operacion", None)
            producto = form.get("producto", None)

            # Construimos un diccionario de filtros dinámicamente basado en los valores existentes
            filters = {}
            if nro_operacion is not None:
                filters["nro_operacion"] = nro_operacion
            if producto is not None:
                filters["producto"] = Products.objects.get(nombre=producto).pk

            # Realizar la consulta solo con los filtros disponibles
            ventas = Ventas.objects.filter(**filters)

            ventas_list = []
            ventaDict ={}
            for venta in ventas:
                ventaDict = {
                    "nro_operacion": venta.nro_operacion,
                    "cuotas_pagadas": len(venta.cuotas_pagadas()),
                    "nro_ordenes" : [contrato["nro_orden"] for contrato in venta.cantidadContratos],
                    "producto": venta.producto.nombre,
                    "tipo_producto": venta.producto.tipo_de_producto,
                    "img_tipo_producto": "",
                    "fecha_inscripcion": venta.fecha,
                    "estado": getEstadoVenta(venta),
                    "importe": venta.importe,
                }
                ventas_list.append(ventaDict)


            # Convertir el QuerySet a una lista para que sea serializable por JSON


            return JsonResponse({"status": True,"ventas":ventas_list}, safe=False)

        except Exception as error:   
            return JsonResponse({"status": False,"message":"Filtro fallido","detalleError":str(error)}, safe=False)


class PanelAdmin(TestLogin,PermissionRequiredMixin,generic.View):
    template_name = "panelAdmin.html"
    permission_required = "sales.my_ver_resumen"
    def get(self,request,*args,**kwargs):
        context= {}
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
    if request.method =="POST":
        keyPassaword = json.loads(request.body)["pass"]
        motivo = json.loads(request.body)["motivo"]
        key = Key.objects.get(motivo = motivo)

        if(key.password == int(keyPassaword)): 
            request.session["statusKeyPorcentajeBaja"] = True
            return JsonResponse({'status': True, 'message': 'Contraseña correcta'},safe=False)
        else:
            request.session["statusKeyPorcentajeBaja"] = False
            return JsonResponse({'status': False, 'message': 'Contraseña incorrecta'},safe=False)
            

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
        context= {
            "sucursales": sucursales,
            }
        return render(request, self.template_name, context)

    def post(self,request,*args,**kwargs):
        context = {}
        pk = request.POST.get("inputID")
        direccion = request.POST.get("inputDireccion")
        hora = request.POST.get("inputHora")

        # Para editar la sucursal 
        sucursal = Sucursal.objects.get(pk=pk)
        sucursal.direccion = direccion
        sucursal.hora_apertura = hora

        sucursal.save()  
        response_data = {'message': 'Datos recibidos correctamente'}
        return JsonResponse(response_data)
    
def updateSucursal(request):
    if request.method == "POST":
        pk = json.loads(request.body)["sucursalPk"]
        direccion = json.loads(request.body)["direccion"]
        hora = json.loads(request.body)["horaApertura"]
        
        sucursal = Sucursal.objects.get(pk=pk)
        sucursal.direccion = direccion
        sucursal.hora_apertura = hora
        sucursal.save()
        
        response_data = {"message":"Sucursal actualizada con exito!!"}
        return JsonResponse(response_data)

def addSucursal(request):
    if request.method == "POST":
        provincia = json.loads(request.body)["provincia"]
        localidad = json.loads(request.body)["localidad"]
        direccion = json.loads(request.body)["direccion"]
        hora = json.loads(request.body)["horaApertura"]
        
        newSucursal = Sucursal()
        newSucursal.provincia = provincia.title()
        newSucursal.localidad = localidad.title()
        newSucursal.direccion = direccion.capitalize()
        newSucursal.hora_apertura = hora
        newSucursal.save()
        
        response_data = {"message":"Sucursal creada exitosamente!!","pk":str(newSucursal.pk),'name': str(newSucursal.pseudonimo), "direccion": str(newSucursal.direccion), "hora": str(newSucursal.hora_apertura)}
        return JsonResponse(response_data)
    
def removeSucursal(request):
    if request.method == "POST":
        pk = int(json.loads(request.body)["pk"]) 

        deleteSucursal = Sucursal.objects.get(pk=pk)

        Usuario.objects.filter(sucursal=deleteSucursal).update(sucursal=None) # Setear en None los usuarios asociados para que no se borren
        Ventas.objects.filter(agencia=deleteSucursal).update(agencia=None) # Setear en None las ventas asociadas para que no se borren
        MovimientoExterno.objects.filter(agencia=deleteSucursal).update(agencia=None) # Setear en None los movimientos asociados para que no se borren
        ArqueoCaja.objects.filter(agencia=deleteSucursal).update(agencia=None) # Setear en None los arqueos asociados para que no se borren

        deleteSucursal.delete()
        
        response_data = {"message":"Eliminado correctamente"}
        return JsonResponse(response_data)

#endregion  - - - - - - - - - - - - - - - - - - - - - - - -