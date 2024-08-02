# Generated by Django 4.2 on 2024-07-31 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_remove_products_paquete'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plan',
            name='c24',
        ),
        migrations.RemoveField(
            model_name='plan',
            name='c30',
        ),
        migrations.RemoveField(
            model_name='plan',
            name='c48',
        ),
        migrations.RemoveField(
            model_name='plan',
            name='c60',
        ),
        migrations.AddField(
            model_name='plan',
            name='c24_porcentage',
            field=models.PositiveIntegerField(default=0, verbose_name='Porcentaje de 30 c'),
        ),
        migrations.AddField(
            model_name='plan',
            name='c30_porcentage',
            field=models.PositiveIntegerField(default=0, verbose_name='Porcentaje de 24 c'),
        ),
        migrations.AddField(
            model_name='plan',
            name='c48_porcentage',
            field=models.PositiveIntegerField(default=0, verbose_name='Porcentaje de 48 c'),
        ),
        migrations.AddField(
            model_name='plan',
            name='c60_porcentage',
            field=models.PositiveIntegerField(default=0, verbose_name='Porcentaje de 60 c'),
        ),
    ]