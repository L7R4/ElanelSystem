from datetime import datetime
from django.contrib.auth.models import Group,Permission
from django import forms
from django.contrib.auth.forms import AuthenticationForm,UserChangeForm
from .models import Usuario, Cliente, Sucursal
import re

rangos = Group.objects.all()



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
            'maxlength':"24", 
            'class': 'input-read-write-default'
        }
    ))
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput(
        attrs={
            'id': 'password2',
            'required': 'required',
            'autocomplete': 'off',
            'maxlength':"24", 
            'class': 'input-read-write-default'
        }
    ))

    """
        CAMPOS A VALIDAR EN EL FORMULARIO
    """
    class Meta:
        model = Usuario
        fields =["nombre","email" ,"dni", "rango", "tel", "domic", "prov", "cp", "loc" ,"lugar_nacimiento", "fec_nacimiento","fec_ingreso", "estado_civil", "xp_laboral"]

        widgets ={
            'email': forms.EmailInput(
            attrs= {
                'id': 'emailInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"100",
                'class': 'input-read-write-default'
            }
            ),
            'nombre': forms.TextInput(
            attrs= {
                'id': 'nombreInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"100",
                'class': 'input-read-write-default'
            }
            ),
            'dni': forms.TextInput(
            attrs= {
                'id': 'dniInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"8",
                'class': 'input-read-write-default'
            }
            ),
            'rango': forms.TextInput(
            attrs= {
                'id': 'rangoInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"20",
                'class': 'selectInput input-read-write-default onlySelect'
            }
            ),
            'tel': forms.TextInput(
            attrs= {
                'id': 'telInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"11",
                'class': 'input-read-write-default'
            }
            ),
            'domic': forms.TextInput(
            attrs= {
                'id': 'domicInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"200",
                'class': 'input-read-write-default'
            }
            ),
            'prov': forms.TextInput(
            attrs= {
                'id': 'provInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"40",
                'class': 'input-read-write-default'
            }
            ),
            'cp': forms.TextInput(
            attrs= {
                'id': 'cpInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"5",
                'class': 'input-read-write-default'
            }
            ),
            'loc': forms.TextInput(
            attrs= {
                'id': 'locInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"100",
                'class': 'input-read-write-default'
            }
            ),
            'lugar_nacimiento': forms.TextInput(
            attrs= {
                'id': 'lugar_nacimientoInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"100",
                'class': 'input-read-write-default'
            }
            ),
            'fec_nacimiento': forms.TextInput(
            attrs= {
                'id': 'fec_nacimientoInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"10",
                'class': 'input-read-write-default'
            }
            ),
            'fec_ingreso': forms.TextInput(
            attrs= {
                'id': 'fecIngresoInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"10",
                'class': 'input-read-write-default'
            }
            ),
            'estado_civil': forms.TextInput(
            attrs= {
                'id': 'estado_civilInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"20",
                'class': 'input-read-write-default'
            }
            ),
            'xp_laboral': forms.Textarea(
            attrs= {
                'id': 'xp_laboralInput',
                'required': 'required',
                'autocomplete': 'off',
                'class': 'input-read-write-default'
            }
            ),
        }

    # def clean_sucursal(self):
    #     sucursal = self.cleaned_data['sucursal']
    #     print("SUCURSALES PERMITIDAS --------------------------------------------->")
    #     print(sucursal)
        
    

    def clean_rango(self):
        rango = self.cleaned_data['rango']
        rangos_permitidas = [m.name.lower() for m in rangos]

        if rango.lower() not in rangos_permitidas:
           raise forms.ValidationError('Rango inválido')
        return rango
    

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


