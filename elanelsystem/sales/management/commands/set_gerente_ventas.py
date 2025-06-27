from django.core.management.base import BaseCommand, CommandError
from sales.models import Ventas
from users.models import Usuario

class Command(BaseCommand):
    help = (
        "Asigna el campo 'gerente' de todas las Ventas de una sucursal y campaña "
        "al Usuario cuyo DNI sea el pasado como argumento."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'id_sucursal',
            type=int,
            help='ID de la sucursal donde se realizaron las ventas'
        )
        parser.add_argument(
            'dni_gerente',
            type=str,
            help='DNI del gerente a asignar en las ventas'
        )
        parser.add_argument(
            '--campania',
            type=str,
            default=None,
            help='Nombre de la campaña (por ejemplo: "Abril 2025"). Si no se pasa, actualiza todas las campañas.'
        )

    def handle(self, *args, **options):
        id_sucursal = options['id_sucursal']
        dni_gerente = options['dni_gerente']
        campania = options['campania']

        # 1) Intentamos buscar al Usuario con ese DNI
        try:
            usuario_gerente = Usuario.objects.get(dni=dni_gerente)
        except Usuario.DoesNotExist:
            raise CommandError(f"No existe ningún Usuario con DNI = '{dni_gerente}'.") 

        # 2) Filtramos las Ventas según sucursal y (si se pasó) campaña
        if campania:
            ventas_qs = Ventas.objects.filter(
                agencia_id=id_sucursal,
                campania=campania
            )
        else:
            ventas_qs = Ventas.objects.filter(
                agencia_id=id_sucursal
            )

        # 3) Si no hay ventas que coincidan, terminamos
        if not ventas_qs.exists():
            msg = (
                f"No se encontraron Ventas en la sucursal ID={id_sucursal} "
                + (f"y campaña='{campania}'." if campania else "para ninguna campaña.")
            )
            raise CommandError(msg)

        # 4) Actualizamos el campo 'gerente' de todas esas Ventas
        cantidad_actualizadas = ventas_qs.update(gerente=usuario_gerente)

        # 5) Mensaje de éxito
        self.stdout.write(self.style.SUCCESS(
            f"✅ Se actualizaron {cantidad_actualizadas} venta(s) "
            f"asignando como gerente al usuario '{usuario_gerente.nombre}' (DNI: {dni_gerente})."
        ))