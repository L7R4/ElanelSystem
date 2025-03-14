from django.template.loader import get_template
from weasyprint import HTML,CSS
import elanelsystem.settings as settings
import os
import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.db.models import Max
import openpyxl
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from django.http import HttpResponse, JsonResponse
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from users.models import Cliente
from django.templatetags.static import static

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags

#region Funciones para exportar PDFs
def printPDFBaja(data,url,productoName):
    template = get_template("pdfForBaja.html")
    html_template = template.render(data)
    css_url = os.path.join(settings.BASE_DIR, "static/css/pdfForBaja.css")
    if not os.path.exists(settings.PDF_STORAGE_DIR):
        os.makedirs(settings.PDF_STORAGE_DIR)
    HTML(string=html_template,base_url=url).write_pdf(target=productoName, stylesheets = [CSS(css_url)])
    

def printPDFtitularidad(data,url,productoName):
    template = get_template("pdfForTitu.html")
    context = data
    html_template = template.render(context)
    css_url = os.path.join(settings.BASE_DIR, "static/css/pdfForTitu.css")
    if not os.path.exists(settings.PDF_STORAGE_DIR):
        os.makedirs(settings.PDF_STORAGE_DIR)
    pdf = HTML(string=html_template,base_url=url).write_pdf(target=productoName, stylesheets = [CSS(css_url)])
    # print(pdf)
    return pdf

def printPDFarqueo(data,url,productoName):
    template = get_template("pdfForArqueo.html")
    context = data
    html_template = template.render(context)
    css_url = os.path.join(settings.BASE_DIR, "static/css/pdfArqueo.css")
    if not os.path.exists(settings.PDF_STORAGE_DIR):
        os.makedirs(settings.PDF_STORAGE_DIR)
    pdf = HTML(string=html_template,base_url=url).write_pdf(target=productoName, stylesheets = [CSS(css_url)])
    # print(pdf)
    return pdf

def printPDFinforme(data,url,productoName):
    template = get_template("pdfForInforme.html")
    context = data
    html_template = template.render(context)
    css_url = os.path.join(settings.BASE_DIR, "static/css/pdfInforme.css")
    if not os.path.exists(settings.PDF_STORAGE_DIR):
        os.makedirs(settings.PDF_STORAGE_DIR)
    pdf = HTML(string=html_template,base_url=url).write_pdf(target=productoName, stylesheets = [CSS(css_url)])
    # print(pdf)
    return pdf

def printPDFinformePostVenta(data,url,productoName):
    template = get_template("pdfPostVentaInforme.html")
    context = data
    html_template = template.render(context)
    css_url = os.path.join(settings.BASE_DIR, "static/css/pdfPostVentaInforme.css")
    if not os.path.exists(settings.PDF_STORAGE_DIR):
        os.makedirs(settings.PDF_STORAGE_DIR)
    pdf = HTML(string=html_template,base_url=url).write_pdf(target=productoName, stylesheets = [CSS(css_url)])
    # print(pdf)
    return pdf


def sendEmailPDF(email,pdf_path,sujeto):
        try:
            subject = sujeto
            from_email =  settings.EMAIL_HOST_USER
            to_email = [email]

            email = EmailMultiAlternatives(subject, '', from_email, to_email)
            email.attach_alternative("Se adjunta el PDF.", "text/plain")
            
            # Adjuntar el PDF al correo electrónico
            email.attach_file(pdf_path)

            # Enviar el correo electrónico
            email.send()
            response_data = {'success': True}
            print("weps se envio")
        except Exception as e:
            response_data = {'success': False, 'error_message': str(e)}
            print(e)

        return response_data
#endregion ---------------------------------------------


