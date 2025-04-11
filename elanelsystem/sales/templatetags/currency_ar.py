from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter
def currency_ar(value):
    """
    Convierte un número (ej: 1234567) a string con separador de miles 
    en formato Argentina, anteponiendo '$ '.
    Por ejemplo: 1234567 => '$ 1.234.567'.
    Si el valor no es convertible a entero, lo retorna tal cual.
    """
    try:
        valor_int = int(value)  # asegúrate de que sea int (o redondeo).
    except (ValueError, TypeError):
        # Si no se puede convertir, regreso el valor original:
        return value

    # Usa intcomma => "1,234,567"
    s = intcomma(valor_int)
    # Reemplaza comas con puntos => "1.234.567"
    s = s.replace(",", ".")
    # Anteponemos "$ "
    return f"$ {s}"