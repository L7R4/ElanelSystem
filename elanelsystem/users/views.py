from django.shortcuts import redirect, render
from django.views import generic
from .models import Usuario,Cliente
from .forms import FormCreateUser
from django.urls import reverse_lazy

import json
from django.http import HttpResponseRedirect, HttpResponse

class CrearUsuario(generic.View):
    model = Usuario
   
    template_name = "create_user.html"
    # success_url = reverse_lazy('')
    

    def get(self,request,*args, **kwargs):
        context = {}
        return render(request, self.template_name,context)
    
    def post(self,request,*args, **kwargs):
        form = FormCreateUser()
        if request.method == "POST":
                nombre = request.POST.get('nombre')
                email = request.POST.get('email')
                tel = request.POST.get('tel')
                rango = request.POST.get('rango')
                password1 = request.POST.get('password1')
                password2 = request.POST.get('password2')
                usuario_admin = True

                new_user= self.model.objects.create_user(
                email=email,
                nombre=nombre,
                rango=rango,
                password = password2)
                new_user.rango = rango
                new_user.save()

        else:
                print(form)
                # message_error = {"message": "No valido"}
        return redirect("sales:resumen")

class ListaUsers(generic.ListView):
    model = Usuario
    template_name = "list_users.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = self.model.objects.all()
        return context
    

class ListaClientes(generic.View):
    model = Cliente
    template_name= "list_customers.html"

    def get(self,request,*args, **kwargs):
        customers = Cliente.objects.all()
        context = {
            "customers": customers
        }
        customers_list = []
        for c in customers:
            data_customer = {}
            data_customer["nro_cliente"] = c.nro_cliente
            data_customer["nombre"] = c.nombre
            data_customer["dni"] = c.dni
            data_customer["domic"] = c.domic
            data_customer["loc"] = c.loc
            data_customer["prov"] = c.prov
            data_customer["cod_postal"] = c.cod_postal
            data_customer["tel"] = c.tel
            data_customer["fec_nacimiento"] = c.fec_nacimiento
            data_customer["estado_civil"] = c.estado_civil
            data_customer["ocupacion"] = c.ocupacion
            customers_list.append(data_customer)
        data = json.dumps(customers_list)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponse(data, 'application/json')
        return render(request, self.template_name,context)