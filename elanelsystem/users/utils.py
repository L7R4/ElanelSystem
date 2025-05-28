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

def snapshot_usuario_by_campana(user,campania_str):
    from elanelsystem.utils import obtener_fechas_campania,parse_fecha_to_date

    inicio_camp, fin_camp = obtener_fechas_campania(campania_str)

    history_list_by_user = []
    for h in user.history.all():
            fecha_ing = parse_fecha_to_date(h.fec_ingreso)
            if fecha_ing and fecha_ing <= fin_camp:
                history_list_by_user.append(h)

    if not history_list_by_user:
        return None, 0
    elif len(history_list_by_user) == 1 and history_list_by_user[0].history_type == "+": # Si solo hay un ingreso y es de tipo +, quiere decir que desde que se registró no salio
        pass
    elif len(history_list_by_user) > 1:
        history_list_by_user = [h for h in history_list_by_user if h.history_type != "+"]

    history_list_by_user.sort(key=lambda h: parse_fecha_to_date(h.fec_ingreso))

    ultima_version = history_list_by_user[-1]
    days_worked = count_days_worked_by_user(ultima_version, campania_str)
    return ultima_version, days_worked


def obtener_usuarios_segun_campana(campania_str,sucursal):
    from elanelsystem.utils import obtener_fechas_campania,parse_fecha_to_date
    from users.models import Usuario

    colaboradores = (Usuario.objects.filter(
        sucursales__in=[sucursal]
        )).exclude(nombre__startswith="Agencia")
    
    usuarios_activos = []

    for c in colaboradores:
        snapshot_by_user, days_worked = snapshot_usuario_by_campana(c, campania_str)
        if snapshot_by_user and days_worked > 0:
            usuarios_activos.append(c)    


    return usuarios_activos


def count_days_worked_by_user(user_last_version, compania_str):
    from elanelsystem.utils import obtener_fechas_campania,parse_fecha_to_date
    inicio_camp, fin_camp = obtener_fechas_campania(compania_str)
    
    fecha_ingreso = parse_fecha_to_date(user_last_version.fec_ingreso)
    fecha_egreso = parse_fecha_to_date(user_last_version.fec_egreso) if user_last_version.fec_egreso else datetime.datetime.today().date()


    fecha_inicio_real = max(fecha_ingreso, inicio_camp)
    fecha_fin_real = min(fecha_egreso, fin_camp)
    dias_trabajados_campania = 0
    if fecha_inicio_real > fecha_fin_real:
        dias_trabajados_campania = 0
    else:
        dias_trabajados_campania = (fecha_fin_real - fecha_inicio_real).days + 1

    return dias_trabajados_campania