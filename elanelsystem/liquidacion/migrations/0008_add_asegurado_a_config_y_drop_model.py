import datetime
from django.db import migrations


ASEGURADO_ACTUAL = {
    "vendedor": 300000,
    "supervisor": 500000,
    "gerente sucursal": 1000000,
}

ASEGURADO_INICIAL = {
    "vendedor": 300000,
    "supervisor": 500000,
    "gerente sucursal": 900000,
}


def add_asegurado_to_configs(apps, schema_editor):
    ConfiguracionLiquidacion = apps.get_model("liquidacion", "ConfiguracionLiquidacion")

    config_inicial = ConfiguracionLiquidacion.objects.filter(
        vigencia_desde=datetime.date(2021, 1, 1)
    ).first()
    if config_inicial:
        config_inicial.parametros["asegurado_por_rol"] = ASEGURADO_INICIAL
        config_inicial.save()

    config_actual = ConfiguracionLiquidacion.objects.filter(
        vigencia_desde=datetime.date(2026, 2, 1)
    ).first()
    if config_actual:
        config_actual.parametros["asegurado_por_rol"] = ASEGURADO_ACTUAL
        config_actual.save()


def remove_asegurado_from_configs(apps, schema_editor):
    ConfiguracionLiquidacion = apps.get_model("liquidacion", "ConfiguracionLiquidacion")
    for cfg in ConfiguracionLiquidacion.objects.all():
        cfg.parametros.pop("asegurado_por_rol", None)
        cfg.save()


class Migration(migrations.Migration):

    dependencies = [
        ("liquidacion", "0007_seed_configuraciones_liquidacion"),
    ]

    operations = [
        migrations.RunPython(add_asegurado_to_configs, remove_asegurado_from_configs),
        migrations.DeleteModel(name="Asegurado"),
    ]
