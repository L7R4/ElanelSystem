from django.db import models
from users.models import Cliente,Usuario
from products.models import Products
from django.core.validators import RegexValidator


class CoeficientesListadePrecios(models.Model):
    valor_nominal = models.IntegerField("Valor Nominal:")
    cuota = models.IntegerField("Cuotas:")
    porcentage = models.FloatField("Porcentage:")

class Ventas(models.Model):
    MODALIDADES = (
        ('Semanal', 'Semanal'),
        ('Mensual', 'Mensual'),
        ('Bimestral', 'Bimestral')
    )

    nro_cliente = models.ForeignKey(Cliente,on_delete=models.CASCADE,related_name="ventas_nro_cliente")
    nombre_completo = models.ForeignKey(Cliente,on_delete=models.CASCADE,related_name="ventas_nombre_cliente")
    nro_solicitud = models.CharField("Nro solicitud:",max_length=10,validators=[RegexValidator(r'^\d+(\.\d+)?$', 'Ingrese un número válido')],default="")
    modalidad = models.CharField("Modalidad:",max_length=15, choices=MODALIDADES,default="")
    nro_cuotas = models.CharField("Nro Cuotas:",max_length=3,validators=[RegexValidator(r'^\d+(\.\d+)?$', 'Ingrese un número válido')],default="")
    importe = models.FloatField("Importe:",default=0)
    tasa_interes = models.FloatField("Tasa de Interes:",validators=[RegexValidator(r'^\d+(\.\d+)?$', 'Ingrese un número válido')],default=0)
    intereses_generados = models.FloatField("Intereses Gen:",default=0)
    importe_x_cuota = models.FloatField("Importe x Cuota:",default=0)
    total_a_pagar = models.FloatField("Total a pagar:",default=0)
    fecha = models.CharField("Fecha:", max_length=30,default="")
    tipo_producto = models.CharField(max_length=20,default="")
    producto = models.ForeignKey(Products,on_delete=models.CASCADE,related_name="ventas_producto",default="")
    paquete = models.CharField(max_length=20,default="")
    nro_orden = models.CharField("Nro de Orden:",max_length=10,validators=[RegexValidator(r'^\d+(\.\d+)?$', 'Ingrese un número válido')],default="")
    vendedor = models.ForeignKey(Usuario,on_delete=models.CASCADE,related_name="ventas_ven_usuario",default="")
    supervisor = models.ForeignKey(Usuario,on_delete=models.CASCADE,related_name="venta_super_usuario",default="")
    observaciones = models.CharField("Obeservaciones:",max_length=255,blank=True,null=True)
