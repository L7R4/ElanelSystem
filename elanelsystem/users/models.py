from django.db import models
from django.dispatch import receiver
from django.core.validators import RegexValidator,EmailValidator,validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, PermissionsMixin
import re, datetime

class Sucursal(models.Model):
    direccion = models.CharField("Direccion",max_length =100)
    hora_apertura = models.CharField("Hora de apertura",max_length =5)
    provincia = models.CharField("Provincia",max_length =80)
    localidad = models.CharField("Localidad",max_length =80)
    sucursal_central = models.BooleanField(default=False)
    pseudonimo = models.CharField("Pseudonimo", max_length=100, default="")
    gerente = models.ForeignKey('users.Usuario',on_delete=models.DO_NOTHING,related_name="gerente")


    def __str__(self):
        return self.pseudonimo

    def save(self, *args, **kwargs):
        if((self.localidad).lower() in "resistencia"):
            self.pseudonimo = "Sucursal central"
        else:    
            self.pseudonimo = (f'{self.localidad}, {self.provincia}')
        super(Sucursal, self).save(*args, **kwargs)


class UserManager(BaseUserManager):
    
    def _create_user(self,email,nombre,dni,rango,is_staff,is_superuser,password):
        if not email:
            raise ValueError("Debe contener un email")

        user = self.model(
            email = self.normalize_email(email),
            nombre = nombre,
            dni = dni,
            rango = rango,
            is_staff = is_staff,
            is_superuser = is_superuser,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self,email,nombre,dni,rango,password = None):
        return self._create_user(email,nombre,dni,rango,False,False,password)
        
    def create_superuser(self,email,nombre,dni,rango="Admin",password = None):
        return self._create_user(email,nombre,dni,rango,True,True,password)


