# Generated by Django 4.2 on 2024-11-06 20:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor_nominal', models.PositiveIntegerField()),
                ('tipodePlan', models.CharField(choices=[('Basico', 'Basico'), ('Estandar', 'Estandar'), ('Premium', 'Premium')], max_length=8)),
                ('suscripcion', models.IntegerField(default=0)),
                ('primer_cuota', models.IntegerField(default=0)),
                ('c24_porcentage', models.FloatField(default=0, verbose_name='Porcentaje de 24 c')),
                ('c30_porcentage', models.FloatField(default=0, verbose_name='Porcentaje de 30 c')),
                ('c48_porcentage', models.FloatField(default=0, verbose_name='Porcentaje de 48 c')),
                ('c60_porcentage', models.FloatField(default=0, verbose_name='Porcentaje de 60 c')),
            ],
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_de_producto', models.CharField(choices=[('Prestamo', 'Prestamo'), ('Moto', 'Moto'), ('Electrodomestico', 'Electrodomestico')], max_length=20)),
                ('nombre', models.CharField(max_length=100)),
                ('plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='plan_producto', to='products.plan')),
            ],
        ),
    ]
