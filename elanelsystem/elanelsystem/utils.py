from datetime import datetime
import re
import pandas as pd
from sales.models import Ventas
import elanelsystem.settings as settings
from django.template.loader import get_template
import os
from django.template.loader import get_template
from weasyprint import HTML,CSS
import numpy as np


def safe_to_int(value):
    """
    Convierte 'value' a int de forma segura, manejando varios tipos:
    - np.float64, np.int64
    - float, int
    - str que contenga un número válido
    - y por defecto, intenta convertir a float primero.
    
    Si no logra convertir, lanza ValueError.
    """
    if value is None:
        raise ValueError("No se puede convertir None a entero.")
    
    # Caso numpy integer (np.int32, np.int64, etc.)
    if isinstance(value, np.integer):
        return int(value)
    
    # Caso numpy float (np.float64, etc.)
    if isinstance(value, np.floating):
        return int(value)
    
    # Caso float, int nativo de Python
    if isinstance(value, (float, int)):
        return int(value)
    
    # Caso string: intentar convertirlo a float y luego int
    if isinstance(value, str):
        # Verificar que sea realmente un número
        try:
            return int(float(value))
        except ValueError:
            raise ValueError(f"No se pudo convertir la cadena '{value}' a entero.")
    
    # Si no entra en ninguno de los casos anteriores, 
    # hacer un intento genérico
    try:
        return int(float(value))
    except Exception as e:
        raise ValueError(f"No se pudo convertir {value} a entero. Error: {e}")

# Funcion para manejar valores NaN desde JS
def handle_nan(value):
    # Comprobar si el valor es NaN usando pandas
    return "" if pd.isna(value) else value


# Función para formatear la fecha
def format_date(date_value):
    # Si el valor es NaT o vacío, devolver una cadena vacía
    if pd.isna(date_value) or date_value == pd.NaT:
        return ""
    
    # Si es un Timestamp, formatear con strftime
    if isinstance(date_value, (pd.Timestamp, datetime)):
        return date_value.strftime('%d/%m/%Y')
    
    # Si es una cadena, convertirla a datetime y formatear
    elif isinstance(date_value, str):
        try:
            print("wepweweas")
            return pd.to_datetime(date_value).strftime('%d/%m/%Y')
        except ValueError:
            return ""  # En caso de que la conversión falle, devolver cadena vacía
    
    # En caso de que no sea un tipo soportado, devolver cadena vacía
    return ""


#funcion para formatear las columnas de los excels
def formatear_columnas(file_path, sheet_name):
    # Leer la hoja del archivo Excel
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    # Renombrar las columnas
    df.columns = [
        col.strip().lower().replace(" ", "_").replace("-", "_").replace(".", "_").replace("/", "_")
        for col in df.columns
    ]
    
    return df


#Funcion para obtener una campaña a traves de la fecha en tipo STR
def obtenerCampaña_atraves_fecha(fecha_str):
    # Convertir la cadena de fecha en un objeto datetime
    # fecha = format_date(fecha_str)
    # if not fecha:
    #     return ""
    print(fecha_str)
    fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
    
    # Diccionario para traducir el número del mes a nombre en español
    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    
    # Obtener el nombre del mes y el año
    nombre_mes = meses[fecha.month]
    año = fecha.year
    
    # Formatear la campaña en el formato "Mes Año"
    nombre_campaña = f"{nombre_mes} {año}"
    return nombre_campaña


# Funcion para obtener todos los contratos existentes en la base de datos
def obtener_todos_los_contratos():
    todos_los_contratos = []
    
    ventas = Ventas.objects.all()
    
    # Iterar sobre cada venta y extraer los contratos
    for venta in ventas:
        # Agregar los contratos de esta venta a la lista general
        todos_los_contratos.extend(venta.cantidadContratos)
    
    return todos_los_contratos


