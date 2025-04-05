from django.core.management.base import BaseCommand, CommandError
from sales.models import Ventas

class Command(BaseCommand):
    help = "Audita las ventas y asigna el valor 'auditoria' con el valor proporcionado."

    def handle(self, *args, **options):
        # Definimos el valor que queremos asignar a 'auditoria'
        try: 
            nuevo_valor = [{
                "grade": True,
                "realizada": True,
                "comentarios": "Todo ok",
                "fecha_hora": "04/04/2025",
                "version": 1
            }]

            # Actualizamos TODAS las ventas, asignando 'auditoria' con ese valor
            # Ventas.objects.filter(campania="Marzo 2025").update(auditoria=nuevo_valor)
            Ventas.objects.update(auditoria=nuevo_valor)
            self.stdout.write(self.style.SUCCESS(f"Todas las ventas seleccionadas han sido actualizadas con el valor 'auditoria'"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Hubo un error al actualizar los valores de auditorias"))
