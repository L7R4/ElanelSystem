# Generated by Django 4.2 on 2025-04-08 14:10

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
            ],
        ),
        migrations.CreateModel(
            name='LiquidacionAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campania', models.CharField(max_length=50, verbose_name='Campaña')),
                ('total_comisionado_blanco', models.FloatField(verbose_name='Total comisionado blanco')),
                ('total_comisionado_negro', models.FloatField(verbose_name='Total comisionado negro')),
            ],
        ),
        migrations.CreateModel(
            name='LiquidacionCompleta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.CharField(max_length=10, verbose_name='Fecha')),
                ('campania', models.CharField(max_length=50, verbose_name='Campaña')),
                ('total_recaudado', models.FloatField(default=0, verbose_name='Total recaudado')),
                ('total_proyectado', models.FloatField(default=0, verbose_name='Total proyectado')),
                ('total_liquidado', models.FloatField(default=0, verbose_name='Total liquidado')),
                ('cant_ventas', models.IntegerField(default=0, verbose_name='Cantidad de ventas')),
            ],
        ),
        migrations.CreateModel(
            name='LiquidacionGerenteSucursal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campania', models.CharField(max_length=50, verbose_name='Campaña')),
                ('total_comisionado', models.FloatField(verbose_name='Total comisionado')),
                ('detalle', models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='LiquidacionSupervisor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campania', models.CharField(max_length=50, verbose_name='Campaña')),
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
                ('campania', models.CharField(max_length=50, verbose_name='Campaña')),
                ('cant_ventas', models.IntegerField(verbose_name='Cantidad de ventas')),
                ('productividad', models.FloatField(verbose_name='Productividad')),
                ('total_comisionado', models.FloatField(verbose_name='Total comisionado')),
                ('detalle', models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='MontoTardanzaAusencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto_tardanza', models.DecimalField(decimal_places=2, default=350.0, max_digits=6)),
                ('monto_ausencia', models.DecimalField(decimal_places=2, default=2000.0, max_digits=6)),
                ('margen_tiempo', models.IntegerField(default=15)),
            ],
        ),
    ]