class UsuarioUpdateForm(forms.ModelForm):

    """
        CAMPOS ADICIONALES A LOS DEL MODELO 'USUARIO'
    """
    password1 = forms.CharField(label="Contraseña" ,widget=forms.PasswordInput(
        attrs={
            'id': 'password1',
            'required': 'required',
            'autocomplete': 'off',
            'maxlength':"24",
            'class': 'input-read-write-default'
        }
    ))
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput(
        attrs={
            'id': 'password2',
            'required': 'required',
            'autocomplete': 'off',
            'maxlength':"24",
            'class': 'input-read-write-default'

        }
    ))

    """
        CAMPOS A VALIDAR EN EL FORMULARIO
    """
    class Meta:
        model = Usuario
        fields =["nombre","email" ,"dni", "rango", "tel", "domic", "prov", "cp", "loc", "lugar_nacimiento", "fec_nacimiento","fec_ingreso","estado_civil", "xp_laboral"]

        widgets ={
            'email': forms.EmailInput(
            attrs= {
                'id': 'emailInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"100",
                'class': 'input-read-write-default'
            }
            ),
            'nombre': forms.TextInput(
            attrs= {
                'id': 'nombreInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"100",
                'class': 'input-read-write-default'
            }
            ),
            'dni': forms.TextInput(
            attrs= {
                'id': 'dniInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"8",
                'class': 'input-read-write-default'
            }
            ),
            'rango': forms.TextInput(
            attrs= {
                'id': 'rangoInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"20",
                'class': 'selectInput input-read-write-default onlySelect',
                'readonly': 'readonly'
            }
            ),
            'tel': forms.TextInput(
            attrs= {
                'id': 'telInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"11",
                'class': 'input-read-write-default'
            }
            ),
            'domic': forms.TextInput(
            attrs= {
                'id': 'domicInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"200",
                'class': 'input-read-write-default'
            }
            ),
            'prov': forms.TextInput(
            attrs= {
                'id': 'provInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"40",
                'class': 'input-read-write-default'
            }
            ),
            'cp': forms.TextInput(
            attrs= {
                'id': 'cpInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"5",
                'class': 'input-read-write-default'
            }
            ),
            'loc': forms.TextInput(
            attrs= {
                'id': 'locInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"100",
                'class': 'input-read-write-default'
            }
            ),
            'lugar_nacimiento': forms.TextInput(
            attrs= {
                'id': 'lugar_nacimientoInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"100",
                'class': 'input-read-write-default'
            }
            ),
            'fec_nacimiento': forms.TextInput(
            attrs= {
                'id': 'fec_nacimientoInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"10",
                'class': 'input-read-write-default'
            }
            ),
            'fec_ingreso': forms.TextInput(
            attrs= {
                'id': 'fecIngresoInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"10",
                'class': 'input-read-write-default'
            }
            ),
            'estado_civil': forms.TextInput(
            attrs= {
                'id': 'estado_civilInput',
                'required': 'required',
                'autocomplete': 'off',
                'maxlength':"20",
                'class': 'input-read-write-default'
            }
            ),
            'xp_laboral': forms.Textarea(
            attrs= {
                'id': 'xp_laboralInput',
                'required': 'required',
                'autocomplete': 'off',
                'class': 'input-read-write-default'
            }
            ),
        }

    

    #region VALIDACIONES DE CAMPOS
    def clean_rango(self):
        rango = self.cleaned_data['rango']
        rangos_permitidas = [m.name.lower() for m in rangos]

        if rango.lower() not in rangos_permitidas:
           raise forms.ValidationError('Rango inválido')
        return rango
    

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
    

    def clean_tel(self):
        tel = self.cleaned_data['tel']
        if not tel.isdigit():
            raise forms.ValidationError('Numero invalido')
        
        if len(tel) < 8 or len(tel) > 11:
            raise forms.ValidationError('Numero invalido')
        return tel
    
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # usuario actual desde la instancia del formulario
        usuario_actual = self.instance

        if email and email != usuario_actual.email:
            # Verificar si el correo electrónico ya existe en la base de datos
            existing_user = Usuario.objects.filter(email=email)
            if existing_user.exists():
                raise forms.ValidationError("¡Email ya registrado!")

            # Validar la estructura del correo electrónico usando una expresión regular
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                raise forms.ValidationError("Email invalido")

        return email
    
    #endregion


class CreateClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ('nro_cliente','nombre','dni','domic','loc','prov','cod_postal','tel','fec_nacimiento','estado_civil','ocupacion')  # Esto incluirá todos los campos del modelo en el formulario
        
        # Labels de los campos
        labels = {
            'nro_cliente': 'Nro Cliente',
            'nombre': 'Nombre',
            'dni': 'DNI',
            'domic': 'Domicilio',
            'loc': 'Localidad',
            'prov': 'Provincia',
            'cod_postal': 'Código Postal',
            'tel': 'Teléfono',
            'fec_nacimiento': 'Fecha de Nacimiento',
            'estado_civil': 'Estado Civil',
            'ocupacion': 'Ocupación'
        }
        
        # Clases de los campos llamada input-read-write-default
        widgets = {
            'nro_cliente': forms.TextInput(attrs={'class': 'input-read-write-default', 'readonly': 'readonly'}),
            'nombre': forms.TextInput(attrs={'class': 'input-read-write-default'}),
            'dni': forms.TextInput(attrs={'class': 'input-read-write-default', 'type': 'number','oninput':"if(this.value.length > 9) this.value = this.value.slice(0, 9);"}),
            'domic': forms.TextInput(attrs={'class': 'input-read-write-default'}),
            'loc': forms.TextInput(attrs={'class': 'input-read-write-default'}),
            'prov': forms.TextInput(attrs={'class': 'input-read-write-default'}),
            'cod_postal': forms.TextInput(attrs={'class': 'input-read-write-default','type': 'number','oninput':"if(this.value.length > 7) this.value = this.value.slice(0, 7);"}),
            'tel': forms.TextInput(attrs={'class': 'input-read-write-default','type': 'number'}),
            'fec_nacimiento': forms.TextInput(attrs={'class': 'input-read-write-default','maxlength':"10"}),
            'estado_civil': forms.TextInput(attrs={'class': 'input-read-write-default'}),
            'ocupacion': forms.TextInput(attrs={'class': 'input-read-write-default'})
        }
    
    def clean_nro_cliente(self):
        nro_cliente = int(self.cleaned_data['nro_cliente'].split("_")[1])
        print(f"Cantidad de clientes: {Cliente.objects.count()}")
        if(Cliente.objects.count() != 0):
            last_cliente = int(Cliente.objects.last().nro_cliente.split("_")[1])
            if(nro_cliente != last_cliente+1):
                raise forms.ValidationError("Número de cliente incorrecto")
        else:
            return 'cli_1'
        return f"cli_{nro_cliente}"

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        nombre = nombre.title()
        if not re.match(r'^[a-zA-Z\s]*$', nombre):
            raise forms.ValidationError('Ingrese solo letras')
        return nombre.title()

    def clean_dni(self):
        dniRequest = self.cleaned_data['dni']
        existing_client = Cliente.objects.filter(dni=dniRequest)
        if not dniRequest.isdigit():
            raise forms.ValidationError('DNI inválido')
        
        if existing_client.exists():
            raise forms.ValidationError("Este DNI ya existe")
        if len(dniRequest) < 8:
            raise forms.ValidationError("DNI inválido")
        return str(dniRequest)

    def clean_prov(self):
        prov = self.cleaned_data['prov']
        prov = prov.capitalize()
        return prov.capitalize()
    
    def clean_loc(self):
        loc = self.cleaned_data['loc']
        loc = loc.capitalize()
        return loc.capitalize()

    def clean_estado_civil(self):
        estado_civil = self.cleaned_data['estado_civil']
        estado_civil = estado_civil.capitalize()
        if not re.match(r'^[a-zA-Z\s]*$', estado_civil):
            raise forms.ValidationError('Ingrese solo letras')
        return estado_civil.capitalize()
    
    def clean_ocupacion(self):
        ocupacion = self.cleaned_data['ocupacion']
        ocupacion = ocupacion.capitalize()
        if not re.match(r'^[a-zA-Z\s]*$', ocupacion):
            raise forms.ValidationError('Ingrese solo letras')
        return ocupacion.capitalize()

    def clean_cod_postal(self):
        cod_postal = self.cleaned_data['cod_postal']
        if not cod_postal.isdigit():
            raise forms.ValidationError('Valor invalido')
        return str(cod_postal)

    def clean_tel(self):
        tel = self.cleaned_data['tel']
        if not str(tel).isdigit():
            raise forms.ValidationError('Numero invalido')
        
        if len(str(tel)) < 8 or len(str(tel)) > 11:
            raise forms.ValidationError('Numero invalido')
        return str(tel)
    
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