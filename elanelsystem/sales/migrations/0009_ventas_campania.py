# Generated by Django 4.2 on 2024-02-06 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0008_alter_ventas_auditoria'),
    ]

    operations = [
        migrations.AddField(
            model_name='ventas',
            name='campania',
            field=models.IntegerField(default=0),
        ),
    ]