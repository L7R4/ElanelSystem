
import datetime
import os
from django.conf import settings
from django.contrib.auth.models import Group,Permission
from django.forms import ValidationError
from django.shortcuts import redirect, render
from django.views import generic

from users.utils import printPDFNewUSer

from .models import Usuario,Cliente,Sucursal
from sales.models import Ventas
from .forms import CreateClienteForm, FormCreateUser, UsuarioUpdateForm
from django.urls import reverse_lazy
from django.contrib.auth.models import Permission
from sales.mixins import TestLogin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

import json
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse, JsonResponse

#region Usuarios - - - - - - - - - - - - - - - - - - - -
class CrearUsuario(TestLogin, generic.View):
    model = Usuario
    form_class = FormCreateUser
    template_name = "create_user.html"
    roles = Group.objects.all()

    def get(self,request,*args, **kwargs):
        context = {}
        sucursales = Sucursal.objects.all()
        context["sucursales"] = sucursales
        context["roles"] = self.roles

        context["form"] = self.form_class
        return render(request, self.template_name,context)
    

    def post(self,request,*args, **kwargs):
        form =self.form_class(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data["nombre"]
            dni = form.cleaned_data["dni"]
            email = form.cleaned_data["email"]
            sucursal = request.POST.get("sucursal")
            tel = form.cleaned_data["tel"]
            rango = form.cleaned_data["rango"]
            password1 = form.cleaned_data["password1"]
            password2 = form.cleaned_data["password2"]
            new_user = self.model.objects.create_user(
                email=email,
                nombre=nombre,
                dni=dni,
                rango=rango,
                password=password2
            )
            sucursalObject = Sucursal.objects.get(pseudonimo = sucursal)
            new_user.sucursal = sucursalObject
            if not Sucursal.objects.filter(pk=sucursalObject.pk).exists():
                raise ValidationError('Sucursal inválida')
            
            new_user.tel = tel
            new_user.c = form.cleaned_data["password1"]
            new_user.is_active = True
            new_user.domic = form.cleaned_data["domic"]
            new_user.prov = form.cleaned_data["prov"]
            new_user.cp = form.cleaned_data["cp"]
            new_user.loc = form.cleaned_data["loc"]
            new_user.lugar_nacimiento = form.cleaned_data["lugar_nacimiento"]
            new_user.fec_nacimiento = form.cleaned_data["fec_nacimiento"]
            new_user.fec_ingreso = form.cleaned_data["fec_ingreso"]
            new_user.estado_civil = form.cleaned_data["estado_civil"]
            new_user.xp_laboral = form.cleaned_data["xp_laboral"]

            # Para guardar los familiares en caso que haya
            familiares = []
            for key, value in request.POST.items():
                if key.startswith('familia_nombre_') and value:
                    familiares.append({
                        'relacion': request.POST.get(f'familia_relacion_{key.split("_")[-1]}', ''),
                        'nombre': value,
                        'tel': request.POST.get(f'familia_tel_{key.split("_")[-1]}', '')
                    })
            new_user.datos_familiares = familiares
            # ------------------------------------------------------------------------------
            

            # Para guardar los vendedores a cargo en caso que haya
            vendedores = []
            for key, value in request.POST.items():
                if key.startswith('idv_') and value:
                    vendedores.append({
                        'nombre': Usuario.objects.get(email=value).nombre,
                        'email': value,
                    })
            new_user.vendedores_a_cargo = vendedores
            # ------------------------------------------------------------------------------       

            # Para establecer al grupo que pertence segun el rango
            grupo = Group.objects.get(name=rango)
            new_user.groups.add(grupo)
            # -------------------------------------------------------
                
            new_user.save()
            response_data = {"urlPDF":reverse_lazy('users:newUserPDF',args=[new_user.pk]),"urlRedirect": reverse_lazy('users:list_customers'),"success": True}
            
            return JsonResponse(response_data, safe=False)

        else:
            context = {}
            sucursales = Sucursal.objects.all()
            context["sucursales"] = sucursales
            context["roles"] = self.roles
            context["form"] = form
            return render(request, self.template_name,context)
        
        
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
                "agenciaNombre": newUserObject.sucursal,
                "provincia_localidad_sucursal": newUserObject.sucursal.localidad + "," + newUserObject.sucursal.provincia,
                "agenciaDireccion": newUserObject.sucursal.direccion,
            }
            
    userName = str(newUserObject.nombre)
    urlPDF= os.path.join(settings.PDF_STORAGE_DIR, "newUser.pdf")
    
    printPDFNewUSer(context,request.build_absolute_uri(),urlPDF)

    with open(urlPDF, 'rb') as pdf_file:
        response = HttpResponse(pdf_file,content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename='+userName+"_ficha"+'.pdf'
        return response
    

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
            data_user["sucursal"] = str(c.sucursal)
            data_user["tel"] = c.tel
            data_user["rango"] = c.rango
            users_list.append(data_user)
        data = json.dumps(users_list)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponse(data, 'application/json')
        return render(request, self.template_name,context)


def requestUsuariosAcargo(request):
    sucursalName = request.GET.get("sucursal",None)
    usuarioPk = request.GET.get("usuario",None)
    usuarioObject = Usuario.objects.get(pk=usuarioPk)
    
    if sucursalName !="":
        sucursalObject = Sucursal.objects.get(pseudonimo = sucursalName)
        usuarios_filtrados = Usuario.objects.filter(sucursal = sucursalObject, rango="Vendedor").exclude(pk=usuarioPk)
        usuarios_filtrados_listDict = list({"nombre": item.nombre, "email":item.email} for item in usuarios_filtrados)

    else:
        usuarios_filtrados = Usuario.objects.filter(rango = "Vendedor")
        usuarios_filtrados_listDict = list({"nombre": item.nombre, "email":item.email} for item in usuarios_filtrados)
    
    
    return JsonResponse({"data":usuarios_filtrados_listDict, "vendedores_a_cargo": usuarioObject.vendedores_a_cargo})

def requestUsuarios(request):
    sucursalName = request.GET.get("sucursal",None)
    
    if sucursalName !="":
        sucursalObject = Sucursal.objects.get(pseudonimo = sucursalName)
        usuarios_filtrados = Usuario.objects.filter(sucursal = sucursalObject, rango="Vendedor")
        usuarios_filtrados_listDict = list({"nombre": item.nombre, "email":item.email} for item in usuarios_filtrados)

    else:
        usuarios_filtrados = Usuario.objects.filter(rango = "Vendedor")
        usuarios_filtrados_listDict = list({"nombre": item.nombre, "email":item.email} for item in usuarios_filtrados)
    
    
    return JsonResponse({"data":usuarios_filtrados_listDict})


class DetailUser(TestLogin, generic.DetailView):
    model = Usuario
    template_name = "detail_user.html"
    roles = Group.objects.all()
    
    def get(self,request,*args,**kwargs):
        self.object = self.get_object()
        context ={}
        context["form"] = UsuarioUpdateForm(instance = self.object)
        sucursales = Sucursal.objects.all()
        context["sucursales"] = sucursales
        context["roles"] = self.roles
        context["sucursal_object"] = self.object.sucursal
        context["familiares"] = self.object.datos_familiares
        context["object"] = self.get_object()

        if self.object.rango == "Supervisor":
            vendedores_a_cargo = self.object.vendedores_a_cargo
            vendedores_sucursal = Usuario.objects.filter(sucursal=self.object.sucursal, rango="Vendedor")

            # Excluir vendedores que están a cargo
            vendedores_disponibles = vendedores_sucursal.exclude(email__in=[vendedor['email'] for vendedor in vendedores_a_cargo])
            
            context["vendedor_a_cargo"] = vendedores_a_cargo
            context["vendedores"] = vendedores_disponibles

        return render(request, self.template_name, context)
    

    def post(self,request,*args, **kwargs):
        self.object = self.get_object()
        form =UsuarioUpdateForm(request.POST, instance = self.object)
        updateUser = Usuario.objects.get(pk = self.object.pk)

        if form.is_valid():
            nombre = form.cleaned_data["nombre"]
            dni = form.cleaned_data["dni"]
            email = form.cleaned_data["email"]
            sucursal = request.POST.get("sucursal")
            updateUser.sucursal = Sucursal.objects.get(pseudonimo = sucursal)
            

            tel = form.cleaned_data["tel"]
            rango = form.cleaned_data["rango"]
            password1 = form.cleaned_data["password1"]
            password2 = form.cleaned_data["password2"]

            updateUser.rango = rango
            if(rango != "Supervisor"):
                updateUser.vendedores_a_cargo = []
            else:
                # Para guardar los vendedores a cargo en caso que haya
                vendedores = []
                for key, value in request.POST.items():
                    if key.startswith('idv_') and value:
                        vendedores.append({
                            'nombre': Usuario.objects.get(email=value).nombre,
                            'email': value,
                        })
                updateUser.vendedores_a_cargo = vendedores
            # ------------------------------------------------------------------------------       
            
            updateUser.nombre = nombre
            updateUser.tel = tel
            updateUser.email = email
            updateUser.dni = dni
            updateUser.c = password1
            updateUser.set_password(password1)
            

            grupo = Group.objects.get(name=rango)

            updateUser.groups.clear()
            updateUser.groups.add(grupo)
            updateUser.save()
            
            response_data = {"urlPDF":reverse_lazy('users:newUserPDF',args=[updateUser.pk]),"urlRedirect": reverse_lazy('users:list_customers'),"success": True}
            return JsonResponse(response_data, safe=False)


        else:
            context = {}
            sucursales = Sucursal.objects.all()
            context["sucursales"] = sucursales
            context["roles"] = self.roles
            context["form"] = form
            print(form)
            return render(request, self.template_name,context)
        return redirect("users:list_users")
    
#endregion - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
#region Clientes - - - - - - - - - - - - - - - - - - - - - - -
class ListaClientes(TestLogin, generic.View):
    model = Cliente
    template_name= "list_customers.html"

    def get(self,request,*args, **kwargs):
        # print(request.user.get_all_permissions())
        customers = Cliente.objects.filter(agencia_registrada = request.user.sucursal)
        context = {
            "customers": customers
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

   
class CrearCliente(TestLogin, generic.CreateView):
    model = Cliente
    template_name = 'create_customers.html'
    form_class = CreateClienteForm


    def get(self, request,*args, **kwargs):
        context = {}
        context["customer_number"] = Cliente.returNro_Cliente
        context['form'] = self.form_class
        return render(request, self.template_name, context)
    

    def post(self,request,*args,**kwargs):
        
        form =self.form_class(request.POST)
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
                customer.agencia_registrada = request.user.sucursal
                customer.save()              
                return redirect("users:list_customers")
        else:
            context = {}
            context["customer_number"] = Cliente.returNro_Cliente
            context['form'] = form
            return render(request, self.template_name, context)


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

        ventasOrdenadas = ventas.order_by("-adjudicado","deBaja","-nro_operacion")
        context = {"customer": self.object,
                   "ventas": ventasOrdenadas}
        return render(request, self.template_name, context)


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
        # print(groupRequest)
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

        context = {
            "message": "toda piola wachin"
        }
        return JsonResponse(context,safe=False)
#endregion  - - - - - - - - - - - - - - - - - - - - - - - - - 

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
        newSucursal.provincia = provincia
        newSucursal.localidad = localidad
        newSucursal.direccion = direccion
        newSucursal.hora_apertura = hora
        newSucursal.save()
        
        response_data = {"message":"Sucursal creada exitosamente!!","pk":str(newSucursal.pk),'name': str(newSucursal.pseudonimo), "direccion": str(newSucursal.direccion), "hora": str(newSucursal.hora_apertura)}
        return JsonResponse(response_data)
    
def removeSucursal(request):
    if request.method == "POST":
        print(json.loads(request.body)["pk"])
        pk = int(json.loads(request.body)["pk"])
        deleteSucursal = Sucursal.objects.get(pk=pk)
        deleteSucursal.delete()
        
        response_data = {"message":"Eliminado correctamente"}
        return JsonResponse(response_data)

#endregion  - - - - - - - - - - - - - - - - - - - - - - - -