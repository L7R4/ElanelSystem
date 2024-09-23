# Generated by Django 4.2 on 2024-09-22 21:08

from django.db import migrations, models
import sales.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ArqueoCaja',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.CharField(max_length=30, verbose_name='Fecha')),
                ('admin', models.CharField(default='', max_length=70)),
                ('responsable', models.CharField(default='', max_length=70)),
                ('totalPlanilla', models.FloatField(default=0, verbose_name='Total Planilla Efectivo')),
                ('totalSegunDiarioCaja', models.FloatField(default=0, verbose_name='Total segun diario de caja')),
                ('diferencia', models.FloatField(default=0, verbose_name='Diferencia')),
                ('observaciones', models.TextField()),
                ('detalle', models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='CoeficientesListadePrecios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor_nominal', models.IntegerField(verbose_name='Valor Nominal:')),
                ('cuota', models.IntegerField(verbose_name='Cuotas:')),
                ('porcentage', models.FloatField(verbose_name='Porcentage:')),
            ],
        ),
        migrations.CreateModel(
            name='CuentaCobranza',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(max_length=50, verbose_name='Alias:')),
            ],
        ),
        migrations.CreateModel(
            name='MovimientoExterno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipoIdentificacion', models.CharField(blank=True, choices=[('DNI', 'DNI'), ('CUIT', 'CUIT')], max_length=15, null=True, verbose_name='Tipo de identificacion:')),
                ('nroIdentificacion', models.CharField(blank=True, max_length=20, null=True, verbose_name='N° de Identificacion:')),
                ('tipoComprobante', models.CharField(blank=True, choices=[('A', 'A'), ('B', 'B'), ('C', 'C')], max_length=3, null=True, verbose_name='Tipo de comprobante:')),
                ('nroComprobante', models.CharField(blank=True, max_length=40, null=True, verbose_name='Nro de comprobante:')),
                ('denominacion', models.CharField(blank=True, max_length=60, null=True, verbose_name='Denominacion del ente:')),
                ('tipoMoneda', models.CharField(blank=True, choices=[('ARS', 'ARS'), ('USD', 'USD'), ('BRL', 'BRL')], max_length=3, null=True, verbose_name='Tipo de moneda:')),
                ('movimiento', models.CharField(choices=[('Ingreso', 'Ingreso'), ('Egreso', 'Egreso')], max_length=8, verbose_name='Movimiento:')),
                ('dinero', models.FloatField(verbose_name='Dinero:')),
                ('metodoPago', models.CharField(max_length=30, verbose_name='Metodo de pago:')),
                ('ente', models.CharField(max_length=40, verbose_name='Ente:')),
                ('fecha', models.CharField(max_length=16, verbose_name='Fecha:')),
                ('campania', models.IntegerField(default=0, verbose_name='Campaña:')),
                ('concepto', models.CharField(max_length=200, verbose_name='Concepto:')),
                ('premio', models.BooleanField(default=False, verbose_name='Premio:')),
                ('adelanto', models.BooleanField(default=False, verbose_name='Adelanto:')),
            ],
        ),
        migrations.CreateModel(
            name='Ventas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modalidad', models.CharField(choices=[('Diario', 'Diario'), ('Semanal', 'Semanal'), ('Quincenal', 'Quincenal'), ('Mensual', 'Mensual')], default='', max_length=15, verbose_name='Modalidad:')),
                ('nro_cuotas', models.IntegerField()),
                ('nro_operacion', models.IntegerField(default=sales.models.Ventas.returnOperacion)),
                ('campania', models.CharField(default='', max_length=50, verbose_name='Campaña:')),
                ('cambioTitularidadField', models.JSONField(blank=True, default=list, null=True)),
                ('suspendida', models.BooleanField(default=False)),
                ('importe', models.FloatField(default=0, verbose_name='Importe:')),
                ('tasa_interes', models.FloatField(default=0, verbose_name='Tasa de Interes:')),
                ('primer_cuota', models.FloatField(default=0, verbose_name='Primer cuota:')),
                ('anticipo', models.IntegerField(default=0, verbose_name='Cuota de Inscripcion:')),
                ('intereses_generados', models.FloatField(default=0, verbose_name='Intereses Gen:')),
                ('importe_x_cuota', models.FloatField(default=0, verbose_name='Importe x Cuota:')),
                ('total_a_pagar', models.FloatField(default=0, verbose_name='Total a pagar:')),
                ('fecha', models.CharField(default='', max_length=30, verbose_name='Fecha:')),
                ('tipo_producto', models.CharField(default='', max_length=20)),
                ('paquete', models.CharField(default='', max_length=20)),
                ('observaciones', models.CharField(blank=True, max_length=255, null=True, verbose_name='Obeservaciones:')),
                ('auditoria', models.JSONField(default=[{'comentarios': '', 'fecha_hora': '', 'grade': False, 'realizada': False, 'version': 0}])),
                ('adjudicado', models.JSONField(default={'autorizado_por': '', 'contratoAdjudicado': '', 'status': False, 'tipo': ''})),
                ('deBaja', models.JSONField(default={'detalleMotivo': '', 'motivo': '', 'nuevaVentaPK': '', 'observacion': '', 'responsable': '', 'status': False})),
                ('cuotas', models.JSONField(blank=True, default=list, null=True)),
                ('cantidadContratos', models.JSONField(blank=True, default=list, null=True, verbose_name='Chances')),
            ],
        ),
    ]
