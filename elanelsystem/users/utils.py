from django.template.loader import get_template
from weasyprint import HTML,CSS
import elanelsystem.settings as settings
import os
import pandas as pd
import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.core.exceptions import PermissionDenied
from django.utils import timezone

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

def snapshot_usuario_by_campana(user, campania_str):
    """
    Devuelve (snapshot, dias_trabajados) para un usuario en una campaña dada.

    CONCEPTO: dado el lapso de tiempo que cubre la campaña, se toma el ÚLTIMO
    registro histórico que cayó dentro de ese lapso (o antes de él si no hubo
    cambios durante la campaña). Esto garantiza que siempre se usa el estado
    real del usuario en ese momento, sin importar cuántos cambios haya tenido.

    CORRECCIONES RETROACTIVAS: si fec_ingreso o fec_egreso fueron cargadas en
    el sistema DESPUÉS de que terminó la campaña pero su valor corresponde a una
    fecha dentro del período, se aplican igual (patch en memoria, sin persistir).

    Devuelve (None, 0) si el usuario no participó en la campaña.
    """
    from elanelsystem.utils import obtener_fechas_campania, parse_fecha_to_date

    inicio_camp, fin_camp = obtener_fechas_campania(campania_str)

    # Fin de campaña al final del día para incluir cambios hechos ese mismo día
    fin_dt = datetime.datetime.combine(fin_camp, datetime.time.max)
    if timezone.is_naive(fin_dt):
        fin_dt = timezone.make_aware(fin_dt, timezone.get_current_timezone())

    # Último estado dentro o antes del fin de campaña.
    # Si hubo N cambios en ese lapso, se toma el más reciente.
    h = (
        user.history
        .filter(history_date__lte=fin_dt)
        .order_by("-history_date")
        .first()
    )

    if not h:
        # ── Retroactivo: usuario dado de alta DESPUÉS del cierre de campaña ──
        # Si el usuario fue registrado en el sistema luego de que la campaña
        # terminó (history_date > fin_dt), pero su fec_ingreso cae dentro del
        # período, se toma el registro histórico más reciente como snapshot y
        # se parchea fec_ingreso en memoria (no se persiste).
        if user.fec_ingreso:
            live_ingreso = parse_fecha_to_date(user.fec_ingreso)
            if live_ingreso and live_ingreso <= fin_camp:
                h = user.history.order_by("-history_date").first()
                if not h:
                    return None, 0
                h.fec_ingreso = user.fec_ingreso  # patch en memoria, no se persiste
            else:
                return None, 0
        else:
            return None, 0

    # ── Retroactivo fec_ingreso ───────────────────────────────────────────────
    # Si el ingreso fue corregido después del cierre de la campaña y la nueva
    # fecha cae dentro del período, se aplica la corrección antes de validar
    # la participación (porque afecta si el usuario participa o no).
    if user.fec_ingreso and user.fec_ingreso != h.fec_ingreso:
        live_ingreso = parse_fecha_to_date(user.fec_ingreso)
        if live_ingreso and live_ingreso <= fin_camp:
            h.fec_ingreso = user.fec_ingreso  # patch en memoria, no se persiste

    # Validación de participación: si ingresó después de que terminó la campaña
    fecha_ing = parse_fecha_to_date(h.fec_ingreso)
    if not fecha_ing or fecha_ing > fin_camp:
        return None, 0

    # ── Retroactivo fec_egreso ────────────────────────────────────────────────
    # Si el egreso fue cargado después del cierre de la campaña pero la fecha
    # corresponde a un día dentro del período, se aplica para el cálculo de días.
    if not h.fec_egreso and user.fec_egreso:
        live_egreso = parse_fecha_to_date(user.fec_egreso)
        if live_egreso and live_egreso <= fin_camp:
            h.fec_egreso = user.fec_egreso  # patch en memoria, no se persiste

    days_worked = count_days_worked_by_user(h, campania_str)
    return h, days_worked

def obtener_usuarios_segun_campana(campania_str,sucursal):
    # from elanelsystem.utils import obtener_fechas_campania,parse_fecha_to_date
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


def count_days_worked_by_user(user_last_version, campania_str):
    from elanelsystem.utils import obtener_fechas_campania, parse_fecha_to_date

    inicio_camp, fin_camp = obtener_fechas_campania(campania_str)

    fecha_ingreso = parse_fecha_to_date(user_last_version.fec_ingreso)
    if not fecha_ingreso:
        return 0

    # Si fec_egreso viene vacía / inválida -> sigue activo, se usa hoy como límite
    fecha_egreso = None
    if user_last_version.fec_egreso:
        fecha_egreso = parse_fecha_to_date(user_last_version.fec_egreso)

    if not fecha_egreso:
        import datetime as _dt
        fecha_egreso = _dt.date.today()

    fecha_inicio_real = max(fecha_ingreso, inicio_camp)
    fecha_fin_real = min(fecha_egreso, fin_camp)

    if fecha_inicio_real > fecha_fin_real:
        return 0

    return (fecha_fin_real - fecha_inicio_real).days + 1