from django.db import models
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, PermissionsMixin
import re, datetime
from simple_history.models import HistoricalRecords
from django.db.models.functions import Cast, Substr
from django.db import models, transaction
from django.db.models import IntegerField, Max

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
        return f" {self.id} {self.pseudonimo}"

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
    # email = models.EmailField("Correo Electrónico",max_length=254, unique=True)
    email = models.EmailField("Correo Electrónico",max_length=254, unique=True, default ="", blank=True, null=True)

    rango = models.CharField("Rango:",max_length=40)
    dni = models.CharField("DNI",max_length=12, blank = True, null = True)
    tel = models.CharField("Telefono",max_length=15, blank = True, null = True)
    c = models.CharField("Contraseña_depuracion:",max_length=250)
    fec_ingreso = models.CharField("Fecha de ingreso", max_length = 10, default ="")
    fec_egreso = models.CharField("Fecha de egreso", max_length = 10, default ="", blank=True, null=True)

    domic = models.CharField("Domicilio",max_length=200, default="", blank=True, null=True)
    prov = models.CharField("Provincia",max_length=40, default="", blank=True, null=True)
    cp = models.CharField("Codigo postal",max_length=5, default="", blank=True, null=True)
    loc = models.CharField("Localidad",max_length=100, default="", blank=True, null=True)
    lugar_nacimiento = models.CharField("Lugar de nacimiento",max_length=100, default ="", blank=True, null=True)
    fec_nacimiento = models.CharField("Fecha de nacimiento", max_length = 10, default ="", blank=True, null=True)
    estado_civil = models.CharField("Estado civil", max_length =30,default ="", blank=True, null=True)
    xp_laboral = models.TextField("Experiencia laboral", blank=True,null=True, default="")
    
    premios = models.JSONField("Premios", default=list,blank=True,null=True)

    datos_familiares = models.JSONField("Datos familiares", default=list,blank=True,null=True)
    vendedores_a_cargo = models.JSONField("Vendedores a cargo", default=list,blank=True,null=True) #Este se tiene que eliminar despues
    supervisores_a_cargo = models.ForeignKey('self',on_delete=models.SET_NULL,related_name="supervisor_a_cargo",blank=True,null=True)
    additional_passwords = models.JSONField("Contraseñas adicionales",default=dict,blank=True,null=True)
    history = HistoricalRecords()
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    accesosTodasSucursales = models.BooleanField(default=False)
    generico_user = models.BooleanField(default=False)
    suspendido = models.BooleanField(default=False)
    objects = UserManager()

    class Meta:
        ordering = ['nombre'] 
    
    def __str__(self):
        return self.nombre
    
    # ordenar alfabeticamente los usuarios
    class Meta:
        ordering = ['nombre']
        

    def save(self, *args, **kwargs):

        # Capitalizar campos seleccionados
        nombre_limpio = ' '.join(self.nombre.split()).title()
        self.nombre = nombre_limpio

        if not self.email:
            local_part = self.nombre.replace(' ', '').lower()
            self.email = f"{local_part}@gmail.com"
        else:
            self.email = self.email.lower()

        # self.domic = str(self.domic.capitalize())
        # self.prov = str(self.prov.title())
        # self.loc = str(self.loc.title())
        # self.lugar_nacimiento = str(self.lugar_nacimiento.title())
        # self.estado_civil = str(self.estado_civil.capitalize())
        # self.xp_laboral = str(self.xp_laboral.capitalize())

        # Solo en actualizaciones (no en creación):
        if self.pk:
            # Traigo el estado anterior de la BD
            old = Usuario.objects.get(pk=self.pk)
            # Si cambiaron fec_ingreso:
            if old.fec_ingreso != self.fec_ingreso:
                # Limpio la fecha de egreso y desactivo la suspensión
                self.fec_egreso = ""
                self.suspendido = False
            
            #region Definir el tipo de cambio segun el campo que se modificó
            
            if old.fec_ingreso != self.fec_ingreso:
                self._change_reason = "change_fechas"
            elif old.rango != self.rango:
                self._change_reason = "change_rango"
            elif old.sucursales.all() != self.sucursales.all():
                self._change_reason = "change_sucursal"  
            #endregion


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
            # self.validation_nombre,
            # self.validation_email,
            # self.validation_dni,
            # self.validation_tel,
            # self.validation_fec_ingreso,
            # self.validation_fec_nacimiento,
            # self.validation_cp,
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

class ClienteQuerySet(models.QuerySet):


    def ordered_desc(self):
        return self.annotate(
            nro_cli_num=Cast(Substr('nro_cliente', 5), IntegerField())
        ).order_by('-nro_cli_num', '-nro_cliente')
PAD_WIDTH = 3  # cli_001, cli_002...

