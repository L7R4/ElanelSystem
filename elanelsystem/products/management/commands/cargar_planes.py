from django.core.management.base import BaseCommand, CommandError
from products.models import Plan

lista_1 = planes = [
    {"valor_nominal": 150000, "sus_y_cta_1": 7000, "24": 6300, "30": 5100, "48": 3400, "60": 2700, "categoria": "BASE"},
    {"valor_nominal": 200000, "sus_y_cta_1": 9000, "24": 8400, "30": 6800, "48": 4500, "60": 3600, "categoria": "BASE"},
    {"valor_nominal": 250000, "sus_y_cta_1": 11000, "24": 10500, "30": 8500, "48": 5600, "60": 4500, "categoria": "BASE"},
    {"valor_nominal": 300000, "sus_y_cta_1": 13000, "24": 12400, "30": 10200, "48": 6800, "60": 5400, "categoria": "BASE"},
    {"valor_nominal": 350000, "sus_y_cta_1": 15000, "24": 14600, "30": 11900, "48": 7900, "60": 6300, "categoria": "BASE"},
    {"valor_nominal": 400000, "sus_y_cta_1": 17000, "24": 16700, "30": 13700, "48": 9100, "60": 7200, "categoria": "BASE"},
    {"valor_nominal": 450000, "sus_y_cta_1": 19000, "24": 18800, "30": 15500, "48": 10200, "60": 8100, "categoria": "ESTANDAR"},
    {"valor_nominal": 500000, "sus_y_cta_1": 22000, "24": 20900, "30": 17000, "48": 11400, "60": 9000, "categoria": "ESTANDAR"},
    {"valor_nominal": 550000, "sus_y_cta_1": 24000, "24": 23000, "30": 18800, "48": 12500, "60": 9900, "categoria": "ESTANDAR"},
    {"valor_nominal": 600000, "sus_y_cta_1": 26000, "24": 25000, "30": 20400, "48": 13500, "60": 10800, "categoria": "ESTANDAR"},
    {"valor_nominal": 650000, "sus_y_cta_1": 29000, "24": 27100, "30": 22100, "48": 14600, "60": 11800, "categoria": "ESTANDAR"},
    {"valor_nominal": 700000, "sus_y_cta_1": 31000, "24": 29200, "30": 23800, "48": 15700, "60": 12600, "categoria": "ESTANDAR"},
    {"valor_nominal": 750000, "sus_y_cta_1": 33000, "24": 31300, "30": 25400, "48": 16900, "60": 13500, "categoria": "PREMIUM"},
    {"valor_nominal": 800000, "sus_y_cta_1": 35000, "24": 33400, "30": 27100, "48": 18000, "60": 14400, "categoria": "PREMIUM"},
    {"valor_nominal": 850000, "sus_y_cta_1": 37000, "24": 35500, "30": 28800, "48": 19100, "60": 15300, "categoria": "PREMIUM"},
    {"valor_nominal": 900000, "sus_y_cta_1": 39000, "24": 37500, "30": 30400, "48": 20200, "60": 16200, "categoria": "PREMIUM"},
    {"valor_nominal": 950000, "sus_y_cta_1": 41000, "24": 39600, "30": 32100, "48": 21300, "60": 17100, "categoria": "PREMIUM"},
    {"valor_nominal": 1000000, "sus_y_cta_1": 43000, "24": 41700, "30": 33800, "48": 22400, "60": 18000, "categoria": "PREMIUM"},
]


lista_2 = coeficientes = [
    {"valor_nominal": 150000, "c24": 0.008, "c30": 0.02, "c48": 0.088, "c60": 0.08},
    {"valor_nominal": 200000, "c24": 0.008, "c30": 0.02, "c48": 0.08, "c60": 0.08},
    {"valor_nominal": 250000, "c24": 0.008, "c30": 0.02, "c48": 0.0752, "c60": 0.08},
    {"valor_nominal": 300000, "c24": -0.008, "c30": 0.02, "c48": 0.088, "c60": 0.08},
    {"valor_nominal": 350000, "c24": 0.00114, "c30": 0.02, "c48": 0.0835, "c60": 0.08},
    {"valor_nominal": 400000, "c24": 0.002, "c30": 0.0275, "c48": 0.088, "c60": 0.08},
    {"valor_nominal": 450000, "c24": 0.00266, "c30": 0.0333, "c48": 0.092, "c60": 0.08},
    {"valor_nominal": 500000, "c24": 0.0032, "c30": 0.0333, "c48": 0.088, "c60": 0.08},
    {"valor_nominal": 550000, "c24": 0.00323, "c30": 0.033, "c48": 0.0944, "c60": 0.08},
    {"valor_nominal": 600000, "c24": 0.00363, "c30": 0.0255, "c48": 0.0909, "c60": 0.08},
    {"valor_nominal": 650000, "c24": 0.00061, "c30": 0.02, "c48": 0.0781, "c60": 0.08},
    {"valor_nominal": 700000, "c24": 0.00114, "c30": 0.02, "c48": 0.07657, "c60": 0.0892},
    {"valor_nominal": 750000, "c24": 0.0048, "c30": 0.016, "c48": 0.0816, "c60": 0.08},
    {"valor_nominal": 800000, "c24": 0.002, "c30": 0.01625, "c48": 0.08, "c60": 0.08},
    {"valor_nominal": 850000, "c24": 0.00235, "c30": 0.01647, "c48": 0.0786, "c60": 0.08},
    {"valor_nominal": 900000, "c24": 0.0, "c30": 0.0133, "c48": 0.0773, "c60": 0.08},
    {"valor_nominal": 950000, "c24": 0.00042, "c30": 0.01368, "c48": 0.07622, "c60": 0.08},
    {"valor_nominal": 1000000, "c24": 0.0008, "c30": 0.014, "c48": 0.0752, "c60": 0.08}
]

class Command(BaseCommand):
    help = "Carga o actualiza planes en la BD combinando datos de LISTA_1 y LISTA_2."

    def handle(self, *args, **options):
        # 1) Convertimos LISTA_2 en un dict rápido por valor_nominal
        coef_dict = { item["valor_nominal"]: item for item in lista_2 }

        # 2) Recorremos LISTA_1
        for p1 in lista_1:
            val_nom = p1["valor_nominal"]
            p2 = coef_dict.get(val_nom)
            if not p2:
                self.stdout.write(self.style.WARNING(f"No encontrado en LISTA_2 valor_nominal={val_nom}; se omite."))
                continue
            
            # tipo de plan en capitalizado
            tipo_de_plan = p1["categoria"].capitalize()  # "Base", "Estandar", "Premium"
            
            # Determinar c24_porcentage, etc.
            c24 = p2["c24"]
            c30 = p2["c30"]
            c48 = p2["c48"]
            c60 = p2["c60"]

            # 3) Crear o actualizar la instancia
            # como Plan usa "valor_nominal" como pk, 
            # si ya existe => update; si no => create
            plan, created = Plan.objects.update_or_create(
                valor_nominal=val_nom,
                defaults={
                    "tipodePlan": tipo_de_plan,
                    "suscripcion": p1["sus_y_cta_1"],
                    "primer_cuota": p1["sus_y_cta_1"],
                    "c24_porcentage": c24,
                    "c30_porcentage": c30,
                    "c48_porcentage": c48,
                    "c60_porcentage": c60
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Plan creado => {plan.valor_nominal} - {plan.tipodePlan}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Plan actualizado => {plan.valor_nominal} - {plan.tipodePlan}"))