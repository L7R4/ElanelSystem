from django.core.management.base import BaseCommand
from users.models import Usuario
from datetime import date

class Command(BaseCommand):
    help = "Rellena el campo 'fec_ingreso' con una fecha por defecto a todos los usuarios que lo tienen vacío."

    def handle(self, *args, **options):
        fecha_por_defecto = "01/01/2022"

        usuarios_a_actualizar = Usuario.objects.filter(fec_ingreso="")
        cantidad = usuarios_a_actualizar.count()

        if cantidad == 0:
            self.stdout.write(self.style.SUCCESS("Todos los usuarios ya tienen 'fec_ingreso'."))
            return

        usuarios_a_actualizar.update(fec_ingreso=fecha_por_defecto)

        self.stdout.write(self.style.SUCCESS(
            f"Se actualizó 'fec_ingreso' a {cantidad} usuarios con la fecha {fecha_por_defecto}."
        ))