# Generated by Django 4.2 on 2023-05-06 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='tipo_de_producto',
            field=models.CharField(choices=[('Prestamo', 'Prestamo'), ('Moto', 'Moto'), ('Electrodomestico', 'Electrodomestico')], max_length=20),
        ),
    ]
