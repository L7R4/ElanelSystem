# Generated by Django 4.2 on 2024-04-25 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0011_movimientoexterno_campania'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ventas',
            name='adjudicado',
            field=models.JSONField(default={'status': False, 'tipo': ''}),
        ),
        migrations.AlterField(
            model_name='ventas',
            name='auditoria',
            field=models.JSONField(default=[{'comentarios': '', 'fecha_hora': '', 'grade': False, 'realizada': False, 'version': 0}]),
        ),
        migrations.AlterField(
            model_name='ventas',
            name='deBaja',
            field=models.JSONField(default={'detalleMotivo': '', 'motivo': '', 'observacion': '', 'responsable': '', 'status': False}),
        ),
    ]