#region Funciones para exportar .XLSs
def exportar_excel(data):
    information = data["data"]
    tipo_information = data["tipo"]
    fecha = datetime.datetime.now().strftime("%d-%m-%Y %H-%M")

    # Crear un nuevo libro de trabajo
    wb = Workbook()

    # Seleccionar la primera hoja (automáticamente creada)
    ws = wb.active
    ws.title = "Datos"

    # Estilo para los encabezados
    bold_font = Font(color="FFFFFF", size=13, name="Berlin Sans FB")  # Letra blanca, más grande, y fuente específica
    yellow_fill = PatternFill(start_color="1753ED", end_color="1753ED", fill_type="solid")
    center_alignment = Alignment(horizontal='center')
    thin_border = Border(
        left=Side(border_style="thin"),
        right=Side(border_style="thin"),
        top=Side(border_style="thin"),
        bottom=Side(border_style="thin")
    )

    # Insertar imagen antes de la fila 1
    image_path = os.path.join(settings.BASE_DIR, "static/images/logoElanelPDF.png")
    img = Image(image_path)  # Cargar la imagen desde la ruta proporcionada
    img.width, img.height = 830, 90  # Ajustar tamaño de la imagen
    ws.add_image(img, "A1")  # Insertar imagen en la celda A1

    # Espaciar la primera fila para la imagen
    ws.row_dimensions[1].height = 130

    # Iniciar los encabezados en la fila 3
    if information:
        encabezados = [v['verbose_name'] for v in information[0].values()]
        ws.append([])  # Fila vacía para mantener la separación
        ws.append(encabezados)  # Agregar encabezados en la fila 3

        # Aplicar estilos a los encabezados (fila 3)
        for cell in ws[2]:
            cell.font = bold_font
            cell.fill = yellow_fill
            cell.alignment = center_alignment
            cell.border = thin_border

        # Agregar datos de cada diccionario a partir de la fila 4
        for item in information:
            fila = [v['data'] for v in item.values()]
            ws.append(fila)

        # Establecer la fuente general para todo el Excel
        berlin_font = Font(name="Berlin Sans FB")
        for row in ws.iter_rows(min_row=3):  # Desde la fila 4
            for cell in row:
                cell.font = berlin_font

    # Ajustar el ancho de las columnas basado en los encabezados (fila 3)
    for idx, cell in enumerate(ws[3], start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(idx)].width = len(str(cell.value) if cell.value is not None else "") + 15


    # Configurar la respuesta como archivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="datos_{tipo_information}_{fecha}.xlsx"'

    # Guardar el libro de trabajo en la respuesta
    wb.save(response)

    return response

#endregion 


def filtroMovimientos_fecha(fechaInicio, context ,fechaFinal):
        movimientosFiltrados=[]
        if(fechaInicio != "" and fechaFinal != ""):
            fechaInicio_strToDatetime = datetime.datetime.strptime(fechaInicio,"%d/%m/%Y %H:%M")
            fechaFinal_strToDatetime = datetime.datetime.strptime(fechaFinal,"%d/%m/%Y %H:%M")
            if(fechaInicio_strToDatetime == fechaFinal_strToDatetime):
                for i in range(0,len(context)):
                    x = context[i]["fecha_pago"]
                    fecha_strToDatetime = datetime.datetime.strptime(x, "%d/%m/%Y %H:%M")
                    if fechaInicio_strToDatetime.date() == fecha_strToDatetime.date():
                        movimientosFiltrados.append(context[i])
            else:
                for i in range(0,len(context)):
                    x = context[i]["fecha_pago"]
                    fecha_strToDatetime = datetime.datetime.strptime(x, "%d/%m/%Y %H:%M")
                    if fechaInicio_strToDatetime.date() <= fecha_strToDatetime.date() <= fechaFinal_strToDatetime.date():
                        movimientosFiltrados.append(context[i])
                    
        elif(fechaInicio != "" and fechaFinal==""):
            fechaInicio_strToDatetime = datetime.datetime.strptime(fechaInicio,"%d/%m/%Y %H:%M")
            
            for i in range(0,len(context)):
                x = context[i]["fecha_pago"]
                fecha_strToDatetime = datetime.datetime.strptime(x, "%d/%m/%Y %H:%M")
                if fechaInicio_strToDatetime.date() <= fecha_strToDatetime.date():
                    movimientosFiltrados.append(context[i])
        elif(fechaInicio == "" and fechaFinal!=""):
            fechaFinal_strToDatetime = datetime.datetime.strptime(fechaFinal,"%d/%m/%Y %H:%M")
            
            for i in range(0,len(context)):
                x = context[i]["fecha_pago"]
                fecha_strToDatetime = datetime.datetime.strptime(x, "%d/%m/%Y %H:%M")
                if fechaFinal_strToDatetime.date() >= fecha_strToDatetime.date():
                    movimientosFiltrados.append(context[i])
        return movimientosFiltrados


