from django.core.management.base import BaseCommand, CommandError
from sales.models import Ventas, Auditoria
from django.db import transaction

class Command(BaseCommand):
    help = "Audita las ventas y asigna el valor 'auditoria' con el valor proporcionado."

    def handle(self, *args, **options):
        # Definimos el valor que queremos asignar a 'auditoria'
        try:
            with transaction.atomic():
            # 1) Eliminar todas las auditorias existentes
                Auditoria.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f"✅ Se eliminaron todas las auditorias existentes"))

                auditoria_to_create = []
                qs = Ventas.objects.all()

                for venta in qs:
                    auditoria_to_create.append(
                        Auditoria(
                            venta = venta,
                            version = 1,
                            realizada = True,
                            grade = True,
                        )
                    )
                Auditoria.objects.bulk_create(auditoria_to_create)


                self.stdout.write(self.style.SUCCESS(f"✅ Todas las ventas seleccionadas han sido actualizadas con el valor 'auditoria'"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"❌ Hubo un error al actualizar los valores de auditorias"))
