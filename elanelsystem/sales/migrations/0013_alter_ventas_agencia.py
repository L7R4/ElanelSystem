# Generated by Django 4.2 on 2023-10-30 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0012_remove_ventas_clientes_anteriores'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ventas',
            name='agencia',
            field=models.CharField(default='', max_length=30),
        ),
    ]
