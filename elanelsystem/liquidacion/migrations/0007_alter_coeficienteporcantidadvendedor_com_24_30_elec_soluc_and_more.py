# Generated by Django 4.2 on 2024-02-22 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liquidacion', '0006_remove_coeficienteporcantidadsupervisor_cantidad_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coeficienteporcantidadvendedor',
            name='com_24_30_elec_soluc',
            field=models.FloatField(verbose_name='24/30 Cuotas Elec/Soluc'),
        ),
        migrations.AlterField(
            model_name='coeficienteporcantidadvendedor',
            name='com_24_30_motos',
            field=models.FloatField(verbose_name='24/30 Cuotas Motos'),
        ),
        migrations.AlterField(
            model_name='coeficienteporcantidadvendedor',
            name='com_48_60',
            field=models.FloatField(verbose_name='48/60 Cuotas'),
        ),
        migrations.AlterField(
            model_name='coeficienteporproductividadsupervisor',
            name='dinero',
            field=models.FloatField(verbose_name='Dinero'),
        ),
        migrations.AlterField(
            model_name='coeficienteporproductividadvendedor',
            name='dinero',
            field=models.FloatField(verbose_name='Dinero'),
        ),
    ]
