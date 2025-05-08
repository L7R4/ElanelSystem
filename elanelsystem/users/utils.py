from django.template.loader import get_template
from weasyprint import HTML,CSS
import elanelsystem.settings as settings
import os
import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.core.exceptions import PermissionDenied

def printPDFNewUSer(data,url,productoName):
    template = get_template("pdfCreateUser.html")
    context = data
    html_template = template.render(context)
    css_url = os.path.join(settings.BASE_DIR, "static/css/pdfCreateUser.css")
    if not os.path.exists(settings.PDF_STORAGE_DIR):
        os.makedirs(settings.PDF_STORAGE_DIR)
    pdf = HTML(string=html_template,base_url=url).write_pdf(target=productoName, stylesheets = [CSS(css_url)])
    # print(pdf)
    return pdf

def get_vendedores_a_cargo(supervisor, campania, sucursal):

    from sales.models import Ventas
    from users.models import Usuario

    """
    Devuelve un queryset de Usuarios (vendedores) que:
      - Tienen ventas en la campaña y sucursal dadas
      - Fueron supervisados por el usuario dado

    Lanza PermissionDenied si el usuario no es un supervisor.
    """
    if supervisor.rango.lower() != 'supervisor':
        raise PermissionDenied("El usuario no tiene rol de supervisor.")

   # 1) Partimos de Ventas filtrando por campaña, sucursal y supervisor
    vendedor_ids = (
        Ventas.objects
        .filter(
            campania=campania,
            agencia=sucursal,
            supervisor=supervisor
        )
        .values_list('vendedor', flat=True)
        .distinct()
    )

    # 2) Recuperamos sólo email y nombre de esos usuarios
    qs = Usuario.objects.filter(id__in=vendedor_ids)

    # 3) Devolvemos la lista de dicts
    return list(qs.values('email', 'nombre'))