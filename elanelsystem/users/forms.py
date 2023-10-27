from datetime import datetime
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

    
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        nombre = nombre.title()
        if not re.match(r'^[a-zA-Z\s]*$', nombre):
            raise forms.ValidationError('Ingrese solo letras')
        return nombre

    def clean_dni(self):
        dniRequest = self.cleaned_data['dni']
        existing_client = Cliente.objects.filter(dni=dniRequest)
        if not dniRequest.isdigit():
            raise forms.ValidationError('DNI inválido')
        
        if existing_client.exists():
            print("Este DNI ya pertenece a otro cliente")
            raise forms.ValidationError("Este DNI ya existe")
        if len(dniRequest) != 8:
            raise forms.ValidationError("DNI inválido")
        return dniRequest

    def clean_prov(self):
        prov = self.cleaned_data['prov']
        prov = prov.capitalize()
        return prov
    
    def clean_loc(self):
        loc = self.cleaned_data['loc']
        loc = loc.capitalize()
        return loc

    def clean_estado_civil(self):
        estado_civil = self.cleaned_data['estado_civil']
        estado_civil = estado_civil.capitalize()
        if not re.match(r'^[a-zA-Z\s]*$', estado_civil):
            raise forms.ValidationError('Ingrese solo letras')
        return estado_civil
    
    def clean_ocupacion(self):
        ocupacion = self.cleaned_data['ocupacion']
        ocupacion = ocupacion.capitalize()
        if not re.match(r'^[a-zA-Z\s]*$', ocupacion):
            raise forms.ValidationError('Ingrese solo letras')
        return ocupacion


    def clean_cod_postal(self):
        cod_postal = self.cleaned_data['cod_postal']
        if not cod_postal.isdigit():
            raise forms.ValidationError('Valor invalido')
        return cod_postal

    def clean_tel(self):
        tel = self.cleaned_data['tel']
        if not str(tel).isdigit():
            raise forms.ValidationError('Numero invalido')
        
        if len(str(tel)) < 8 or len(str(tel)) > 11:
            raise forms.ValidationError('Numero invalido')
        return tel
    
    def clean_fec_nacimiento(self):
    
        fecha_input = self.cleaned_data['fec_nacimiento']

        # Validar que la fecha tenga el formato "dd/mm/yyyy" usando una expresión regular
        pattern = re.compile(r'^\d{2}/\d{2}/\d{4}$')
        if not pattern.match(fecha_input):
            raise forms.ValidationError('El formato de la fecha debe ser "dd/mm/yyyy".')

        # Validar que la fecha sea válida en el calendario
        try:
            fecha_valida = datetime.strptime(fecha_input, '%d/%m/%Y')
        except ValueError:
            raise forms.ValidationError('Fecha no válida')
        if(datetime.strptime(fecha_input, '%d/%m/%Y') > datetime.today()):
            raise forms.ValidationError('Fecha no válida')
        
        # Si es necesario, puedes devolver la fecha como objeto datetime
        # return fecha_valida
        return fecha_input