def getCampaniaActual():
    list_mesesStr = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
    mes_actual = datetime.datetime.now().month
    anio_actual = datetime.datetime.now().year
    return f'{list_mesesStr[mes_actual-1]} {anio_actual}'


def getAllCampaniaOfYear():
    list_mesesStr = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
    anio_actual = datetime.datetime.now().year
    meses_formato = [f'{mes} {anio_actual}' for mes in list_mesesStr]
    return meses_formato

# Obtener la campania de acuerdo a la fecha que se pasa por parametro
def getCampaniaByFecha(fecha):
    list_mesesStr = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
    mes = fecha.month
    anio = fecha.year
    return f'{list_mesesStr[mes-1]} {anio}'

# Para obtener todas las compañas desde el inicio de la empresa (2021)
def getTodasCampaniasDesdeInicio():
    list_mesesStr = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                     "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    anio_actual = datetime.datetime.now().year
    anio_inicio = 2021
    campanias = []
    
    # Iterar desde el año actual hasta el año de inicio (descendente)
    for anio in range(anio_actual, anio_inicio - 1, -1):
        # Para cada año, agregar las campañas en orden
        campanias.extend([f'{mes} {anio}' for mes in list_mesesStr])
    
    return campanias


def obtener_ultima_campania():
    # Lo importo aqui para evitar el error de dependencias circulares
    from sales.models import Ventas

    # Obtener el número de campaña más alto
    ultima_campania = Ventas.objects.aggregate(Max('campania'))['campania__max']
    if(ultima_campania == None):
        return 0
    else:
        return ultima_campania


def searchSucursalFromStrings(sucursal):
    from users.models import Sucursal
    sucursalObject = ""
    
    if(sucursal == "Sucursal central"):
        sucursalObject = Sucursal.objects.get(pseudonimo="Sucursal central")  
    else:  
        localidad_buscada, provincia_buscada = map(str.strip, sucursal.split(","))
        sucursalObject = Sucursal.objects.get(localidad = localidad_buscada, provincia = provincia_buscada)

    return sucursalObject


def get_ventasBySucursal(sucursal):
    from sales.models import Ventas
    if sucursal == "":
        return Ventas.objects.all()
    return Ventas.objects.filter(agencia__pseudonimo=sucursal)


def obtenerStatusAuditoria(venta): # Devuelve el estado de la ultima auditoria

    #Verifica si la lista de auditorías está vacía
    if len(venta.auditoria) == 0:
        return {"statusText": "Pendiente", "statusIcon": static(f"/images/icons/operationSuspendido.svg")}  # No auditada
    
    # Obtiene la última auditoría
    ultima_auditoria = venta.auditoria[-1]
    
    # Verifica el estado de la última auditoría
    if ultima_auditoria.get("grade") is True:
        return {"statusText": "Aprobada", "statusIcon": static(f"images/icons/operationActivo.svg")}  # No auditada

    elif ultima_auditoria.get("grade") is False:
        return {"statusText": "Desaprobada", "statusIcon": static(f"images/icons/operationBaja.svg")}  # No auditada


def formatear_moneda(valor):
    """
    Formatea un número en formato de moneda, separando miles con puntos.
    
    Args:
        valor (int, float, str): Número a formatear.
    
    Returns:
        str: Número formateado en formato de moneda.
    """
    try:
        # Convierte el valor a float, en caso de que sea string
        valor = float(valor)
        
        # Divide el entero y los decimales
        entero, decimal = divmod(valor, 1)
        entero_formateado = f"{int(entero):,}".replace(",", ".")
        
        # Si hay decimales, los añade con coma, redondeando a 2 dígitos
        if decimal > 0:
            return f"{entero_formateado},{round(decimal * 100):02d}"
        
        return entero_formateado
    except (ValueError, TypeError):
        # Maneja valores inválidos devolviendo un string vacío
        return ""

#region Data Structures ----------------------------------------------------------

