# Generated by Django 4.2 on 2024-02-19 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liquidacion', '0003_liquidacioncompleta_cant_ventas_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='asegurado',
            name='objetivo',
            field=models.IntegerField(default=0, verbose_name='Objetivo'),
        ),
    ]
