# Generated by Django 4.2 on 2023-09-20 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_key'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='key',
            name='user',
        ),
        migrations.AddField(
            model_name='key',
            name='motivo',
            field=models.CharField(default='', max_length=20),
        ),
    ]
