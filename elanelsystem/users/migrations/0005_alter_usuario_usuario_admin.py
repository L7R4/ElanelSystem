# Generated by Django 4.2 on 2023-05-01 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_usuario_rango'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='usuario_admin',
            field=models.BooleanField(default=True),
        ),
    ]
