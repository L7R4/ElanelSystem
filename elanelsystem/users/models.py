from django.db import models
from django.dispatch import receiver
from django.core.validators import RegexValidator,EmailValidator,validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, PermissionsMixin
import re, datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from elanelsystem.utils import obtenerCampaña_atraves_fecha


class Sucursal(models.Model):
    direccion = models.CharField("Direccion",max_length =100)
    hora_apertura = models.CharField("Hora de apertura",max_length =5)
    provincia = models.CharField("Provincia",max_length =80)
    localidad = models.CharField("Localidad",max_length =80)
    sucursal_central = models.BooleanField(default=False)
    pseudonimo = models.CharField("Pseudonimo", max_length=100, default="")
    gerente = models.ForeignKey('users.Usuario',on_delete=models.SET_NULL,related_name="gerente",blank=True,null=True)
    tel_ref = models.CharField("Telefono de referencia",max_length =15, blank=True, null=True)
    email_ref = models.CharField("Email de referencia",max_length =60, blank=True, null=True)

    def __str__(self):
        return f"{self.pseudonimo}"

    def save(self, *args, **kwargs):
        self.direccion = self.direccion.capitalize()
        self.provincia = self.provincia.title()
        self.localidad = self.localidad.title()
        self.pseudonimo = (f'{self.localidad}, {self.provincia}')
        super(Sucursal, self).save(*args, **kwargs)


    #region Validaciones
    # def clean(self):
    #     errors = {}
    #     validation_methods = [
    #         self.validation_fecha_innaguracion,
    #         # self.validation_campania,
    #     ]

    #     for method in validation_methods:
    #         try:
    #             method()
    #         except ValidationError as e:
    #             errors.update(e.message_dict)

    #     if errors:
    #         raise ValidationError(errors)

    #endregion


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

    nombre = models.CharField("Nombre Completo",max_length=100)
    sucursales = models.ManyToManyField(Sucursal, related_name='sucursales_usuarios',blank=True)
    email = models.EmailField("Correo Electrónico",max_length=254, unique=True)
    rango = models.CharField("Rango:",max_length=40)
    dni = models.CharField("DNI",max_length=12, blank = True, null = True)
    tel = models.CharField("Telefono",max_length=15, blank = True, null = True)
    c = models.CharField("Contraseña_depuracion:",max_length=250)
    fec_ingreso = models.CharField("Fecha de ingreso", max_length = 10, default ="")
    fec_egreso = models.CharField("Fecha de egreso", max_length = 10, default ="", blank=True, null=True)

    domic = models.CharField("Domicilio",max_length=200, default="")
    prov = models.CharField("Provincia",max_length=40, default="")
    cp = models.CharField("Codigo postal",max_length=5, default="")
    loc = models.CharField("Localidad",max_length=100, default="")
    lugar_nacimiento = models.CharField("Lugar de nacimiento",max_length=100, default ="")
    fec_nacimiento = models.CharField("Fecha de nacimiento", max_length = 10, default ="")
    estado_civil = models.CharField("Estado civil", max_length =30,default ="")
    xp_laboral = models.TextField("Experiencia laboral", blank=True,null=True, default="")
    
    premios = models.JSONField("Premios", default=list,blank=True,null=True)

    datos_familiares = models.JSONField("Datos familiares", default=list,blank=True,null=True)
    vendedores_a_cargo = models.JSONField("Vendedores a cargo", default=list,blank=True,null=True)
    additional_passwords = models.JSONField("Contraseñas adicionales",default=dict,blank=True,null=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    accesosTodasSucursales = models.BooleanField(default=False)
    generico_user = models.BooleanField(default=False)
    suspendido = models.BooleanField(default=False)
    objects = UserManager()
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):

        # Capitalizar campos seleccionados
        self.nombre = str(self.nombre.title())
        self.domic = str(self.domic.capitalize())
        self.prov = str(self.prov.title())
        self.loc = str(self.loc.title())
        self.lugar_nacimiento = str(self.lugar_nacimiento.title())
        self.estado_civil = str(self.estado_civil.capitalize())
        self.xp_laboral = str(self.xp_laboral.capitalize())
        self.email = str(self.email.lower())


        super(Usuario, self).save(*args, **kwargs)

    USERNAME_FIELD ="email"
    REQUIRED_FIELDS= ["nombre","dni"]
    
    def setAdditionalPasswords(self):
        permisos = list(self.get_all_permissions())
        permisos = [permiso.split(".")[1] for permiso in permisos]
        
        if('my_anular_cuotas' in permisos):
            self.additional_passwords["anular_cuotas"] = {"password":self.c, "descripcion": "Contraseña para anular cuotas"} #Seteamos por default la contraseña con la de la cuenta incialmente.

        # Agregar mas condicionales si se quiere agregar alguna contraseña adicional . . . . .
        # if('my_anular_cuotas' in permisos):
        #     self.additional_passwords["anular_cuotas"] = self.c



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
        
        patron = r'^[a-zA-ZÁÉÍÓÚáéíóúñÑ\s]*$'
        if not re.match(patron, self.nombre):
            raise ValidationError({'nombre': 'Solo puede contener letras (incluyendo tildes y ñ) y espacios.'})

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


