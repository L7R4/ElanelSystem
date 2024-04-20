import datetime
from django import template
from users.models import Usuario
from django.db.models import Max
from sales.models import Ventas
from sales.utils import obtener_ultima_campania
register = template.Library()

@register.filter
def clear_space(value):
    return str(value).replace(' ', '')


@register.filter(name="postVenta_getLastAuditoria")
def postVenta_getLastAuditoria(value):
    return value[-1]

@register.filter(name='liquidaciones_getVendedorObject')
def getVendedorObject(valor):
    colaborador = Usuario.objects.get(email=valor)
    return colaborador

@register.filter(name='liquidaciones_countFaltas')
def liquidaciones_countFaltas(valor):
    data = valor.faltas_tardanzas
    tardanzas = sum(1 for elemento in data if elemento["hora"] != "---")

    # Cada 3 tardanzas se cuenta 1 falta mas
    faltas = sum(1 for elemento in data if elemento["hora"] == "---") + int(tardanzas/3)
    return faltas

@register.filter(name='liquidaciones_countTardanzas')
def liquidaciones_countTardanzas(valor):
    data = valor.faltas_tardanzas
    tardanzas = sum(1 for elemento in data if elemento["hora"] != "---")
    return tardanzas

@register.filter(name='organizarPorFecha')
def organizarPorFecha(valor):
    for item in valor:
        item['fecha'] = datetime.datetime.strptime(item['fecha'], '%d-%m-%Y')

    # Ordenar la lista de diccionarios por la clave 'fecha' de manera descendente
    json_data_ordenado = sorted(valor, key=lambda x: x['fecha'], reverse=True)

    # Formatear las fechas en el formato original
    for item in json_data_ordenado:
        item['fecha'] = item['fecha'].strftime('%d-%m-%Y')


    return json_data_ordenado

@register.simple_tag
def obtener_ultima_campania():
    # Obtener el número de campaña más alto
    ultima_campania = Ventas.objects.aggregate(Max('campania'))['campania__max']
    if(ultima_campania == None):
        return 0
    else:
        return ultima_campania
    