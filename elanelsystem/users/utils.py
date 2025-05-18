from django.template.loader import get_template
from weasyprint import HTML,CSS
import elanelsystem.settings as settings
import os
import pandas as pd
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



def preprocesar_excel_clientes(file_path):
    from sales.utils import reportar_nans

    """
    Lee la pestaña "CLIENTES" del Excel y:
      - Normaliza nombres de columna a snake_case
      - Comprueba que no falten dni o nro
      - Convierte tipos (nro → int, dni → str, etc)
      - Formatea cod_postal y teléfono como cadenas sin decimales
    Devuelve un DataFrame listo para iterar.
    """
    # 1) Lee la hoja
    df = pd.read_excel(file_path, sheet_name="CLIENTES")

    # 2) Renombra columnas
    df.columns = [
        col.strip()
           .lower()
           .replace(" ", "_")
           .replace("-", "_")
           .replace(".", "")
           .replace("/", "_")
        for col in df.columns
    ]

    # 3) Campos que no pueden estar vacíos
    required = ['nro', 'cliente', 'dni']
    errores = reportar_nans(df, required, id_field='nro')
    if errores:
        raise ValueError(f"Errores en CLIENTES antes de conversión:\n{errores}")

    # 4) Convierte tipos básicos
    df['nro'] = df['nro'].astype(str)
    df['cliente'] = df['cliente'].astype(str).str.strip()
    df['dni'] = df['dni'].astype(str).str.strip()

    # 5) Normaliza opcionales numéricos a string limpio
    def clean_num(col):
        return (
            col.fillna("")
               .map(lambda x: str(x) if str(x).strip() not in ["", "nan"] else "")
        )
    if 'cod_pos' in df.columns:
        df['cod_pos'] = clean_num(df['cod_pos'])
    if 'tel_1' in df.columns:
        df['tel_1'] = clean_num(df['tel_1'])

    # 6) Trim de textos adicionales
    for text_col in ('domic', 'loc', 'prov', 'estado_civil', 'ocupacion'):
        if text_col in df.columns:
            df[text_col] = df[text_col].fillna("").astype(str).str.strip()

    return df