# Generated by Django 4.2 on 2024-08-05 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0020_alter_ventas_campania'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ventas',
            name='deBaja',
            field=models.JSONField(default={'detalleMotivo': '', 'motivo': '', 'nuevaVentaPK': '', 'observacion': '', 'responsable': '', 'status': False}),
        ),
    ]
