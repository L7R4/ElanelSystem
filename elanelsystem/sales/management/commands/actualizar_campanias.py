from django.core.management.base import BaseCommand
from users.models import Sucursal
import re, datetime
from dateutil.relativedelta import relativedelta

class Command(BaseCommand):
    help = 'Actualizar campañas de las sucursales'

    def handle(self, *args, **kwargs) :
        surcursales = Sucursal.objects.all()

        for sucursal in surcursales:
            sucursal.calcularCampania()
            sucursal.save()
        
        self.stdout.write(self.style.SUCCESS('Campañas actualizadas con éxito.'))