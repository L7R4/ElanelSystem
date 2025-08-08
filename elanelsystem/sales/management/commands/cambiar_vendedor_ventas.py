from django.core.management.base import BaseCommand, CommandError
from sales.models import Ventas  
from users.models import Usuario

class Command(BaseCommand):
    help = 'Reemplaza al vendedor de todas las ventas con el DNI viejo por uno nuevo'

    def add_arguments(self, parser):
        parser.add_argument('dni_viejo', type=str, help='DNI del vendedor original')
        parser.add_argument('dni_nuevo', type=str, help='DNI del nuevo vendedor')

    def handle(self, *args, **options):
        dni_viejo = options['dni_viejo']
        dni_nuevo = options['dni_nuevo']

        try:
            vendedor_viejo = Usuario.objects.get(dni=dni_viejo)
        except Usuario.DoesNotExist:
            raise CommandError(f"No se encontró un usuario con DNI {dni_viejo}")

        try:
            vendedor_nuevo = Usuario.objects.get(dni=dni_nuevo)
        except Usuario.DoesNotExist:
            raise CommandError(f"No se encontró un usuario con DNI {dni_nuevo}")

        ventas_actualizadas = Ventas.objects.filter(supervisor=vendedor_viejo).update(supervisor=vendedor_nuevo)
        self.stdout.write(self.style.SUCCESS(f"✅ {ventas_actualizadas} venta(s) actualizadas del vendedor {dni_viejo} al vendedor {dni_nuevo}"))
