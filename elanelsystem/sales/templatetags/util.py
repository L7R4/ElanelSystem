import datetime
from django import template
from django.urls import reverse
from users.models import Usuario
from django.db.models import Max
from sales.models import Ventas
from sales.utils import formatear_moneda_sin_centavos
from elanelsystem.utils import formatear_dd_mm_yyyy
from django.templatetags.static import static

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
    return formatear_dd_mm_yyyy(valor)



@register.filter(name='cuotas_pagadas_len')
def cuotas_pagadas_len(venta):
    return len(venta.cuotas_pagadas())
    

@register.simple_tag(takes_context=True)
def seccionesPorPermisos(context):
    user = context['request'].user
    secciones = {
        # "Resumen": {"permisos": ["sales.my_ver_resumen"], "url": reverse("sales:resumen")},
        "Clientes": {"permisos": ["users.my_ver_clientes"], "url": reverse("users:list_customers"),"image": static("images/icons_sider/clientes.svg")},
        "Caja": {"permisos": ["sales.my_ver_caja"], "url": reverse("sales:caja"),"image": static("images/icons_sider/caja.svg")},
        # "Exportar datos": {"permisos": ["sales.my_ver_reportes"], "url": reverse("detallesNegocio")}, #Mover a a la vista de "Configuracion"
        "Auditorías": {"permisos": ["sales.my_ver_postventa"], "url": reverse("sales:postVentaList"),"image": static("images/icons_sider/auditoria.svg")},
        "Usuarios": {"permisos": ["users.my_ver_colaboradores"], "url": reverse("users:list_users"),"image": static("images/icons_sider/colaboradores.svg")},
        "Liquidaciones": {"permisos": ["my_ver_liquidaciones"], "url": reverse("liquidacion:liquidacionesPanel"),"image": static("images/icons_sider/liquidacion.svg")},
        "Configuración": {"permisos": ["my_ver_administracion"], "url": reverse("users:panelAdmin"),"image": static("images/icons_sider/configuracion.svg")},
    }

    secciones_permitidas = {}
    for k, v in secciones.items():
        if any(user.has_perm(perm) for perm in v['permisos']):
            secciones_permitidas[k] = v
    return secciones_permitidas


@register.simple_tag(takes_context=True)
def iniciales_de_nombre_usuario(context):
    nombre = context['request'].user.nombre
    return ''.join([n[0].upper() for n in nombre.split()][:2])


@register.simple_tag(takes_context=True)
def nombre_completo_usuario(context):
    nombre = context['request'].user.nombre
    return ' '.join([n.capitalize() for n in nombre.split()][:2])


@register.simple_tag(takes_context=True)
def rango_usuario(context):
    rango = context['request'].user.rango
    return rango


@register.filter
def formato_moneda(valor):
    """
    Filtro de template para formatear números en formato moneda.
    """
    return formatear_moneda_sin_centavos(valor)