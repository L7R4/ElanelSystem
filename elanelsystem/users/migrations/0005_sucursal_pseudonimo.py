# Generated by Django 4.2 on 2024-02-28 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_sucursal_sucursal_central'),
    ]

    operations = [
        migrations.AddField(
            model_name='sucursal',
            name='pseudonimo',
            field=models.CharField(default='', max_length=100, verbose_name='Pseudonimo'),
        ),
    ]
