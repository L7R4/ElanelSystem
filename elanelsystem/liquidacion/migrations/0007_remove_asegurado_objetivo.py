# Generated by Django 4.2 on 2025-02-23 16:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('liquidacion', '0006_rename_admin_liquidacionadmin_usuario_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asegurado',
            name='objetivo',
        ),
    ]
