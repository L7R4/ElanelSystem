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
