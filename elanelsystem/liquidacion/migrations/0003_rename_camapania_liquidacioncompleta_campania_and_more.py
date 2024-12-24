# Generated by Django 4.2 on 2024-11-14 13:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('liquidacion', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='liquidacioncompleta',
            old_name='camapania',
            new_name='campania',
        ),
        migrations.AddField(
            model_name='liquidacioncompleta',
            name='sucursal',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, related_name='liquidacion_sucursal', to='users.sucursal'),
            preserve_default=False,
        ),
    ]