def getInfoBaseCannon(venta, cuota):
    cliente = Cliente.objects.get(nro_cliente=venta.nro_cliente.nro_cliente)
    return {
        'cuota': {'data': cuota["cuota"], 'verbose_name': 'Cuota'},
        'nro_operacion': {'data': cuota["nro_operacion"], 'verbose_name': 'N° Operación'},
        'contratos': {'data': venta.cantidadContratos, 'verbose_name': 'Cantidad de Contratos'},
        'nombre_del_cliente': {'data': cliente.nombre, 'verbose_name': 'Nombre del Cliente'},
        'nro_del_cliente': {'data': cliente.nro_cliente, 'verbose_name': 'N° del Cliente'},
        'agencia': {'data': venta.agencia.pseudonimo, 'verbose_name': 'Agencia'},
        'tipo_mov': {'data': "Ingreso", 'verbose_name': 'Tipo de Movimiento'},
        'fecha_de_vencimiento': {'data': cuota['fechaDeVencimiento'], 'verbose_name': 'Fecha de Vencimiento'},
        'descuento': {'data': cuota['descuento'], 'verbose_name': 'Descuento'},
        'estado': {'data': cuota['status'], 'verbose_name': 'Estado'},
        'dias_de_mora': {'data': cuota['diasRetraso'], 'verbose_name': 'Días de Mora'},
        'total_final': {'data': cuota.get('totalFinal', 0), 'verbose_name': 'Total Final'},
        'interes_por_mora': {'data': cuota.get('interesPorMora', 0), 'verbose_name': 'Interés por Mora'},
    }


def dataStructureCannons(sucursal=None):
    from sales.models import Ventas, MetodoPago, CuentaCobranza
    from elanelsystem.views import convertirValoresALista
    
    ventas = ""
    
    if sucursal:
        listaAgencias = convertirValoresALista({"agencia": sucursal})["agencia"]
        ventas = Ventas.objects.filter(agencia__pseudonimo__in=listaAgencias)
    else:
        ventas = Ventas.objects.all()

    cuotas_data = []

    for i in range(int(ventas.count())):
        venta = ventas[i]

        for k in range(len(venta.cuotas)):
            cuota = venta.cuotas[k]

            if cuota["status"] in ["pagado", "parcial", "atrasado"]:
                for pago in cuota["pagos"]:
                    mov = {**getInfoBaseCannon(venta, cuota), **{
                        'metodoPago': {'data': MetodoPago.objects.filter(id=int(pago['metodoPago']))[0].alias, 'verbose_name': 'Método de Pago'},
                        'monto': {'data': pago['monto'], 'verbose_name': 'Monto Pagado'},
                        'fecha': {'data': pago['fecha'], 'verbose_name': 'Fecha de Pago'},
                        'cobrador': {'data': CuentaCobranza.objects.filter(id=int(pago['cobrador']))[0].alias, 'verbose_name': 'Cobrador'},
                    }}
                    cuotas_data.append(mov)
            else:
                mov = {**getInfoBaseCannon(venta, cuota), **{
                    'metodoPago': {'data': "", 'verbose_name': 'Método de Pago'},
                    'monto': {'data': "", 'verbose_name': 'Monto Pagado'},
                    'fecha': {'data': "", 'verbose_name': 'Fecha de Pago'},
                    'cobrador': {'data': "", 'verbose_name': 'Cobrador'},
                }}
                cuotas_data.append(mov)

    # cuotas_data.reverse()
    return cuotas_data


