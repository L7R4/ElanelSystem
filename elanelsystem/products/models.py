from django.db import models
from django.forms import ValidationError

class Plan(models.Model):
    # Campo para el valor nominal, lo configuramos como primary key
    valor_nominal = models.PositiveIntegerField(primary_key=True)

    # Campo para la suscripción
    suscripcion = models.PositiveIntegerField(default=0)

    # Campo para la suscripción
    porcentaje = models.PositiveIntegerField(default=0)

    # Campo para la cuota 1
    cuota_1 = models.PositiveIntegerField(default=0)

    # Opciones para el campo tipoDePlan
    TIPO_PLAN_CHOICES = [
        ('Basico', 'Basico'),
        ('Estandar', 'Estandar'),
        ('Premium', 'Premium'),
    ]
    tipodePlan = models.CharField(max_length=8, choices=TIPO_PLAN_CHOICES)

    c30 = models.PositiveIntegerField(default=0)
    c24 = models.PositiveIntegerField(default=0)
    c48 = models.PositiveIntegerField(default=0)
    c60 = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Plan {self.valor_nominal} - {self.tipodePlan}"
    
    
    #region Validaciones
    def clean(self):
        errors = {}
        validation_methods = [
            self.validation_cuota_1,
            self.validation_tipodePlan,
            self.validation_suscripcion,
            self.validation_valor_nominal,
            self.validation_c60,
            self.validation_c48,
            self.validation_c30,
            self.validation_c24,
        ]

        for method in validation_methods:
            try:
                method()
            except ValidationError as e:
                errors.update(e.message_dict)

        if errors:
            raise ValidationError(errors)


    def validation_cuota_1(self):
        if self.cuota_1 <= 0:
            raise ValidationError({'cuota_1': 'Debe contener un valor valido'})
        
    def validation_suscripcion(self):
        if self.suscripcion <= 0:
            raise ValidationError({'suscripcion': 'Debe contener un valor valido'})
        
    def validation_valor_nominal(self):
        if self.valor_nominal <= 0:
            raise ValidationError({'valor_nominal': 'Debe contener un valor valido'})
        
    def validation_c24(self):
        if self.c24 <= 0:
            raise ValidationError({'c24': 'Debe contener un valor valido'})
        
    def validation_c30(self):
        if self.c30 <= 0:
            raise ValidationError({'c30': 'Debe contener un valor valido'})
        
    def validation_c48(self):
        if self.c48 <= 0:
            raise ValidationError({'c48': 'Debe contener un valor valido'})
        
    def validation_c60(self):
        if self.c60 <= 0:
            raise ValidationError({'c60': 'Debe contener un valor valido'})
   

    def validation_tipodePlan(self):
        planes = [t[0] for t in self.TIPO_PLAN_CHOICES]

        if self.tipodePlan not in  planes:
            raise ValidationError({'paquete': 'Tipo de plan incorrecto.'})

        
    

        
    
    #endregion


class Products(models.Model):
    TIPO_PRODUCTO =(
        ("Prestamo","Prestamo"),
        ("Moto","Moto"),
        ("Electrodomestico","Electrodomestico"),
    )

    # PAQUETES = (
    #     ("Basico","Basico"),
    #     ("Estandar","Estandar"),
    #     ("Premium","Premium"),
    # )

    tipo_de_producto = models.CharField(max_length=20,choices=TIPO_PRODUCTO)
    nombre = models.CharField(max_length=100)
    # paquete = models.CharField(max_length=20,choices=PAQUETES)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, related_name="plan_producto", null=True, blank=True)


    #region Validaciones
    def clean(self):
        errors = {}
        validation_methods = [
            self.validation_tipo_de_producto,
            # self.validation_paquete,
        ]

        for method in validation_methods:
            try:
                method()
            except ValidationError as e:
                errors.update(e.message_dict)

        if errors:
            raise ValidationError(errors)


    def validation_tipo_de_producto(self):
        tipos = [t[0] for t in self.TIPO_PRODUCTO]

        if self.tipo_de_producto not in  tipos:
            raise ValidationError({'tipo_de_producto': 'Tipo de producto incorrecto.'})
   
    # def validation_paquete(self):
    #     paquetes = [t[0] for t in self.PAQUETES]

    #     if self.paquete not in  paquetes:
    #         raise ValidationError({'paquete': 'Paquete incorrecto.'})

        
    

        
    
    #endregion
