# Generated by Django 4.2 on 2024-07-31 23:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_remove_plan_c24_remove_plan_c30_remove_plan_c48_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plan',
            name='cuota_1',
        ),
        migrations.RemoveField(
            model_name='plan',
            name='suscripcion',
        ),
    ]
