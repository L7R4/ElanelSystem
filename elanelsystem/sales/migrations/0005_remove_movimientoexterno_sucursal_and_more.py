# Generated by Django 4.2 on 2023-12-28 22:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_usuario_sucursal'),
        ('sales', '0004_remove_arqueocaja_sucursal_arqueocaja_agencia'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movimientoexterno',
            name='sucursal',
        ),
        migrations.AddField(
            model_name='movimientoexterno',
            name='agencia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='users.sucursal'),
        ),
    ]
