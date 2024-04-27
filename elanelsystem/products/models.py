from django.db import models

class Products(models.Model):
    TIPO_PRODUCTO =(
        ("Prestamo","Prestamo"),
        ("Moto","Moto"),
        ("Electrodomestico","Electrodomestico"),
    )

    PAQUETES = (
        ("Basico","Basico"),
        ("Estandar","Estandar"),
        ("Premium","Premium"),
    )

    tipo_de_producto = models.CharField(max_length=20,choices=TIPO_PRODUCTO)
    nombre = models.CharField(max_length=100)
    paquete = models.CharField(max_length=20,choices=PAQUETES)
    importe = models.FloatField()

class Plan(models.Model):
    # Campo para el valor nominal, lo configuramos como primary key
    valor_nominal = models.PositiveIntegerField(primary_key=True)

    # Campo para la suscripción
    suscripcion = models.PositiveIntegerField(default=0)

    # Campo para la cuota 1
    cuota_1 = models.PositiveIntegerField(default=0)

    # Opciones para el campo tipoDePlan
    TIPO_PLAN_CHOICES = [
        ('basico', 'Basico'),
        ('estandar', 'Estandar'),
        ('premium', 'Premium'),
    ]
    tipodePlan = models.CharField(max_length=8, choices=TIPO_PLAN_CHOICES)

    c24 = models.PositiveIntegerField(default=0)
    c30 = models.PositiveIntegerField(default=0)
    c48 = models.PositiveIntegerField(default=0)
    c60 = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Plan {self.valor_nominal} - {self.tipodePlan}"
    
