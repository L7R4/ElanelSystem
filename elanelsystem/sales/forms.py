from django import forms
from .models import Ventas
from users.models import Cliente, Usuario
from products.models import Products

getCustomerNumber = Cliente.objects.all()
getCustomerName = Cliente.objects.all()
getProducts = Products.objects.all()
getVendedores = Usuario.objects.filter(rango = "Vendedor")
getSupervisores = Usuario.objects.filter(rango = "Supervisor")


class FormCreateVenta(forms.Form):
    nro_cliente = forms.ModelChoiceField(queryset=getCustomerNumber,to_field_name="nro_cliente")
    nombre_completo = forms.ModelChoiceField(queryset=getCustomerName,to_field_name="nombre")
    nro_solicitud = forms.CharField()
    modalidad =forms.CharField()
    nro_cuotas = forms.CharField()
    importe = forms.FloatField()    
    tasa_interes = forms.FloatField()
    intereses_generados = forms.FloatField()
    importe_x_cuota =forms.FloatField()
    total_a_pagar = forms.FloatField()
    fecha = forms.CharField()
    tipo_producto =forms.CharField()
    producto = forms.ModelChoiceField(queryset=getProducts,to_field_name="nombre")
    paquete = forms.CharField()
    nro_orden = forms.CharField()
    vendedor =forms.ModelChoiceField(queryset=getVendedores,to_field_name="nombre")
    supervisor = forms.ModelChoiceField(queryset=getSupervisores,to_field_name="nombre")
    observaciones = forms.CharField(required=False)
