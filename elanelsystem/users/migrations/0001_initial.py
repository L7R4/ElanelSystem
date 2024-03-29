# Generated by Django 4.2 on 2023-08-25 21:40

import django.core.validators
from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre Completo')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Correo Electrónico')),
                ('rango', models.CharField(choices=[('Admin', 'Admin'), ('Gerenete', 'Gerente'), ('Secreteria', 'Secretaria'), ('Vendedor', 'Vendedor'), ('Supervisor', 'Supervisor')], max_length=15, verbose_name='Rango:')),
                ('dni', models.CharField(blank=True, max_length=20, null=True, verbose_name='DNI')),
                ('domic', models.CharField(blank=True, max_length=200, null=True, verbose_name='Domicilio')),
                ('prov', models.CharField(blank=True, max_length=100, null=True, verbose_name='Provincia')),
                ('tel', models.IntegerField(blank=True, null=True, verbose_name='Telefono')),
                ('fec_nacimiento', models.DateField(blank=True, null=True, verbose_name='Fecha de Nacimiento')),
                ('usuario_admin', models.BooleanField(default=True)),
                ('usuario_active', models.BooleanField(default=True)),
            ],
            options={
                'permissions': [('puede_ver_algo', 'Puede ver algo'), ('puede_cambiar_algo', 'Puede cambiar algo'), ('puede_borrar_algo', 'Puede eliminar algo')],
            },
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nro_cliente', models.CharField(default=users.models.Cliente.returNro_Cliente, max_length=15)),
                ('nombre', models.CharField(max_length=100, validators=[django.core.validators.RegexValidator('^[a-zA-ZñÑ ]+$', 'Ingrese solo letras')])),
                ('dni', models.CharField(max_length=20, validators=[django.core.validators.RegexValidator('^\\d+(\\.\\d+)?$', 'Ingrese un número válido')])),
                ('domic', models.CharField(max_length=100)),
                ('loc', models.CharField(max_length=40)),
                ('prov', models.CharField(max_length=40, validators=[django.core.validators.RegexValidator('^[a-zA-ZñÑ ]+$', 'Ingrese solo letras')])),
                ('cod_postal', models.CharField(max_length=4, validators=[django.core.validators.RegexValidator('^\\d+(\\.\\d+)?$', 'Ingrese un número válido')])),
                ('tel', models.IntegerField(validators=[django.core.validators.RegexValidator('^\\d+(\\.\\d+)?$', 'Ingrese un número válido')])),
                ('fec_nacimiento', models.CharField(default='', max_length=30)),
                ('estado_civil', models.CharField(max_length=20)),
                ('ocupacion', models.CharField(max_length=50)),
            ],
        ),
    ]
