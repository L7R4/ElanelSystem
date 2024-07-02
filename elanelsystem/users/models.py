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
    sucursal = models.ForeignKey(Sucursal, on_delete=models.DO_NOTHING,blank = True, null = True)
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
    xp_laboral = models.TextField("Experiencia laboral", default ="Vacio")
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
        self.validation_nombre()
        self.validation_sucursal()
        self.validation_email()
        self.validation_rango()
        self.validation_dni()
        self.validation_tel()
        self.validation_fec_ingreso()
        self.validation_fec_nacimiento()

    #region Clean area de los campos
    def validation_nombre(self):
        if not self.nombre:
            raise ValidationError({'nombre': 'No puede estar vacío.'})
        
        if not re.match(r'^[a-zA-Z\s]*$', self.nombre):
            raise ValidationError({'nombre': 'Solo puede contener letras.'})

    def validation_sucursal(self):
        if not self.sucursal:
            raise ValidationError({'sucursal': 'No puede estar vacio.'})
            
        if not Sucursal.objects.filter(pseudonimo=self.sucursal.pseudonimo).exists():
            raise ValidationError({'sucursal': 'La sucursal no existe.'})

    def validation_email(self):
        try:
           validate_email(self.email)
        except ValidationError: 
            raise ValidationError({'email': 'Email no válido.'})    

    def validation_rango(self):
        if self.rango not in dict(self.TIPOS_RANGOS_PARA_ACCESO_TODAS_SUCURSALES):
            raise ValidationError({'rango': 'Rango no válido.'})

    def validation_dni(self):
        if len(self.dni) < 8: 
            raise ValidationError({'dni': 'DNI inválido.'})

    def validation_tel(self):
        if len(self.tel) < 10:
            raise ValidationError({'tel': 'Telefono inválido.'})

        if not re.match(r'^\d+$', self.tel):
            raise ValidationError({'tel': 'Debe contener solo números.'}) 

    def validation_fec_ingreso(self):
        if self.fec_ingreso and not re.match(r'^\d{2}/\d{2}/\d{4}$', self.fec_ingreso):
            raise ValidationError({'fec_ingreso': 'Debe estar en el formato DD/MM/AAAA.'})
        
        if self.fec_ingreso > datetime.now().strftime('%d/%m/%Y'):
            raise ValidationError({'fec_ingreso': 'Fecha inválida.'})

    def validation_fec_nacimiento(self):
        if self.fec_nacimiento > datetime.now().strftime('%d/%m/%Y'):
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
    nombre = models.CharField(max_length=100,validators=[RegexValidator(r'^[a-zA-ZñÑ ]+$', 'Ingrese solo letras')])
    dni = models.CharField(max_length=9,validators=[RegexValidator(r'^\d+(\.\d+)?$', 'Ingrese un número válido')])
    agencia_registrada = models.CharField(max_length=30,default="")
    domic = models.CharField(max_length=100)
    loc = models.CharField(max_length=40)
    prov = models.CharField(max_length=40, validators=[RegexValidator(r'^[a-zA-ZñÑ ]+$', 'Ingrese solo letras')])
    cod_postal = models.CharField(max_length=7,validators=[RegexValidator(r'^\d+(\.\d+)?$', 'Ingrese un número válido')])
    tel = models.IntegerField(validators=[RegexValidator(r'^\d+(\.\d+)?$', 'Ingrese un número válido')])
    fec_nacimiento = models.CharField(max_length=10, default="")
    estado_civil = models.CharField(max_length=20)
    ocupacion = models.CharField(max_length=50)
    
    def __str__(self):
        return f'{self.nombre} - {self.dni}'

    
class Key(models.Model):
    motivo = models.CharField(max_length=20, default="")
    descripcion = models.CharField(max_length=255, default="")
    password = models.IntegerField()

    def __str__(self):
        return f'{self.motivo} - {self.password}'