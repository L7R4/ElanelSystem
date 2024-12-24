from django.db import models
from django.forms import ValidationError

class Plan(models.Model):
    # Campo para el valor nominal, lo configuramos como primary key
    valor_nominal = models.PositiveIntegerField()

    # Opciones para el campo tipoDePlan
    TIPO_PLAN_CHOICES = [
        ('Basico', 'Basico'),
        ('Estandar', 'Estandar'),
        ('Premium', 'Premium'),
    ]
    tipodePlan = models.CharField(max_length=8, choices=TIPO_PLAN_CHOICES)
    suscripcion = models.IntegerField(default=0)
    primer_cuota = models.IntegerField(default=0)

    c24_porcentage = models.FloatField("Porcentaje de 24 c",default=0)
    c30_porcentage = models.FloatField("Porcentaje de 30 c",default=0)
    c48_porcentage = models.FloatField("Porcentaje de 48 c",default=0)
    c60_porcentage = models.FloatField("Porcentaje de 60 c",default=0)
    
    def __str__(self):
        return f"Plan {self.valor_nominal} - {self.tipodePlan}"
    
    
    #region Validaciones
    def clean(self):
        errors = {}
        validation_methods = [
            self.validation_tipodePlan,
            self.validation_valor_nominal,
            self.validation_c24_porcentage,
            self.validation_c30_porcentage,
            self.validation_c48_porcentage,
            self.validation_c60_porcentage,
        ]

        for method in validation_methods:
            try:
                method()
            except ValidationError as e:
                errors.update(e.message_dict)

        if errors:
            raise ValidationError(errors)



        
    def validation_valor_nominal(self):
        if self.valor_nominal <= 0:
            raise ValidationError({'valor_nominal': 'Debe contener un valor valido'})
        
    def validation_c24_porcentage(self):
        if self.c24_porcentage <= 0:
            raise ValidationError({'c24_porcentage': 'Debe contener un valor valido'})
        
        
    def validation_c30_porcentage(self):
        if self.c30_porcentage <= 0:
            raise ValidationError({'c30_porcentage': 'Debe contener un valor valido'})
        
    def validation_c48_porcentage(self):
        if self.c48_porcentage <= 0:
            raise ValidationError({'c48_porcentage': 'Debe contener un valor valido'})
        
    def validation_c60_porcentage(self):
        if self.c60_porcentage <= 0:
            raise ValidationError({'c60_porcentage': 'Debe contener un valor valido'})
   

    def validation_tipodePlan(self):
        planes = [t[0] for t in self.TIPO_PLAN_CHOICES]

        if self.tipodePlan not in  planes:
            raise ValidationError({'paquete': 'Tipo de plan incorrecto.'})
        
    def validation_valor_nominal(self):
        if Plan.objects.filter(valor_nominal=self.valor_nominal).exists():
            raise ValidationError({'valor_nominal': 'Este valor nominal ya esta registrado'})

        
    

        
    
    #endregion


class Products(models.Model):
    TIPO_PRODUCTO =(
        ("Solucion","Solucion"),
        ("Moto","Moto"),
        ("Combo","Combo"),
        ("Default","Default")
    )

    # precio = models.PositiveIntegerField(default=0)
    tipo_de_producto = models.CharField(max_length=20,choices=TIPO_PRODUCTO)
    nombre = models.CharField(max_length=100)
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
