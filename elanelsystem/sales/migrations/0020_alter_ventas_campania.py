# Generated by Django 4.2 on 2024-08-03 13:05
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0019_remove_ventas_nro_solicitud_ventas_nro_contrato'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ventas',
            name='campania',
            field=models.CharField(default='', max_length=50, verbose_name='Campaña:'),
        ),
    ]
