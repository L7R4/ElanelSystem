from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from .models import Ventas, PagoCannon

@receiver(post_save, sender=Ventas)
def ejecutar_acciones_al_crear_venta(sender, instance, created, **kwargs):
    """
    Esta función se ejecuta cada vez que se guarda un objeto de Ventas.
    Si `created` es True, significa que es una nueva venta.
    """
    if created:
        print("¡Venta creada!", instance)
        instance.testVencimientoCuotas()
        instance.suspenderOperacion()

        # Llama a cualquier función que necesites
        # por ejemplo:
        # enviar_notificacion(instance)
        # generarPDF(instance)
        # loguear_accion(instance)


@receiver(post_save, sender=PagoCannon)
# @receiver(post_delete, sender=PagoCannon)
def _on_pago_cannon_changed(sender, instance, **kwargs):
    print("asddddddddddddddddddd")
    venta = instance.venta
    # sincronizar todas las cuotas de la venta
    venta.sync_estado_cuotas()
    # guardamos sólo el JSON de cuotas y campo suspendida/deBaja
    print("✅ Actualizando cuotas de la venta desde el signal")
    venta.save(update_fields=['cuotas','suspendida','deBaja'])