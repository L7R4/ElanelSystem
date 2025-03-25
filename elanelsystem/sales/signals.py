from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Ventas

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