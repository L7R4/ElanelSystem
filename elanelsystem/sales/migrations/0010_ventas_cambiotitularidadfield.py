# Generated by Django 4.2 on 2023-10-09 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0009_ventas_clientes_anteriores'),
    ]

    operations = [
        migrations.AddField(
            model_name='ventas',
            name='cambioTitularidadField',
            field=models.JSONField(default=dict),
        ),
    ]
