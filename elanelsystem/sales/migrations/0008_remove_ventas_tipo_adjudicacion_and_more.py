# Generated by Django 4.2 on 2023-09-06 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0007_ventas_suspendida'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ventas',
            name='tipo_adjudicacion',
        ),
        migrations.AlterField(
            model_name='ventas',
            name='adjudicado',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='ventas',
            name='deBaja',
            field=models.JSONField(default=dict),
        ),
    ]
