from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario, Cliente
import re

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())


class FormCreateUser(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = Usuario
        fields =[
            'nombre',
            'email',
            'tel',
            'rango',
        ]

class CreateClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ('nro_cliente','nombre','dni','domic','loc','prov','cod_postal','tel','fec_nacimiento','estado_civil','ocupacion')  # Esto incluirá todos los campos del modelo en el formulario

    # Puedes agregar validaciones personalizadas aquí si es necesario
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if not re.match(r'^[a-zA-Z\s]*$', nombre):
            raise forms.ValidationError('Ingrese solo letras en el campo de nombre.')
        return nombre

    def clean_dni(self):
        dni = self.cleaned_data['dni']
        if not dni.isdigit():
            raise forms.ValidationError('Ingrese un número válido en el campo de DNI.')
        return dni

    def clean_prov(self):
        prov = self.cleaned_data['prov']
        if not prov.isalpha():
            raise forms.ValidationError('Ingrese solo letras en el campo de provincia.')
        return prov

    def clean_cod_postal(self):
        cod_postal = self.cleaned_data['cod_postal']
        if not cod_postal.isdigit():
            raise forms.ValidationError('Ingrese un número válido en el campo de código postal.')
        return cod_postal

    def clean_tel(self):
        tel = self.cleaned_data['tel']
        if not str(tel).isdigit():
            raise forms.ValidationError('Ingrese un número válido en el campo de teléfono.')
        return tel