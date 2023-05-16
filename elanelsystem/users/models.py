from django.db import models
from django.dispatch import receiver
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self,email,nombre,rango,password = None):
        if not email:
            raise ValueError("Debe contener un email")

        user = self.model(
            email = self.normalize_email(email),
            nombre = nombre,
            rango = rango,
            # password = password,
            # contraseña = password
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,email,nombre,rango,password):
        user = self.create_user(
            email,
            nombre = nombre,
            rango = rango,
            password=password
        )
        user.usuario_admin = True
        user.save()
        return user

    # def get_by_natural_key(self, email):
    #     return self.get(email=email)


class Usuario(AbstractBaseUser):
    RANGOS = (
        ('Admin', 'Admin'),
        ('Gerenete', 'Gerente'),
        ('Secreteria', 'Secretaria'),
        ('Vendedor', 'Vendedor'),
        ('Supervisor', 'Supervisor'),
    )

    nombre = models.CharField("Nombre Completo",max_length=100)
    email = models.EmailField("Correo Electrónico",max_length=254, unique=True)
    rango = models.CharField("Rango:",max_length=15, choices=RANGOS)
    dni = models.CharField("DNI",max_length=20, blank = True, null = True)
    domic = models.CharField("Domicilio",max_length=200, blank = True, null = True)
    prov = models.CharField("Provincia",max_length=100, blank = True, null = True)
    tel = models.IntegerField("Telefono", blank = True, null = True)
    fec_nacimiento = models.DateField("Fecha de Nacimiento", blank = True, null = True)
    usuario_admin = models.BooleanField(default=True)
    usuario_active = models.BooleanField(default=True)

    objects = UserManager()


    def __str__(self):
        return self.nombre
    
    class Meta:
        permissions = [
            ("puede_ver_algo","Puede ver algo"),
            ("puede_cambiar_algo","Puede cambiar algo"),
            ("puede_borrar_algo","Puede eliminar algo"),
        ]

    USERNAME_FIELD ="email"
    REQUIRED_FIELDS= ["nombre","rango"]
    
    # objects = MyAccountManager()

    def has_perm(self,perm, obj=None):
        return True

    def has_module_perms(self,app_label):
        return True
    
   
    @property
    def is_staff(self):
        return self.usuario_admin
    

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
    dni = models.CharField(max_length=20,validators=[RegexValidator(r'^\d+(\.\d+)?$', 'Ingrese un número válido')])
    domic = models.CharField(max_length=100)
    loc = models.CharField(max_length=40)
    prov = models.CharField(max_length=40, validators=[RegexValidator(r'^[a-zA-ZñÑ ]+$', 'Ingrese solo letras')])
    cod_postal = models.CharField(max_length=4,validators=[RegexValidator(r'^\d+(\.\d+)?$', 'Ingrese un número válido')])
    tel = models.IntegerField(validators=[RegexValidator(r'^\d+(\.\d+)?$', 'Ingrese un número válido')])
    fec_nacimiento = models.CharField(max_length=30, default="")
    estado_civil = models.CharField(max_length=20)
    ocupacion = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.nombre} - {self.dni}'