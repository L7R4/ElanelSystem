import datetime
from django.db import migrations

CONFIG_BASE = {
    "faltas_tardanzas": {
        "tardanzas_por_falta": 3,
        "monto_tardanza": 350.00,
        "monto_ausencia": 2000.00,
        "margen_tiempo_minutos": 15,
    },
    "comision_vendedor": {
        "motos_24_30": [[0, 9, 0.0240], [10, 19, 0.0250], [20, 29, 0.0260], [30, None, 0.0270]],
        "solucion_combo_24_30": [[0, 9, 0.0270], [10, 19, 0.0280], [20, 29, 0.0290], [30, None, 0.0310]],
        "cuotas_48_60": [[0, 9, 0.0135], [10, 19, 0.0140], [20, 29, 0.0145], [30, None, 0.0155]],
    },
    "premio_productividad_vendedor": {
        "bandas": [
            [0, 10000000, 0],
            [10000000, 15000000, 50000],
            [15000000, 20000000, 75000],
            [20000000, 25000000, 100000],
            [25000000, 30000000, 125000],
            [30000000, None, 150000],
        ],
    },
    "cuotas_1": {
        "dias_ventana": 15,
        "porcentaje_sobre_cuota2": 0.10,
    },
    "premio_productividad_supervisor": {
        "bandas": [
            [0, 16000000, 0],
            [16000000, 18000000, 0.00020],
            [18000000, 22000000, 0.00030],
            [22000000, 26000000, 0.00050],
            [26000000, 30000000, 0.00070],
            [30000000, None, 0.00100],
        ],
    },
    "asegurado_equipo": {
        "umbral_ventas": 80,
        "monto": 300000,
    },
    "comision_supervisor_equipo": {
        "bandas": [
            [0, 30, 0],
            [30, 40, 0.0027],
            [40, 50, 0.0029],
            [50, 60, 0.0031],
            [60, 70, 0.0033],
            [70, 80, 0.0035],
            [80, 90, 0.0037],
            [90, None, 0.0039],
        ],
    },
    "gerente_sucursal": {
        "umbral_cuotas0_ampliar_rango": 100,
        "cuotas_base": [1, 2, 3, 4],
        "cuotas_ampliadas": [1, 2, 3, 4, 5, 6],
        "premio_cuotas0": {
            "bandas": [
                [0, 100, 0],
                [100, 119, 1000],
                [120, 149, 1200],
                [150, 179, 1500],
                [180, 199, 1800],
                [200, None, 2000],
            ],
        },
        "porcentaje_agencias_8": 0.08,
        "porcentaje_agencias_6": 0.06,
        "porcentaje_subagencias": 0.03,
        "agencias_8_porc": [
            "Corrientes, Corrientes",
            "Concordia, Entre Rios",
            "Resistencia, Chaco",
            "Posadas, Misiones",
            "Santiago Del Estero, Santiago Del Estero",
            "Formosa, Formosa",
            "Saenz Peña, Chaco",
        ],
        "agencias_6_porc": ["Paso De Los Libres, Corrientes", "Goya, Corrientes"],
        "agencias_objs_200_ventas": [
            "Corrientes, Corrientes",
            "Concordia, Entre Rios",
            "Resistencia, Chaco",
            "Posadas, Misiones",
            "Santiago Del Estero, Santiago Del Estero",
            "Formosa, Formosa",
        ],
        "objetivo_ventas_grande": 200,
        "objetivo_ventas_chico": 150,
    },
}


def seed_configuraciones(apps, schema_editor):
    ConfiguracionLiquidacion = apps.get_model("liquidacion", "ConfiguracionLiquidacion")
    # Config inicial — vigente desde Enero 2021
    # El usuario ajustará los valores históricos desde el admin de Django
    ConfiguracionLiquidacion.objects.create(
        vigencia_desde=datetime.date(2021, 1, 1),
        descripcion="Configuración inicial (Enero 2021)",
        parametros=CONFIG_BASE,
    )
    # Config actual — vigente desde Febrero 2026
    ConfiguracionLiquidacion.objects.create(
        vigencia_desde=datetime.date(2026, 2, 1),
        descripcion="Configuración actual (Febrero 2026)",
        parametros=CONFIG_BASE,
    )


def unseed_configuraciones(apps, schema_editor):
    ConfiguracionLiquidacion = apps.get_model("liquidacion", "ConfiguracionLiquidacion")
    ConfiguracionLiquidacion.objects.filter(
        vigencia_desde__in=[datetime.date(2021, 1, 1), datetime.date(2026, 2, 1)]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("liquidacion", "0006_configuracionliquidacion_liquidacion_es_vigente_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_configuraciones, unseed_configuraciones),
    ]
