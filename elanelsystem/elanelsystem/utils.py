from datetime import datetime
import pandas as pd

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
