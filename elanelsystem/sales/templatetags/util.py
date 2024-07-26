import datetime
from django import template
from django.urls import reverse
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


@register.filter(name='format_dd_mm_yyyy')
def format_dd_mm_yyyy(valor):
    fechaRequest= datetime.datetime.strptime(valor, '%d/%m/%Y %H:%M')
    fechaFormated = fechaRequest.strftime('%d/%m/%Y')

    return fechaFormated


@register.simple_tag
def obtener_ultima_campania():
    # Obtener el número de campaña más alto
    ultima_campania = Ventas.objects.aggregate(Max('campania'))['campania__max']
    if(ultima_campania == None):
        return 0
    else:
        return ultima_campania
    

@register.simple_tag(takes_context=True)
def seccionesPorPermisos(context):
    user = context['request'].user

    secciones = {
        "Resumen": {"permisos": ["sales.my_ver_resumen"], "url": reverse("sales:resumen")},
        "Clientes": {"permisos": ["users.my_ver_clientes"], "url": reverse("users:list_customers")},
        "Caja": {"permisos": ["sales.my_ver_caja"], "url": reverse("sales:caja")},
        "Reportes": {"permisos": ["sales.my_ver_reportes"], "url": reverse("reporteView")},
        "Post Venta": {"permisos": ["sales.my_ver_postventa"], "url": reverse("sales:postVentaList",args=[obtener_ultima_campania()])},
        "Colaboradores": {"permisos": ["users.my_ver_colaboradores"], "url": reverse("users:list_users")},
        "Liquidaciones": {"permisos": ["my_ver_liquidaciones"], "url": reverse("liquidacion:liquidacionesPanel")},
        "Administracion": {"permisos": ["my_ver_administracion"], "url": reverse("users:panelAdmin")},
    }
    secciones_permitidas = {}
    for k, v in secciones.items():
        if v["permisos"][0] in user.get_all_permissions():
            secciones_permitidas[k] = v
            
    return secciones_permitidas