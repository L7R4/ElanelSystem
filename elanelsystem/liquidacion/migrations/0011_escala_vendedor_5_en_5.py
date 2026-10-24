import copy
import datetime
from django.db import migrations

VIGENCIA = datetime.date(2026, 9, 1)
DESCRIPCION = "Escala vendedores de 5 en 5 (Septiembre 2026)"

# Mismos porcentajes que antes; los tramos pasan de 10 en 10 a 5 en 5.
COMISION_VENDEDOR = {
    "motos_24_30": [[0, 4, 0.0240], [5, 9, 0.0250], [10, 14, 0.0260], [15, None, 0.0270]],
    "solucion_combo_24_30": [[0, 4, 0.0270], [5, 9, 0.0280], [10, 14, 0.0290], [15, None, 0.0310]],
    "cuotas_48_60": [[0, 4, 0.0135], [5, 9, 0.0140], [10, 14, 0.0145], [15, None, 0.0155]],
}


def crear_config(apps, schema_editor):
    ConfiguracionLiquidacion = apps.get_model("liquidacion", "ConfiguracionLiquidacion")
    # Partimos de la config vigente a esa fecha para conservar el resto de parámetros
    base = (
        ConfiguracionLiquidacion.objects
        .filter(vigencia_desde__lte=VIGENCIA)
        .order_by("-vigencia_desde")
        .first()
    )
    if base is None:
        raise RuntimeError("No hay configuración de liquidación previa para copiar")

    parametros = copy.deepcopy(base.parametros)
    parametros["comision_vendedor"] = COMISION_VENDEDOR

    if base.vigencia_desde == VIGENCIA:
        base.parametros = parametros
        base.descripcion = DESCRIPCION
        base.save()
    else:
        ConfiguracionLiquidacion.objects.create(
            vigencia_desde=VIGENCIA,
            descripcion=DESCRIPCION,
            parametros=parametros,
        )


def borrar_config(apps, schema_editor):
    ConfiguracionLiquidacion = apps.get_model("liquidacion", "ConfiguracionLiquidacion")
    ConfiguracionLiquidacion.objects.filter(vigencia_desde=VIGENCIA, descripcion=DESCRIPCION).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("liquidacion", "0010_ajustecomision_fecha_ajuste"),
    ]

    operations = [
        migrations.RunPython(crear_config, borrar_config),
    ]
