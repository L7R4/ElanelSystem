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
                ventas_para_actualizar = []

                for venta in Ventas.objects.all():
                    auditoria_to_create.append(
                        Auditoria(
                            venta = venta,
                            version = 1,
                            grade = True,
                        )
                    )
                    venta.is_commissionable = True
                    ventas_para_actualizar.append(venta)


                Auditoria.objects.bulk_create(auditoria_to_create)
                self.stdout.write(self.style.SUCCESS(f"✅ Se crearon {len(auditoria_to_create)} auditorías nuevas"))

                Ventas.objects.bulk_update(ventas_para_actualizar, ["is_commissionable"])
                self.stdout.write(self.style.SUCCESS(f"✅ Se marcaron {len(ventas_para_actualizar)} ventas como commissionable"))

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"❌ Hubo un error al actualizar los valores de auditorias"))
            self.stdout.write(f"❌ Error: {str(e)}")