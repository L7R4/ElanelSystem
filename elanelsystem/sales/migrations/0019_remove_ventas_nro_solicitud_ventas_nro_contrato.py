# Generated by Django 4.2 on 2024-08-01 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0018_alter_ventas_cuotas'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ventas',
            name='nro_solicitud',
        ),
        migrations.AddField(
            model_name='ventas',
            name='nro_contrato',
            field=models.CharField(default='', max_length=10, verbose_name='Nro Contrato:'),
        ),
    ]