# Funcion para generar PDF
def printPDF(data,url,liquidacionName,htmlPath,cssPath):
    template = get_template(htmlPath)
    context = data
    html_template = template.render(context)
    css_url = os.path.join(settings.BASE_DIR, cssPath)
    # print(f"Base dir: {settings.BASE_DIR}")
    if not os.path.exists(settings.PDF_STORAGE_DIR):
        os.makedirs(settings.PDF_STORAGE_DIR)

    pdf = HTML(string=html_template,base_url=url).write_pdf(
        target=liquidacionName, stylesheets = [CSS(css_url)])

    return pdf


# Funcion para formatear las fechas
def formatear_dd_mm_yyyy(valor):
    # print(valor)
    fechaRequest= datetime.strptime(valor, '%d/%m/%Y %H:%M')
    fechaFormated = fechaRequest.strftime('%d/%m/%Y')
    # print(fechaFormated)
    return fechaFormated


def formatear_dd_mm_yyyy_h_m(valor):
    try:
        # Intenta parsear como solo fecha
        fecha = datetime.strptime(valor, "%d/%m/%Y")
        return fecha.strftime("%d/%m/%Y %H:%M")  # fuerza 00:00
    except ValueError:
        pass  # No es solo fecha, seguimos probando

    try:
        # Intenta parsear como fecha con hora (ya formateado)
        datetime.strptime(valor, "%d/%m/%Y %H:%M")
        return valor  # Ya está bien
    except ValueError:
        pass

    # No es ninguno de los formatos esperados
    return valor  # o lanzá una excepción si preferís


def parse_fecha(fecha_str):
    formatos = ["%d/%m/%Y %H:%M", "%d/%m/%Y"]  # Formatos posibles
    for formato in formatos:
        try:
            return datetime.strptime(fecha_str, formato)
        except ValueError:
            continue
    raise ValueError(f"Formato de fecha no válido: {fecha_str}")


def formatar_fecha(value, with_time = False):
    """
    Normaliza cualquier fecha (“value”) a cadena en formato:
      - '%d/%m/%Y'            si with_time=False
      - '%d/%m/%Y 00:00'      si with_time=True

    Acepta:
      • strings en cualquiera de estos formatos:
        - 'DD/MM/YYYY', 'YYYY/MM/DD'
        - 'DD-MM-YYYY', 'YYYY-MM-DD'
        - incluso con hora: 'YYYY-MM-DD HH:MM', etc.
      • pandas.Timestamp o datetime.datetime
      • NaN, None, ''  → devuelve ''

    Ejemplos:
      formatar_fecha('2025-3-5')             → '05/03/2025'
      formatar_fecha('2025-03-25', True)     → '25/03/2025 00:00'
      formatar_fecha(pd.NaT)                 → ''
      formatar_fecha(datetime.now())         → '23/04/2025'
    """
    # 1) Manejo de valores nulos
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    # 2) Si ya es Timestamp o datetime, lo tomamos directamente
    if isinstance(value, (pd.Timestamp, datetime)):
        dt = value.to_pydatetime() if hasattr(value, "to_pydatetime") else value
    else:
        # 3) Si es string, intentamos reconocerlo con pandas (flexible)
        s = str(value).strip()
        if not s:
            return ""
        # Quitar posibles sub-segundos o zona
        # pd.to_datetime infiere la mayoría de formatos conocidos
        dayfirst = bool(re.match(r'\d{1,2}/\d{1,2}/\d{4}', s))
        dt = pd.to_datetime(s, dayfirst=dayfirst, errors='coerce')
        if pd.isna(dt):
            # Fallback manual con patrones concretos
            patrones = [
                "%d/%m/%Y", "%Y/%m/%d",
                "%d-%m-%Y", "%Y-%m-%d",
                "%d/%m/%Y %H:%M", "%Y/%m/%d %H:%M",
                "%d-%m-%Y %H:%M", "%Y-%m-%d %H:%M",
            ]
            for fmt in patrones:
                try:
                    dt = datetime.strptime(s, fmt)
                    break
                except ValueError:
                    dt = None
            if dt is None:
                return ""
    # 4) Formatear según el flag
    if with_time:
        return dt.strftime("%d/%m/%Y 00:00")
    else:
        return dt.strftime("%d/%m/%Y")