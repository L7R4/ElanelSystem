from datetime import datetime
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario, Cliente
import re


rangos = Usuario.RANGOS



class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())


class FormCreateUser(forms.ModelForm):
    """
        CAMPOS ADICIONALES A LOS DEL MODELO 'USUARIO'
    """
    password1 = forms.CharField(label="Contraseña" ,widget=forms.PasswordInput(
        attrs={
            'id': 'password1',
            'required': 'required',
            'autocomplete': 'off',
            'maxlength':"24"
        }
    ))
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput(
        attrs={
            'id': 'password2',
            'required': 'required',
            'autocomplete': 'off',
            'maxlength':"24"
        }
    ))

    """
        CAMPOS A VALIDAR EN EL FORMULARIO
    """
    class Meta:
        model = Usuario
        fields =["nombre","email" ,"dni","sucursal", "rango", "tel"]
        widgets ={
            'email': forms.EmailInput(
                attrs= {
                    'id': 'emailInput',
                    'required': 'required',
                    'autocomplete': 'off',
                    'maxlength':"100"
                }
            ),
            'nombre': forms.TextInput(
                attrs= {
                    'id': 'nombreInput',
                    'required': 'required',
                    'autocomplete': 'off',
                    'maxlength':"100"
                }
            ),
            'dni': forms.TextInput(
                attrs= {
                    'id': 'dniInput',
                    'required': 'required',
                    'autocomplete': 'off',
                    'maxlength':"8"
                }
            ),
            'sucursal': forms.TextInput(
                attrs= {
                    'id': 'sucursalInput',
                    'required': 'required',
                    'autocomplete': 'off',
                    'maxlength':"50",
                    'class': 'selectInput'
                }
            ),
            'rango': forms.TextInput(
                attrs= {
                    'id': 'rangoInput',
                    'required': 'required',
                    'autocomplete': 'off',
                    'maxlength':"20",
                    'class': 'selectInput'
                }
            ),
            'tel': forms.TextInput(
                attrs= {
                    'id': 'telInput',
                    'required': 'required',
                    'autocomplete': 'off',
                    'maxlength':"11"
                }
            )
        }

    def clean_password2(self):
        passw1 = self.cleaned_data['password1']
        passw2 = self.cleaned_data['password2']
        if(passw1 != passw2):
            raise forms.ValidationError('Las contraseñas no coinciden')
        return passw2
    

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
    
    def clean_sucursal(self,sucursal):
        sucursales = Usuario.SUCURSALES
        sucursales_permitidas = [m[0].lower() for m in sucursales]
        if sucursal.lower() not in sucursales_permitidas:
            return ('Sucursal inválida')

        return sucursal
    
    def clean_rango(self,rango):
        rangos = Usuario.RANGOS
        rangos_permitidas = [m[0].lower() for m in rangos]
        if rango.lower() not in rangos_permitidas:
           return('Rango inválido')

        return rango
    

    def clean_tel(self):
        tel = self.cleaned_data['tel']
        if not tel.isdigit():
            raise forms.ValidationError('Numero invalido')
        
        if len(tel) < 8 or len(tel) > 11:
            raise forms.ValidationError('Numero invalido')
        return tel
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Verificar si el correo electrónico ya existe en la base de datos
            existing_user = Usuario.objects.filter(email=email)
            if existing_user.exists():
                raise forms.ValidationError("¡Email ya registrado!")

            # Validar la estructura del correo electrónico usando una expresión regular
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                raise forms.ValidationError("Email invalido")

        return email
            
        
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