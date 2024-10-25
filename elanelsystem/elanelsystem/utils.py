from datetime import datetime
import pandas as pd

# Funcion para manejar valores NaN desde JS
def handle_nan(value):
    # Comprobar si el valor es NaN usando pandas
    return "" if pd.isna(value) else value


# Funcion para formatear la fecha
def format_date(date_value):

    # Si es un Timestamp, formatear con strftime
    if isinstance(date_value, pd.Timestamp):
        return date_value.strftime('%d/%m/%Y')
    
    # Si es una cadena, convertirla a datetime y formatear
    elif isinstance(date_value, str):
        return pd.to_datetime(date_value).strftime('%d/%m/%Y')
    
    else:
        return ""  # En caso de que no sea un tipo soportado