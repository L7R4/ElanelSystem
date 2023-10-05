from typing import Any
from django.shortcuts import redirect, render
from django.views import generic
from .models import Usuario,Cliente
from sales.models import Ventas
from .forms import FormCreateUser
from django.urls import reverse_lazy

import json
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse

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
    
class CrearCliente(generic.CreateView):
    model = Cliente
    template_name = 'create_customers.html'
    fields = "__all__"
    success_url = reverse_lazy('sales:create_sale')

    def get(self, request,*args, **kwargs):
        context = {}
        context["customer_number"] = Cliente.returNro_Cliente
        return render(request, self.template_name, context)
    

class CuentaUser(generic.DetailView):
    model = Cliente
    template_name = "cuenta_cliente.html"

    def get(self,request,*args,**kwargs):
        # planes = Plan.objects.all()
        self.object = self.get_object()
        ventas = self.object.ventas_nro_cliente.all()

        for i in range (ventas.count()):
            ventas[i].suspenderOperacion()

        ventasOrdenadas = ventas.order_by("-adjudicado","deBaja","-nro_operacion")
        context = {"customer": self.object,
                   "ventas": ventasOrdenadas}
        return render(request, self.template_name, context)