# Generated by Django 4.2 on 2023-12-28 22:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_usuario_sucursal'),
        ('sales', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ventas',
            name='agencia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='users.sucursal'),
        ),
    ]
