# Generated by Django 4.2 on 2025-03-24 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0006_movimientoexterno_observaciones'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movimientoexterno',
            name='movimiento',
            field=models.CharField(max_length=8, verbose_name='Movimiento:'),
        ),
    ]
