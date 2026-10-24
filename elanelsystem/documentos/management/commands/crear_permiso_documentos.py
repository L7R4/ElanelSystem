from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from documentos.models import Documento


class Command(BaseCommand):
    help = 'Crea el permiso documentos.my_ver_documentos'

    def handle(self, *args, **options):
        content_type = ContentType.objects.get_for_model(Documento)

        permission, created = Permission.objects.get_or_create(
            codename='my_ver_documentos',
            name='Puede ver documentos',
            content_type=content_type,
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS('Permiso "documentos.my_ver_documentos" creado exitosamente')
            )
        else:
            self.stdout.write(
                self.style.WARNING('El permiso "documentos.my_ver_documentos" ya existe')
            )
