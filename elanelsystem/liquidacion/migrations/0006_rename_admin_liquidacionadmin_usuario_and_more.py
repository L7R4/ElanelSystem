# Generated by Django 4.2 on 2025-02-03 15:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('liquidacion', '0005_alter_liquidacionadmin_campania_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='liquidacionadmin',
            old_name='admin',
            new_name='usuario',
        ),
        migrations.RenameField(
            model_name='liquidaciongerentesucursal',
            old_name='gerente',
            new_name='usuario',
        ),
        migrations.RenameField(
            model_name='liquidacionsupervisor',
            old_name='supervisor',
            new_name='usuario',
        ),
        migrations.RenameField(
            model_name='liquidacionvendedor',
            old_name='vendedor',
            new_name='usuario',
        ),
    ]