class Ausencia(models.Model):

    def now_formatted():
        return datetime.datetime.now().strftime("%d/%m/%Y %H:%M")


    usuario   = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="ausencias",
        help_text="Usuario al que corresponde esta falta o tardanza"
    )
    fecha_de_carga = models.CharField(max_length = 20, help_text="Día de carga de falta/tardanza", default=now_formatted)
    tipo = models.CharField(max_length=20,choices=[("Falta", "Falta"), ("Tardanza", "Tardanza")])
    motivo = models.TextField(blank=True)
    campania = models.CharField("Campaña",max_length=30,blank=True)
    
    dia = models.CharField(max_length = 10, help_text="Día de falta/tardanza", default="")
    hora = models.CharField(max_length = 5, help_text="Hora de falta/tardanza", default="")

    class Meta:
        ordering = ["-fecha_de_carga"]
        verbose_name = "Ausencia/Tardanza"
        verbose_name_plural = "Ausencias/Tardanzas"

    def save(self, *args, **kwargs):
        # si no vino explícito, lo genero aquí
        if not self.a:
            self.a = obtenerCampaña_atraves_fecha(self.fecha)

    def __str__(self):
        return f"{self.usuario.nombre} – {self.tipo} el {self.fecha}"


class Descuento(models.Model):
    def now_formatted():
        return datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    usuario   = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="descuentos",
        help_text="Usuario al que corresponde este descuento"
    )
    fecha = models.CharField(max_length = 20, help_text="Fecha de aplicación del descuento", default=now_formatted)
    monto = models.IntegerField(default=0, help_text="Monto del descuento")
    concepto = models.CharField(max_length=100, help_text="¿Por qué se aplica?")

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Descuento"
        verbose_name_plural = "Descuentos"

    def __str__(self):
        return f"{self.usuario.nombre} – ${self.monto} ({self.fecha})"


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
    dni = models.CharField(max_length=12,default="")
    # agencia_registrada = models.CharField(max_length=30,default="")
    agencia_registrada = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name="cliente_sucursal")

    domic = models.CharField(max_length=100,default="")
    loc = models.CharField(max_length=40,default="")
    prov = models.CharField(max_length=40,default="")
    cod_postal = models.CharField(max_length=7,default="")
    tel = models.CharField(max_length=15,default="")
    fec_nacimiento = models.CharField(max_length=10, default="",blank=True,null=True)
    estado_civil = models.CharField(max_length=50, blank=True, null=True)
    ocupacion = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f'{self.nro_cliente}: {self.nombre} - {self.dni}'
    
    def save(self, *args, **kwargs):
        # Convertir a string y luego capitalizar los campos que puedan tener valores nulos o numéricos
        self.nombre = str(self.nombre).title()
        self.domic = str(self.domic).capitalize()
        self.prov = str(self.prov).title()
        self.loc = str(self.loc).title()
        self.estado_civil = str(self.estado_civil).capitalize() if self.estado_civil else None
        self.ocupacion = str(self.ocupacion).capitalize() if self.ocupacion else None
        
        super(Cliente, self).save(*args, **kwargs)


    def clean(self):
        errors = {}
        validation_methods = [
            # self.clean_nro_cliente,
            self.validation_nombre,
            self.validation_estado_civil,
            self.validation_dni,
            self.validation_tel,
            # self.validation_fec_nacimiento,
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
        if Cliente.objects.last():
            nro_cliente = int(self.nro_cliente.split("_")[1])
            last_cliente = int(Cliente.objects.last().nro_cliente.split("_")[1])
            if(nro_cliente != last_cliente+1):
                raise ValidationError({'nro_cliente': "Número de cliente incorrecto."})
            

    def validation_nombre(self):
        if not self.nombre:
            raise ValidationError({'nombre': 'No puede estar vacío.'})
        
        patron = r'^[a-zA-ZÁÉÍÓÚáéíóúñÑ\s]*$'
        if not re.match(patron, self.nombre):
            raise ValidationError({'nombre': 'Solo puede contener letras (incluyendo tildes y ñ) y espacios.'})


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
        
        if Cliente.objects.filter(dni=self.dni).exists():
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