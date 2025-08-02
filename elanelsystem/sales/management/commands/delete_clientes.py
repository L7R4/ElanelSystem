from django.core.management.base import BaseCommand, CommandError
from users.models import Cliente

class Command(BaseCommand):
    # help = "Audita las ventas (todas o de una sucursal) y marca is_commissionable=True."

    def add_arguments(self, parser):
        parser.add_argument(
            'sucursal_id',
            nargs='?',
            type=int,
            default=None,
            help="(Opcional) ID de la sucursal coyus clientes quieres elimintar. Si no se pasa, se eliminan todos."
        )

    def handle(self, *args, **options):
        sucursal_id = options['sucursal_id']

        # 1) Construir el queryset de ventas a procesar
        if sucursal_id is not None:
            clientes_qs = Cliente.objects.filter(agencia_registrada=sucursal_id)
            label = f"sucursal {sucursal_id}"
        else:
            clientes_qs = Cliente.objects.all()
            label = "todas las sucursales"

        if not clientes_qs.exists():
            self.stdout.write(self.style.WARNING(
                f"No se encontraron clientes para {label}."
            ))
            return

        try:
            self.stdout.write(self.style.SUCCESS(
                f"✅ Se eliminaron {clientes_qs.count()} clientes de {label}."
            ))
            clientes_qs.delete()

            
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"❌ Error al eliminar las ventas para {label}: {e}"
            ))
            raise CommandError("No se completo la eliminacion de clientes.") 
