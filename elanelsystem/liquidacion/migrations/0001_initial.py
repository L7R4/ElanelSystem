# Generated by Django 4.2 on 2024-09-22 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asegurado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dinero', models.IntegerField(verbose_name='Dinero')),
                ('dirigido', models.CharField(max_length=80, verbose_name='Dirigido')),
                ('objetivo', models.IntegerField(default=0, verbose_name='Objetivo')),
            ],
        ),
        migrations.CreateModel(
            name='CoeficientePorCantidadSupervisor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_minima', models.IntegerField(default=0, verbose_name='Cantidad minima')),
                ('cantidad_maxima', models.IntegerField(default=0, verbose_name='Cantidad maxima')),
                ('coeficiente', models.FloatField(verbose_name='Coeficiente')),
            ],
        ),
        migrations.CreateModel(
            name='CoeficientePorCantidadVendedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_minima', models.IntegerField(default=0, verbose_name='Cantidad minima')),
                ('cantidad_maxima', models.IntegerField(default=0, verbose_name='Cantidad maxima')),
                ('com_48_60', models.FloatField(verbose_name='48/60 Cuotas')),
                ('com_24_30_motos', models.FloatField(verbose_name='24/30 Cuotas Motos')),
                ('com_24_30_elec_soluc', models.FloatField(verbose_name='24/30 Cuotas Elec/Soluc')),
            ],
        ),
        migrations.CreateModel(
            name='CoeficientePorProductividadSupervisor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dinero', models.FloatField(verbose_name='Dinero')),
                ('coeficiente', models.FloatField(verbose_name='Coeficiente')),
            ],
        ),
        migrations.CreateModel(
            name='CoeficientePorProductividadVendedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dinero', models.FloatField(verbose_name='Dinero')),
                ('premio', models.FloatField(verbose_name='Premio')),
            ],
        ),
        migrations.CreateModel(
            name='LiquidacionAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campania', models.IntegerField(verbose_name='Campaña')),
                ('total_comisionado_blanco', models.FloatField(verbose_name='Total comisionado blanco')),
                ('total_comisionado_negro', models.FloatField(verbose_name='Total comisionado negro')),
            ],
        ),
        migrations.CreateModel(
            name='LiquidacionCompleta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.CharField(max_length=10, verbose_name='Fecha')),
                ('camapania', models.IntegerField(verbose_name='Camapaña')),
                ('total_recaudado', models.FloatField(default=0, verbose_name='Total recaudado')),
                ('total_liquidado', models.FloatField(default=0, verbose_name='Total liquidado')),
                ('cant_ventas', models.IntegerField(default=0, verbose_name='Cantidad de ventas')),
            ],
        ),
        migrations.CreateModel(
            name='LiquidacionGerenteSucursal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campania', models.IntegerField(verbose_name='Campaña')),
                ('total_comisionado', models.FloatField(verbose_name='Total comisionado')),
                ('detalle', models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='LiquidacionSupervisor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campania', models.IntegerField(verbose_name='Campaña')),
                ('cant_ventas', models.IntegerField(verbose_name='Cantidad de ventas')),
                ('productividad', models.FloatField(default=0, verbose_name='Productividad')),
                ('total_comisionado', models.FloatField(verbose_name='Total comisionado')),
                ('detalle', models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='LiquidacionVendedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campania', models.IntegerField(verbose_name='Campaña')),
                ('cant_ventas', models.IntegerField(verbose_name='Cantidad de ventas')),
                ('productividad', models.FloatField(verbose_name='Productividad')),
                ('total_comisionado', models.FloatField(verbose_name='Total comisionado')),
                ('detalle', models.JSONField(default=dict)),
            ],
        ),
    ]
