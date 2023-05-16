# Generated by Django 4.2 on 2023-05-07 19:06

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0002_alter_products_tipo_de_producto'),
        ('sales', '0007_ventas_nombre_completo'),
    ]

    operations = [
        migrations.AddField(
            model_name='ventas',
            name='fecha',
            field=models.CharField(default='', max_length=30, verbose_name='Fecha:'),
        ),
        migrations.AddField(
            model_name='ventas',
            name='importe',
            field=models.FloatField(default=0, verbose_name='Importe:'),
        ),
        migrations.AddField(
            model_name='ventas',
            name='importe_x_cuota',
            field=models.FloatField(default=0, verbose_name='Importe x Cuota:'),
        ),
        migrations.AddField(
            model_name='ventas',
            name='intereses_generados',
            field=models.FloatField(default=0, verbose_name='Intereses Gen:'),
        ),
        migrations.AddField(
            model_name='ventas',
            name='modalidad',
            field=models.CharField(choices=[('Semanal', 'Semanal'), ('Mensual', 'Mensual'), ('Bimestral', 'Bimestral')], default='', max_length=15, verbose_name='Modalidad:'),
        ),
        migrations.AddField(
            model_name='ventas',
            name='nro_cuotas',
            field=models.CharField(default='', max_length=3, validators=[django.core.validators.RegexValidator('^\\d+(\\.\\d+)?$', 'Ingrese un número válido')], verbose_name='Nro Cuotas:'),
        ),
        migrations.AddField(
            model_name='ventas',
            name='nro_orden',
            field=models.CharField(default='', max_length=10, validators=[django.core.validators.RegexValidator('^\\d+(\\.\\d+)?$', 'Ingrese un número válido')], verbose_name='Nro de Orden:'),
        ),
        migrations.AddField(
            model_name='ventas',
            name='nro_solicitud',
            field=models.CharField(default='', max_length=10, validators=[django.core.validators.RegexValidator('^\\d+(\\.\\d+)?$', 'Ingrese un número válido')], verbose_name='Nro solicitud:'),
        ),
        migrations.AddField(
            model_name='ventas',
            name='observaciones',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Obeservaciones:'),
        ),
        migrations.AddField(
            model_name='ventas',
            name='paquete',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='ventas',
            name='producto',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='ventas_producto', to='products.products'),
        ),
        migrations.AddField(
            model_name='ventas',
            name='supervisor',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='venta_super_usuario', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ventas',
            name='tasa_interes',
            field=models.FloatField(default=0, validators=[django.core.validators.RegexValidator('^\\d+(\\.\\d+)?$', 'Ingrese un número válido')], verbose_name='Tasa de Interes:'),
        ),
        migrations.AddField(
            model_name='ventas',
            name='tipo_producto',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='ventas',
            name='total_a_pagar',
            field=models.FloatField(default=0, verbose_name='Total a pagar:'),
        ),
        migrations.AddField(
            model_name='ventas',
            name='vendedor',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='ventas_ven_usuario', to=settings.AUTH_USER_MODEL),
        ),
    ]
