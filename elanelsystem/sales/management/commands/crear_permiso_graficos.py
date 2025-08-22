from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from sales.models import Ventas

class Command(BaseCommand):
    help = 'Crea el permiso sales.my_ver_graficos'

    def handle(self, *args, **options):
        # Obtener el content type para el modelo Ventas
        content_type = ContentType.objects.get_for_model(Ventas)
        
        # Crear el permiso
        permission, created = Permission.objects.get_or_create(
            codename='my_ver_graficos',
            name='Puede ver gráficos',
            content_type=content_type,
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Permiso "sales.my_ver_graficos" creado exitosamente')
            )
        else:
            self.stdout.write(
                self.style.WARNING('El permiso "sales.my_ver_graficos" ya existe')
            ) 