from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from sales.models import Ventas, Auditoria

class Command(BaseCommand):
    help = "Audita las ventas (todas o de una sucursal) y marca is_commissionable=True."

    def add_arguments(self, parser):
        parser.add_argument(
            'sucursal_id',
            nargs='?',
            type=int,
            default=None,
            help="(Opcional) ID de la sucursal cuyas ventas quieres auditar. Si no se pasa, se auditan todas."
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
            with transaction.atomic():
                # 2) Borrar solo las auditorías de esas ventas
                filtro_aud = {'venta__in': ventas_qs}
                borradas, _ = Auditoria.objects.filter(**filtro_aud).delete()
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Se eliminaron {borradas} auditorías antiguas de {label}."
                ))

                crear = []
                actualizar = []

                # 3) Preparar nuevas auditorías y marcar ventas
                for venta in ventas_qs:
                    crear.append(Auditoria(
                        venta=venta,
                        version=1,
                        grade=True,
                    ))
                    venta.is_commissionable = True
                    actualizar.append(venta)

                # 4) Bulk create y bulk update
                Auditoria.objects.bulk_create(crear)
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Se crearon {len(crear)} nuevas auditorías para {label}."
                ))

                Ventas.objects.bulk_update(actualizar, ['is_commissionable'])
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Se marcaron {len(actualizar)} ventas como comisionables para {label}."
                ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"❌ Error al procesar auditoría para {label}: {e}"
            ))
            raise CommandError("No se completó la auditoría.") 