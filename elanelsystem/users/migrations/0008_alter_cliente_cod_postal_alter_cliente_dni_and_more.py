# Generated by Django 4.2 on 2024-06-30 02:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_key_descripcion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='cod_postal',
            field=models.CharField(max_length=7, validators=[django.core.validators.RegexValidator('^\\d+(\\.\\d+)?$', 'Ingrese un número válido')]),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='dni',
            field=models.CharField(max_length=9, validators=[django.core.validators.RegexValidator('^\\d+(\\.\\d+)?$', 'Ingrese un número válido')]),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='fec_nacimiento',
            field=models.CharField(default='', max_length=10),
        ),
    ]
