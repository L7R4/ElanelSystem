# Generated by Django 4.2 on 2024-02-19 19:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_usuario_sucursal'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('liquidacion', '0002_asegurado'),
    ]

    operations = [
        migrations.AddField(
            model_name='liquidacioncompleta',
            name='cant_ventas',
            field=models.IntegerField(default=0, verbose_name='Cantidad de ventas'),
        ),
        migrations.AddField(
            model_name='liquidacioncompleta',
            name='detalle_gerentes',
            field=models.ManyToManyField(blank=True, to='liquidacion.liquidaciongerentesucursal'),
        ),
        migrations.AddField(
            model_name='liquidacioncompleta',
            name='detalle_supervisores',
            field=models.ManyToManyField(blank=True, to='liquidacion.liquidacionsupervisor'),
        ),
        migrations.AddField(
            model_name='liquidacioncompleta',
            name='detalle_vendedores',
            field=models.ManyToManyField(blank=True, to='liquidacion.liquidacionvendedor'),
        ),
        migrations.AddField(
            model_name='liquidacioncompleta',
            name='total_recaudado',
            field=models.FloatField(default=0, verbose_name='Total recaudado'),
        ),
        migrations.AlterField(
            model_name='liquidacioncompleta',
            name='fecha',
            field=models.CharField(max_length=10, verbose_name='Fecha'),
        ),
        migrations.AlterField(
            model_name='liquidacioncompleta',
            name='total_liquidado',
            field=models.FloatField(default=0, verbose_name='Total liquidado'),
        ),
        migrations.CreateModel(
            name='LiquidacionAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campania', models.IntegerField(verbose_name='Campaña')),
                ('total_comisionado_blanco', models.FloatField(verbose_name='Total comisionado blanco')),
                ('total_comisionado_negro', models.FloatField(verbose_name='Total comisionado negro')),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='users.sucursal')),
            ],
        ),
        migrations.AddField(
            model_name='liquidacioncompleta',
            name='detalle_admins',
            field=models.ManyToManyField(blank=True, to='liquidacion.liquidacionadmin'),
        ),
    ]