# Generated by Django 4.2 on 2024-01-26 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0007_alter_ventas_auditoria'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ventas',
            name='auditoria',
            field=models.JSONField(default=list),
        ),
    ]