class Usuario(AbstractBaseUser, PermissionsMixin):
    TIPOS_RANGOS_PARA_ACCESO_TODAS_SUCURSALES = (
        ('Admin', 'Admin'),
        ('Administracion', 'Administracion'), 
        ('Dueños', 'Dueños'), 
    )
    nombre = models.CharField("Nombre Completo",max_length=100)
    sucursales = models.ManyToManyField(Sucursal, related_name='sucursales_usuarios')
    # sucursal = models.ForeignKey(Sucursal, on_delete=models.DO_NOTHING,blank = True, null = True)
    email = models.EmailField("Correo Electrónico",max_length=254, unique=True)
    rango = models.CharField("Rango:",max_length=40)
    dni = models.CharField("DNI",max_length=9, blank = True, null = True)
    tel = models.CharField("Telefono",max_length=11, blank = True, null = True)
    
    c = models.CharField("Contraseña_depuracion:",max_length=250)
    fec_ingreso = models.CharField("Fecha de ingreso", max_length = 10, default ="")
    domic = models.CharField("Domicilio",max_length=200, default="")
    prov = models.CharField("Provincia",max_length=40, default="")
    cp = models.CharField("Codigo postal",max_length=5, default="")
    loc = models.CharField("Localidad",max_length=100, default="")
    lugar_nacimiento = models.CharField("Lugar de nacimiento",max_length=100, default ="")
    fec_nacimiento = models.CharField("Fecha de nacimiento", max_length = 10, default ="")
    estado_civil = models.CharField("Estado civil", max_length =30,default ="")
    xp_laboral = models.TextField("Experiencia laboral", blank=True,null=True, default="")
    datos_familiares = models.JSONField("Datos familiares", default=list,blank=True,null=True)
    vendedores_a_cargo = models.JSONField("Vendedores a cargo", default=list,blank=True,null=True)
    faltas_tardanzas = models.JSONField("Faltas o tardanzas", default=list,blank=True,null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    accesosTodasSucursales = models.BooleanField(default=False)
    objects = UserManager()


    def __str__(self):
        return self.nombre
    

    USERNAME_FIELD ="email"
    REQUIRED_FIELDS= ["nombre","dni"]
    
    def clean(self):
        errors = {}
        validation_methods = [
            self.validation_nombre,
            self.validation_email,
            self.validation_dni,
            self.validation_tel,
            self.validation_fec_ingreso,
            self.validation_fec_nacimiento,
            self.validation_cp,
        ]

        for method in validation_methods:
            try:
                method()
            except ValidationError as e:
                errors.update(e.message_dict)

        if errors:
            raise ValidationError(errors)
        

    #region Clean area de los campos
    def validation_nombre(self):
        if not self.nombre:
            raise ValidationError({'nombre': 'No puede estar vacío.'})
        
        if not re.match(r'^[a-zA-Z\s]*$', self.nombre):
            raise ValidationError({'nombre': 'Solo puede contener letras.'})

    # Validar el cp es decir el codigo postal, solamente puede contener numeros
    def validation_cp(self):

        if len(self.cp) > 5:
            raise ValidationError({'cp': 'Codigo postal invalido.'})

        if not re.match(r'^\d+$', self.cp):
            raise ValidationError({'cp': 'Debe contener solo números.'})

    def validation_email(self):
        try:
           validate_email(self.email)
        except ValidationError: 
            raise ValidationError({'email': 'Email no válido.'}) 
           


    def validation_dni(self):
        
        if len(self.dni) < 8: 
            raise ValidationError({'dni': 'DNI inválido.'})
        
        # Si el dni no es un número lanzar error
        if not re.match(r'^\d+$', self.dni):
            raise ValidationError({'dni': 'Debe contener solo números.'})

    def validation_tel(self):
        if len(self.tel) < 10:
            raise ValidationError({'tel': 'Telefono inválido.'})

        if not re.match(r'^\d+$', self.tel):
            raise ValidationError({'tel': 'Debe contener solo números.'}) 

    def validation_fec_ingreso(self):
        if self.fec_ingreso:
            if self.fec_ingreso and not re.match(r'^\d{2}/\d{2}/\d{4}$', self.fec_ingreso):
                raise ValidationError({'fec_ingreso': 'Debe estar en el formato DD/MM/AAAA.'})
            
            try:
                fec_ingreso = datetime.datetime.strptime(self.fec_ingreso, '%d/%m/%Y')
            except ValueError:
                raise ValidationError({'fec_ingreso': 'Fecha inválida.'})

            fec_ingreso = datetime.datetime.strptime(self.fec_ingreso, '%d/%m/%Y')
            if fec_ingreso > datetime.datetime.now():
                raise ValidationError({'fec_ingreso': 'Fecha inválida.'})
            
            

    def validation_fec_nacimiento(self):
        if self.fec_nacimiento:
            if self.fec_nacimiento and not re.match(r'^\d{2}/\d{2}/\d{4}$', self.fec_nacimiento):
                raise ValidationError({'fec_nacimiento': 'Debe estar en el formato DD/MM/AAAA.'})

            try:
                fec_nacimiento = datetime.datetime.strptime(self.fec_nacimiento, '%d/%m/%Y')
            except ValueError:
                raise ValidationError({'fec_nacimiento': 'Fecha inválida.'})

            fec_nacimiento = datetime.datetime.strptime(self.fec_nacimiento, '%d/%m/%Y')
            if fec_nacimiento > datetime.datetime.now():
                raise ValidationError({'fec_nacimiento': 'Fecha inválida.'})


    # endregion 


class Cliente(models.Model):
    def returNro_Cliente(): 
        
        if not Cliente.objects.last():
            number_client = 1
            last_number_cliente_char = f"cli_{number_client}"
        else:
            last_cliente = Cliente.objects.last()
            number_client = int(last_cliente.nro_cliente.split("_")[1])
            last_number_cliente_char = last_cliente.nro_cliente = f"cli_{number_client + 1}"
        return last_number_cliente_char    
        
    nro_cliente = models.CharField(max_length=15,default=returNro_Cliente)
    nombre = models.CharField(max_length=100)
    dni = models.CharField(max_length=9)
    agencia_registrada = models.CharField(max_length=30,default="")
    domic = models.CharField(max_length=100)
    loc = models.CharField(max_length=40)
    prov = models.CharField(max_length=40)
    cod_postal = models.CharField(max_length=7)
    tel = models.CharField(max_length=11)
    fec_nacimiento = models.CharField(max_length=10, default="")
    estado_civil = models.CharField(max_length=20)
    ocupacion = models.CharField(max_length=50)
    
    def __str__(self):
        return f'{self.nro_cliente}: {self.nombre} - {self.dni}'

    def clean(self):
        errors = {}
        validation_methods = [
            self.clean_nro_cliente,
            self.validation_nombre,
            self.validation_estado_civil,
            self.validation_dni,
            self.validation_tel,
            self.validation_fec_nacimiento,
            self.validation_cod_postal,
        ]

        for method in validation_methods:
            try:
                method()
            except ValidationError as e:
                errors.update(e.message_dict)

        if errors:
            raise ValidationError(errors)
        
    #region Clean area de los campos
    def clean_nro_cliente(self):
        nro_cliente = int(self.nro_cliente.split("_")[1])
        last_cliente = int(Cliente.objects.last().nro_cliente.split("_")[1])
        if(nro_cliente != last_cliente+1):
            raise ValidationError({'nro_cliente': "Número de cliente incorrecto."})
            

    def validation_nombre(self):
        if not self.nombre:
            raise ValidationError({'nombre': 'No puede estar vacío.'})
        
        if not re.match(r'^[a-zA-Z\s]*$', self.nombre):
            raise ValidationError({'nombre': 'Solo puede contener letras.'})


    def validation_estado_civil(self):
        if not re.match(r'^[a-zA-Z\s]*$', self.estado_civil):
            raise ValidationError({'estado_civil': 'Solo puede contener letras.'})
        

    def validation_cod_postal(self):

        if len(self.cod_postal) > 5:
            raise ValidationError({'cod_postal': 'Codigo postal invalido.'})

        if not re.match(r'^\d+$', self.cod_postal):
            raise ValidationError({'cod_postal': 'Debe contener solo números.'})


    def validation_dni(self):
        
        if len(self.dni) < 8: 
            raise ValidationError({'dni': 'DNI inválido.'})

        if not re.match(r'^\d+$', self.dni):
            raise ValidationError({'dni': 'Debe contener solo números.'})
        
        if Usuario.objects.filter(dni=self.dni).exists():
            raise ValidationError({'dni': 'DNI ya registrado.'})


    def validation_tel(self):
        if len(self.tel) < 10:
            raise ValidationError({'tel': 'Telefono inválido.'})

        if not re.match(r'^\d+$', self.tel):
            raise ValidationError({'tel': 'Debe contener solo números.'}) 
            

    def validation_fec_nacimiento(self):
        if self.fec_nacimiento:
            if self.fec_nacimiento and not re.match(r'^\d{2}/\d{2}/\d{4}$', self.fec_nacimiento):
                raise ValidationError({'fec_nacimiento': 'Debe estar en el formato DD/MM/AAAA.'})

            try:
                fec_nacimiento = datetime.datetime.strptime(self.fec_nacimiento, '%d/%m/%Y')
            except ValueError:
                raise ValidationError({'fec_nacimiento': 'Fecha inválida.'})

            fec_nacimiento = datetime.datetime.strptime(self.fec_nacimiento, '%d/%m/%Y')
            if fec_nacimiento > datetime.datetime.now():
                raise ValidationError({'fec_nacimiento': 'Fecha inválida.'})


    # endregion 

    
class Key(models.Model):
    motivo = models.CharField(max_length=20, default="")
    descripcion = models.CharField(max_length=255, default="")
    password = models.IntegerField()

    def __str__(self):
        return f'{self.motivo} - {self.password}'