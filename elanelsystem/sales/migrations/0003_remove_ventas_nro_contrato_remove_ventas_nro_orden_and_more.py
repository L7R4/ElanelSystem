# Generated by Django 4.2 on 2024-08-23 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ventas',
            name='nro_contrato',
        ),
        migrations.RemoveField(
            model_name='ventas',
            name='nro_orden',
        ),
        migrations.AddField(
            model_name='ventas',
            name='cantidadContratos',
            field=models.JSONField(blank=True, default=list, null=True, verbose_name='Chances'),
        ),
    ]
