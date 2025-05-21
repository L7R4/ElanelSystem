from django.core.management.base import BaseCommand, CommandError
from sales.models import Ventas

class Command(BaseCommand):
    # help = "Audita las ventas (todas o de una sucursal) y marca is_commissionable=True."

    def add_arguments(self, parser):
        parser.add_argument(
            'sucursal_id',
            nargs='?',
            type=int,
            default=None,
            help="(Opcional) ID de la sucursal cuyas ventas quieres elimintar. Si no se pasa, se eliminan todas."
        )

    def handle(self, *args, **options):
        sucursal_id = options['sucursal_id']

        # 1) Construir el queryset de ventas a procesar
        if sucursal_id is not None:
            ventas_qs = Ventas.objects.filter(agencia_id=sucursal_id)
            label = f"sucursal {sucursal_id}"
        else:
            ventas_qs = Ventas.objects.all()
            label = "todas las sucursales"

        if not ventas_qs.exists():
            self.stdout.write(self.style.WARNING(
                f"No se encontraron ventas para {label}."
            ))
            return

        try:
            self.stdout.write(self.style.SUCCESS(
                f"✅ Se eliminaron {ventas_qs.count()} ventas de {label}."
            ))
            ventas_qs.delete()

            
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"❌ Error al eliminar las ventas para {label}: {e}"
            ))
            raise CommandError("No se completo la eliminacion de las ventas.") 