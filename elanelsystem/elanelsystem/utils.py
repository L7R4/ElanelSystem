from datetime import datetime
import pandas as pd
from sales.models import Ventas

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
    if isinstance(date_value, pd.Timestamp):
        return date_value.strftime('%d/%m/%Y')
    
    # Si es una cadena, convertirla a datetime y formatear
    elif isinstance(date_value, str):
        try:
            return pd.to_datetime(date_value).strftime('%d/%m/%Y')
        except ValueError:
            return ""  # En caso de que la conversión falle, devolver cadena vacía
    
    # En caso de que no sea un tipo soportado, devolver cadena vacía
    return ""


def obtenerCampaña_atraves_fecha(fecha_str):
    # Convertir la cadena de fecha en un objeto datetime
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


def obtener_todos_los_contratos():
    todos_los_contratos = []
    
    ventas = Ventas.objects.all()
    
    # Iterar sobre cada venta y extraer los contratos
    for venta in ventas:
        # Agregar los contratos de esta venta a la lista general
        todos_los_contratos.extend(venta.cantidadContratos)
    
    return todos_los_contratos

