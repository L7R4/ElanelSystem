# Generated by Django 4.2 on 2024-01-09 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0005_remove_movimientoexterno_sucursal_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ventas',
            name='auditoria',
            field=models.BooleanField(default=False),
        ),
    ]