def dataStructureVentas(sucursal=None):
    from sales.models import Ventas

    if sucursal:
        ventas = get_ventasBySucursal(sucursal)
    else:
        ventas = Ventas.objects.all()
        
    ventasList = []
    for i in range(int(ventas.count())):
        venta = ventas[i]
        
        ventaDict = {
            'nro_operacion': {'data': venta.nro_operacion, 'verbose_name': 'N° ope'},
            'fecha': {'data': venta.fecha, 'verbose_name': 'Fecha'},
            'nro_cliente': {'data': venta.nro_cliente.nro_cliente, 'verbose_name': 'N° cliente'},
            'nombre_de_cliente': {'data': venta.nro_cliente.nombre, 'verbose_name': 'Nombre del cliente'},
            'agencia': {'data': venta.agencia.pseudonimo, 'verbose_name': 'Agencia'},
            'nro_cuotas': {'data': venta.nro_cuotas, 'verbose_name': 'N° cuotas'},
            'id': {'data': venta.id, 'verbose_name': 'ID'},
            'campania': {'data': venta.campania, 'verbose_name': 'Campaña'},
            'importe': {'data': venta.importe, 'verbose_name': 'Importe'},
            'paquete': {'data': venta.paquete, 'verbose_name': 'Paquete'},
            'primer_cuota': {'data': venta.primer_cuota, 'verbose_name': 'Primer cuota'},
            'suscripcion': {'data': venta.anticipo, 'verbose_name': 'Suscripción'},
            'cuota_comercial': {'data': venta.importe_x_cuota, 'verbose_name': 'Cuota comercial'},
            'interes_generado': {'data': venta.intereses_generados, 'verbose_name': 'Interés generado'},
            'total_a_pagar': {'data': venta.total_a_pagar, 'verbose_name': 'Total a pagar'},
            'dinero_entregado': {'data': getDineroEntregado(venta.cuotas), 'verbose_name': 'Dinero entregado'},
            'dinero_restante': {'data': venta.total_a_pagar - getDineroEntregado(venta.cuotas), 'verbose_name': 'Dinero restante'},
            'vendedor': {'data': venta.vendedor.nombre, 'verbose_name': 'Vendedor'},
            'producto': {'data': venta.producto.nombre, 'verbose_name': 'Producto'},
            'supervisor': {'data': venta.supervisor.nombre, 'verbose_name': 'Supervisor'},
        }

        # Agregar el campo si la venta esta AUDITADA  
        if len(venta.auditoria) > 0:   
            last_auditoria = venta.auditoria[-1]
            ventaDict["auditada"] = {'data': "Si", 'verbose_name': 'Auditada'}
            ventaDict["ultima_auditoria"] = {'data': last_auditoria["grade"], 'verbose_name': 'Última auditoría'}

        # Agregar el campo si la venta esta ADJUDICADA
        if(venta.adjudicado["status"]):
            ventaDict["adjudicado"] = {'data': "Si", 'verbose_name': 'Adjudicado'}
            ventaDict["tipo_de_adjudicacion"] = {'data': venta.adjudicado["tipo"], 'verbose_name': 'Tipo de adjudicación'}

        # Agregar el campo si la venta esta DE BAJA
        if(venta.deBaja["status"]):
            ventaDict["de_baja"] = {'data': "Si", 'verbose_name': 'De baja'}
            ventaDict["motivo_de_baja"] = {'data': venta.deBaja["motivo"] , 'verbose_name': 'Motivo de baja'}
            ventaDict["responsable"] = {'data': venta.deBaja["responsable"], 'verbose_name': 'Responsable'}
        
        # Agregar el campo si la venta esta SUSPENDIDA
        if(venta.suspendida):
            ventaDict["suspendida"] = {'data': "Si", 'verbose_name': 'Suspendida'}

        ventaDict['observaciones'] = {'data': venta.observaciones, 'verbose_name': 'Observaciones'}

        ventasList.append(ventaDict)

    return ventasList


def dataStructureMovimientosExternos(sucursal=None):
    from sales.models import MovimientoExterno
    from elanelsystem.views import convertirValoresALista

    movs_externos = ""
    
    if sucursal:
        listaAgencias = convertirValoresALista({"agencia":sucursal})["agencia"]
        movs_externos = MovimientoExterno.objects.filter(agencia__pseudonimo__in=listaAgencias)
    
    else:
        movs_externos = MovimientoExterno.objects.all()
        
    movsExternosList = []
    for movs_externo in movs_externos:
        movsExternoDict = {
            "tipoIdentificacion": {'data': movs_externo.tipoIdentificacion, 'verbose_name': 'Tipo Identificación'},
            "nroIdentificacion": {'data': movs_externo.nroIdentificacion, 'verbose_name': 'N° Identificación'},
            "tipoComprobante": {'data': movs_externo.tipoComprobante, 'verbose_name': 'Tipo Comprobante'},
            "nroComprobante": {'data': movs_externo.nroComprobante, 'verbose_name': 'N° Comprobante'},
            "denominacion": {'data': movs_externo.denominacion, 'verbose_name': 'Denominación'},
            "tipoMoneda": {'data': movs_externo.tipoMoneda, 'verbose_name': 'Tipo Moneda'},
            "tipo_mov": {'data': movs_externo.movimiento, 'verbose_name': 'Tipo Movimiento'},
            "monto": {'data': movs_externo.dinero, 'verbose_name': 'Monto'},
            "metodoPago": {'data': movs_externo.metodoPago, 'verbose_name': 'Método de Pago'},
            "agencia": {'data': movs_externo.agencia.pseudonimo, 'verbose_name': 'Sucursal'},
            "cobrador": {'data': movs_externo.cobrador, 'verbose_name': 'Cobrador'},
            "fecha": {'data': movs_externo.fecha, 'verbose_name': 'Fecha'},
            "campania": {'data': movs_externo.campania, 'verbose_name': 'Campaña'},
            "concepto": {'data': movs_externo.concepto, 'verbose_name': 'Concepto'},
            "premio": {'data': movs_externo.premio, 'verbose_name': 'Premio'},
            "adelanto": {'data': movs_externo.adelanto, 'verbose_name': 'Adelanto'},
        }
        
        movsExternosList.append(movsExternoDict)
    
    return movsExternosList


