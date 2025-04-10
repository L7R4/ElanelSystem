from django.core.management.base import BaseCommand
from django.db.models import F
from users.models import Usuario  # Ajusta a donde tengas tu modelo Usuario
from sales.models import Ventas  # Ajusta a donde tengas tu modelo Ventas

class Command(BaseCommand):
    help = "Reemplaza el vendedor 'Agencia Concordia' por 'Galeano Axel Rodrigo' en las Ventas."

    def handle(self, *args, **options):
        """
        1) Busca el Usuario con nombre='Agencia Concordia'
        2) Busca el Usuario con nombre='Galeano Axel Rodrigo'
        3) Actualiza todas las ventas para que, si su vendedor es 'Agencia Concordia',
           ahora sea 'Galeano Axel Rodrigo'
        """
        # 1) Usuario actual 'Agencia Concordia'
        try:
            old_vendor = Usuario.objects.get(nombre="Agencia Concordia")
        except Usuario.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("No existe un usuario con nombre='Agencia Concordia'.")
            )
            return

        # 2) Usuario nuevo 'Galeano Axel Rodrigo'
        try:
            new_vendor = Usuario.objects.get(nombre="Galeano Axel Rodrigo")
        except Usuario.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("No existe un usuario con nombre='Galeano Axel Rodrigo'.")
            )
            return

        # 3) Actualizar las ventas
        ventas_to_update = Ventas.objects.filter(vendedor=old_vendor)
        count = ventas_to_update.count()

        ventas_to_update.update(vendedor=new_vendor)
        self.stdout.write(self.style.SUCCESS(
            f"Se actualizaron {count} ventas: de 'Agencia Concordia' a 'Galeano Axel Rodrigo'."
        ))