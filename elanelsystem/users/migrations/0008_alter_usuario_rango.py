# Generated by Django 4.2 on 2023-05-02 01:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_usuario_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='rango',
            field=models.CharField(choices=[('Admin', 'Admin'), ('Gerenete', 'Gerente'), ('Secreteria', 'Secretaria'), ('Vendedor', 'Vendedor'), ('Supervisor', 'Supervisor')], max_length=15, verbose_name='Rango:'),
        ),
    ]
