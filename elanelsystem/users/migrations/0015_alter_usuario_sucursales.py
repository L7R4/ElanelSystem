# Generated by Django 4.2 on 2024-07-28 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_alter_sucursal_gerente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='sucursales',
            field=models.ManyToManyField(blank=True, related_name='sucursales_usuarios', to='users.sucursal'),
        ),
    ]