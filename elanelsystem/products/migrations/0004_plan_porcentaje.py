# Generated by Django 4.2 on 2024-07-31 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_remove_products_paquete'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='porcentaje',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