def dataStructureMoviemientosYCannons(sucursal):
    structureCannons = dataStructureCannons(sucursal)
    structureMovsExternos = dataStructureMovimientosExternos(sucursal)
    structureMovimientos_Generales = structureCannons + structureMovsExternos

    # Logica para colocar un ID de indice a cada movimiento
    id_cont = 0
    for mov in structureMovimientos_Generales:
        id_cont += 1
        mov["id_cont"] = id_cont

    return structureMovimientos_Generales


def dataStructureClientes(sucursal=None):
    from users.models import Cliente
    from elanelsystem.views import convertirValoresALista

    clientes = ""
    
    if sucursal:
        listaAgencias = convertirValoresALista({"agencia":sucursal})["agencia"]
        clientes = Cliente.objects.filter(agencia_registrada__pseudonimo__in=listaAgencias)
    
    else:
        clientes = Cliente.objects.all()
        
    clienteList = []
    for cliente in clientes:
        clienteDict = {
            "nro_cliente": {'data': cliente.nro_cliente, 'verbose_name': 'N° Cli'},
            "nombre": {'data': cliente.nombre, 'verbose_name': 'Nombre'},
            "dni": {'data': cliente.dni, 'verbose_name': 'DNI'},
            "domic": {'data': cliente.domic, 'verbose_name': 'Domicilio'},
            "loc": {'data': cliente.loc, 'verbose_name': 'Localidd'},
            "prov": {'data': cliente.prov, 'verbose_name': 'Provincia'},
            "cod_postal": {'data': cliente.cod_postal, 'verbose_name': 'Codigo Postal'},
            "tel": {'data': cliente.tel, 'verbose_name': 'Telefono'},
            "fec_nacimiento": {'data': cliente.fec_nacimiento, 'verbose_name': 'Fecha de Nacimiento'},
            "agencia": {'data': cliente.agencia_registrada.pseudonimo, 'verbose_name': 'Agencia registrada'},
            "estado_civil": {'data': cliente.estado_civil, 'verbose_name': 'Estado civil'},
            "ocupacion": {'data': cliente.ocupacion, 'verbose_name': 'Ocupacion'},
        }
        
        clienteList.append(clienteDict)
    
    return clienteList
#endregion


#region Other functions
def deleteFieldsInDataStructures(lista_dicts, campos_a_eliminar):
    # Iterar sobre cada diccionario en la lista
    for item in lista_dicts:
        # Eliminar los campos especificados si existen en el diccionario
        for campo in campos_a_eliminar:
            if campo in item:
                del item[campo]
    return lista_dicts


def formatKeys(lista_dicts):
    # Nueva lista de diccionarios con claves formateadas
    lista_formateada = []

    # Iterar sobre cada diccionario en la lista
    for item in lista_dicts:
        nuevo_dict = {}
        for key, value in item.items():
            # Separar la clave por "_" y capitalizar cada parte
            partes = key.split("_")

            # Unir las partes con espacios y crear la nueva clave
            nueva_clave = " ".join(partes)
            nueva_clave = nueva_clave.capitalize()

            # Añadir al nuevo diccionario
            nuevo_dict[nueva_clave] = value

        # Añadir el nuevo diccionario a la lista formateada
        lista_formateada.append(nuevo_dict)

    return lista_formateada