class Cliente(models.Model):
    nro_cliente = models.CharField(max_length=15)  # sin default (lo asignamos en save)
    nombre = models.CharField(max_length=100)
    dni = models.CharField(max_length=12, default="")
    agencia_registrada = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name="cliente_sucursal")

    domic = models.CharField(max_length=100, default="", blank=True, null=True)
    loc = models.CharField(max_length=40, default="", blank=True, null=True)
    prov = models.CharField(max_length=40, default="", blank=True, null=True)
    cod_postal = models.CharField(max_length=7, default="", blank=True, null=True)
    tel = models.CharField(max_length=15, default="", blank=True, null=True)
    fec_nacimiento = models.CharField(max_length=10, default="", blank=True, null=True)
    estado_civil = models.CharField(max_length=50, blank=True, null=True)
    ocupacion = models.CharField(max_length=50, blank=True, null=True)

    # Si usás un QuerySet custom:
    # objects = ClienteQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["agencia_registrada", "nro_cliente"],
                name="uniq_nro_cliente_por_agencia",
            ),
        ]

    def __str__(self):
        return f'{self.nro_cliente}: {self.nombre} - {self.dni}'

    # ---------- Núcleo: asignación segura del número por agencia ----------
    @classmethod
    def next_for_agencia(cls, sucursal: Sucursal) -> str:
        """
        Calcula el próximo nro_cliente de la forma cli_### dentro de la agencia dada,
        de forma segura ante concurrencia.
        """
        with transaction.atomic():
            # Tomamos lock sobre la fila de la sucursal para serializar la numeración
            Sucursal.objects.select_for_update().filter(pk=sucursal.pk).exists()

            last_num = (
                cls.objects.filter(agencia_registrada=sucursal)
                .annotate(n=Cast(Substr("nro_cliente", 5), IntegerField()))
                .aggregate(m=Max("n"))["m"] or 0
            )
            return f"cli_{last_num + 1:0{PAD_WIDTH}d}"

    def assign_nro_cliente_if_needed(self):
        if not self.nro_cliente:
            if not self.agencia_registrada_id:
                raise ValidationError({"agencia_registrada": "Debe indicar la agencia registrante."})
            self.nro_cliente = self.next_for_agencia(self.agencia_registrada)

        # Validar formato básico (por si alguien lo tocó manualmente)
        if not re.match(r"^cli_\d+$", self.nro_cliente):
            raise ValidationError({"nro_cliente": "Formato inválido. Debe ser cli_###."})

    # ---------- Save con normalizaciones + asignación de número ----------
    def save(self, *args, **kwargs):
        # Asignar nro si falta
        self.assign_nro_cliente_if_needed()

        # Normalizaciones de texto
        self.nombre = str(self.nombre).title()
        self.domic = str(self.domic).capitalize()
        self.prov = str(self.prov).title()
        self.loc = str(self.loc).title()
        self.estado_civil = str(self.estado_civil).capitalize() if self.estado_civil else None
        self.ocupacion = str(self.ocupacion).capitalize() if self.ocupacion else None

        super().save(*args, **kwargs)

    # ---------- Validaciones ----------
    def clean(self):
        errors = {}
        validation_methods = [
            self.validation_nombre,
            self.validation_estado_civil,
            self.validation_dni,
            self.validation_tel,
            self.validation_cod_postal,
            # self.validation_fec_nacimiento,  # si querés activarla
        ]

        for method in validation_methods:
            try:
                method()
            except ValidationError as e:
                errors.update(e.message_dict)

        if errors:
            raise ValidationError(errors)

    def validation_nombre(self):
        if not self.nombre:
            raise ValidationError({'nombre': 'No puede estar vacío.'})
        patron = r'^[a-zA-ZÁÉÍÓÚáéíóúñÑ\s]*$'
        if not re.match(patron, self.nombre):
            raise ValidationError({'nombre': 'Solo puede contener letras (incluyendo tildes y ñ) y espacios.'})

    def validation_estado_civil(self):
        if self.estado_civil and not re.match(r'^[a-zA-Z\s]*$', self.estado_civil):
            raise ValidationError({'estado_civil': 'Solo puede contener letras.'})

    def validation_cod_postal(self):
        if self.cod_postal:
            if len(self.cod_postal) > 5:
                raise ValidationError({'cod_postal': 'Código postal inválido.'})
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
            raise ValidationError({'tel': 'Teléfono inválido.'})
        if not re.match(r'^\d+$', self.tel):
            raise ValidationError({'tel': 'Debe contener solo números.'})

    def validation_fec_nacimiento(self):
        if self.fec_nacimiento:
            if not re.match(r'^\d{2}/\d{2}/\d{4}$', self.fec_nacimiento):
                raise ValidationError({'fec_nacimiento': 'Debe estar en el formato DD/MM/AAAA.'})
            try:
                fec_nacimiento = datetime.datetime.strptime(self.fec_nacimiento, '%d/%m/%Y')
            except ValueError:
                raise ValidationError({'fec_nacimiento': 'Fecha inválida.'})
            if fec_nacimiento > datetime.datetime.now():
                raise ValidationError({'fec_nacimiento': 'Fecha inválida.'})
            
class Key(models.Model):
    motivo = models.CharField(max_length=20, default="")
    descripcion = models.CharField(max_length=255, default="")
    password = models.IntegerField()

    def __str__(self):
        return f'{self.motivo} - {self.password}'