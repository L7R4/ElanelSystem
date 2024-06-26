# Generated by Django 4.2 on 2023-12-28 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('valor_nominal', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('suscripcion', models.PositiveIntegerField(default=0)),
                ('cuota_1', models.PositiveIntegerField(default=0)),
                ('tipodePlan', models.CharField(choices=[('basico', 'Basico'), ('estandar', 'Estandar'), ('premium', 'Premium')], max_length=8)),
                ('c24', models.PositiveIntegerField(default=0)),
                ('c30', models.PositiveIntegerField(default=0)),
                ('c48', models.PositiveIntegerField(default=0)),
                ('c60', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_de_producto', models.CharField(choices=[('Prestamo', 'Prestamo'), ('Moto', 'Moto'), ('Electrodomestico', 'Electrodomestico')], max_length=20)),
                ('nombre', models.CharField(max_length=100)),
                ('paquete', models.CharField(choices=[('Basico', 'Basico'), ('Estandar', 'Estandar'), ('Premium', 'Premium')], max_length=20)),
                ('importe', models.FloatField()),
            ],
        ),
    ]