def getEstadoVenta(venta):
    if(venta.deBaja["status"]):
        return f"De baja por {venta.deBaja['motivo']}"
    elif(venta.suspendida):
        return "Suspendida"
    elif(venta.adjudicado["status"]):
        return f"Adjudicada por {venta.adjudicado['tipo']}"
    else:
        return "Activo"
    

def getCuotasPagadasSinCredito(cuotas):
    cuotasPagadasSinCredito = []
    for cuota in cuotas:
        pagos = cuota["pagos"]
        metodoDePagoDeCuota = [pago["metodoPago"] for pago in pagos] # Obtiene los metodos de pago de la cuota
        # Me aseguro que si se aplico un credito a una cuota y no fue el unico metodo de pago, se tome como ultima cuota porque quiere decir que el cliente abono un monto de la cuota
        if("Credito" in metodoDePagoDeCuota and len(metodoDePagoDeCuota) != 1):
            cuotasPagadasSinCredito.append(cuota)
        # Si la cuota no tiene credito, se toma como ultima cuota
        elif ("Credito" not in metodoDePagoDeCuota):
            cuotasPagadasSinCredito.append(cuota)
    return cuotasPagadasSinCredito


def bloquer_desbloquear_cuotas(cuotas):
    nuevas_cuotas = []
    for i in range(0,len(cuotas)):
        cuota = cuotas[i]
        if not (i == 0):
            pagos = cuota["pagos"]
            metodoDePagoDeCuota = [pago["metodoPago"] for pago in pagos] # Obtiene los metodos de pago de la cuota
            if(cuotas[i-1]["status"] == "Pagado"):
                cuota["bloqueada"] = False
            elif("Credito" in metodoDePagoDeCuota):
                cuota["bloqueada"] = False
            else:
                cuota["bloqueada"] = True
        nuevas_cuotas.append(cuota)
    return nuevas_cuotas


def getDineroEntregado(cuotas):
    dineroEntregado = 0
    for cuota in cuotas:
        pagos = cuota["pagos"]
        if(len(pagos)>0):
            for pago in pagos:
                dineroEntregado += pago["monto"]
    return dineroEntregado

#endregion


#region Para enviar correos electrónicos
# def send_html_email(subject, template, context, from_email, to_email):
#     """
#     Envía un correo electrónico HTML.

#     :param subject: Asunto del correo electrónico.
#     :param template: Ruta al template HTML.
#     :param context: Contexto para renderizar el template.
#     :param from_email: Dirección de correo del remitente.
#     :param to_email: Dirección de correo del destinatario.
    
#     """
#     html_message = render_to_string(template, context)
#     plain_message = strip_tags(html_message)
    
#     email = EmailMessage(subject, plain_message, from_email, [to_email])
#     email.content_subtype = 'html'  # Define que el contenido es HTML
#     email.send()
def send_html_email(subject, template, context, from_email, to_email):
    """
    Envía un correo electrónico en formato HTML.
    """
    html_message = render_to_string(template, context)  # Renderizar el template con contexto
    plain_message = strip_tags(html_message)  # Generar versión en texto plano

    email = EmailMessage(subject, html_message, from_email, [to_email])
    email.content_subtype = "html"  # Asegurar que se envía como HTML
    email.send()
#endregion





# def asignar_usuario_a_ventas():
#     import random
#     from sales.models import Ventas
#     from users.models import Usuario  # Ajusta esto al nombre de tu app de usuarios

#     # Obtiene todas las ventas que no tienen vendedor o supervisor
#     ventas_sin_vendedor_o_supervisor = Ventas.objects.filter(
#         vendedor__isnull=True
#     ) | Ventas.objects.filter(
#         supervisor__isnull=True
#     )

#     # Obtiene todos los usuarios del modelo Usuario
#     usuarios = list(Usuario.objects.all())
#     if not usuarios:
#         print("No hay usuarios disponibles para asignar.")
#         return

#     # Asigna un usuario aleatorio a cada venta
#     for venta in ventas_sin_vendedor_o_supervisor:
#         if not venta.vendedor:
#             venta.vendedor = random.choice(usuarios)  # Asigna un vendedor aleatorio
#         if not venta.supervisor:
#             venta.supervisor = random.choice(usuarios)  # Asigna un supervisor aleatorio

#         # Guarda los cambios en la base de datos
#         venta.save()

#     print(f"Se han actualizado {ventas_sin_vendedor_o_supervisor.count()} ventas.")