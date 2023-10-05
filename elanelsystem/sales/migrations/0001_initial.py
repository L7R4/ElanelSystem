# Generated by Django 4.2 on 2023-08-25 21:40

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoeficientesListadePrecios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor_nominal', models.IntegerField(verbose_name='Valor Nominal:')),
                ('cuota', models.IntegerField(verbose_name='Cuotas:')),
                ('porcentage', models.FloatField(verbose_name='Porcentage:')),
            ],
        ),
        migrations.CreateModel(
            name='Ventas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nro_solicitud', models.CharField(default='', max_length=10, validators=[django.core.validators.RegexValidator('^\\d+(\\.\\d+)?$', 'Ingrese un número válido')], verbose_name='Nro solicitud:')),
                ('modalidad', models.CharField(choices=[('Diario', 'Diario'), ('Semanal', 'Semanal'), ('Quincenal', 'Quincenal'), ('Mensual', 'Mensual')], default='', max_length=15, verbose_name='Modalidad:')),
                ('nro_cuotas', models.IntegerField()),
                ('adjudicado', models.BooleanField(default=False)),
                ('tipo_adjudicacion', models.CharField(choices=[('Sorteo', 'Sorteo'), ('Negociacion', 'Negociacion')], default='Ninguno', max_length=15)),
                ('agencia', models.CharField(choices=[('Agencia Chaco', 'Agencia Chaco'), ('Agencia Corrientes', 'Agencia Corrientes'), ('Agencia Misiones', 'Agencia Misiones')], default='', max_length=20)),
                ('importe', models.FloatField(default=0, verbose_name='Importe:')),
                ('tasa_interes', models.FloatField(default=0, validators=[django.core.validators.RegexValidator('^\\d+(\\.\\d+)?$', 'Ingrese un número válido')], verbose_name='Tasa de Interes:')),
                ('primer_cuota', models.FloatField(default=0, verbose_name='Primer cuota:')),
                ('anticipo', models.FloatField(default=0, verbose_name='Cuota de Inscripcion:')),
                ('intereses_generados', models.FloatField(default=0, verbose_name='Intereses Gen:')),
                ('importe_x_cuota', models.FloatField(default=0, verbose_name='Importe x Cuota:')),
                ('total_a_pagar', models.FloatField(default=0, verbose_name='Total a pagar:')),
                ('fecha', models.CharField(default='', max_length=30, verbose_name='Fecha:')),
                ('tipo_producto', models.CharField(default='', max_length=20)),
                ('paquete', models.CharField(default='', max_length=20)),
                ('nro_orden', models.CharField(default='', max_length=10, validators=[django.core.validators.RegexValidator('^\\d+(\\.\\d+)?$', 'Ingrese un número válido')], verbose_name='Nro de Orden:')),
                ('observaciones', models.CharField(blank=True, max_length=255, null=True, verbose_name='Obeservaciones:')),
                ('cuotas', models.JSONField(default=list)),
                ('nro_cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ventas_nro_cliente', to='users.cliente')),
                ('producto', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='ventas_producto', to='products.products')),
                ('supervisor', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='venta_super_usuario', to=settings.AUTH_USER_MODEL)),
                ('vendedor', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='ventas_ven_usuario', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
