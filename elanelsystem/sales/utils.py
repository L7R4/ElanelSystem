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
from django.http import HttpResponse, JsonResponse
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from users.models import Cliente

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

def printPDFLiquidacion(data,url,liquidacionName):
    template = get_template("pdfForLiquidacion.html")
    context = data
    html_template = template.render(context)
    css_url = os.path.join(settings.BASE_DIR, "static/css/pdfLiquidacion.css")
    if not os.path.exists(settings.PDF_STORAGE_DIR):
        os.makedirs(settings.PDF_STORAGE_DIR)
    pdf = HTML(string=html_template,base_url=url).write_pdf(target=liquidacionName, stylesheets = [CSS(css_url)])
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
def exportar_excel(information):
    # Crear un nuevo libro de trabajo
    wb = Workbook()

    # Seleccionar la primera hoja (automáticamente creada)
    ws = wb.active
    ws.title = "Datos"  # Cambiar el nombre de la hoja

    # Estilo para toda la fila 1
    bold_font = Font(bold=True)  # Negrita
    yellow_fill = PatternFill(start_color="546FFF", end_color="546FFF", fill_type="solid")  # Relleno amarillo
    center_alignment = Alignment(horizontal='center')  # Alineación centrada
    thin_border = Border(
        left=Side(border_style="thin"),
        right=Side(border_style="thin"),
        top=Side(border_style="thin"),
        bottom=Side(border_style="thin")
    )


    # Obtener los encabezados a partir de las claves del primer diccionario en la lista
    if information:
        information = formatKeys(information)
        encabezados = list(information[0].keys())
        
        ws.append(encabezados)  # Agregar encabezados a la hoja

        # Agregar datos de cada diccionario a la hoja
        for item in information:
            fila = []
            for key in encabezados:
                valor = item.get(key, "")
                fila.append(valor)
            ws.append(fila)
    
    for cell in ws[1]:  # Obtener todas las celdas de la fila 1
        cell.font = bold_font
        cell.fill = yellow_fill
        cell.alignment = center_alignment
        cell.border = thin_border
    
    # Ajustar el ancho de las columnas basado en la fila 1
    column_widths = [len(cell.value) for cell in ws[1]]  # Ancho basado en el contenido

    for idx, width in enumerate(column_widths, start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(idx)].width = width + 5  # Añadir espacio adicional

    # Configurar la respuesta como archivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="datos.xlsx"'

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


def obtener_ultima_campania():
    # Lo importo aca para evitar el error de dependencias circulares
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


#region Data Structures ----------------------------------------------------------

def getInfoBaseCannon(venta, cuota):
    cliente = Cliente.objects.get(nro_cliente = venta.nro_cliente.nro_cliente)
    return {
        'cuota' : cuota["cuota"],
        'nro_operacion': cuota["nro_operacion"],
        'contratos': venta.cantidadContratos,
        'nombre_del_cliente' : cliente.nombre,
        'nro_del_cliente' : cliente.nro_cliente,
        'sucursal' : venta.agencia.pseudonimo,
        'tipo_mov' : "Ingreso",
        'fecha_de_vencimiento' : cuota['fechaDeVencimiento'],
        'descuento' : cuota['descuento'],
        'estado' : cuota['status'],
        'dias_de_mora' : cuota['diasRetraso'],
        'total_final' : cuota.get('totalFinal',None),
        'interes_por_mora' : cuota.get('interesPorMora',None),
    }


def dataStructureCannons(sucursal):
    from sales.models import Ventas
    from elanelsystem.views import convertirValoresALista
    
    listaAgencias = convertirValoresALista({"agencia":sucursal})["agencia"]
    
    ventas = Ventas.objects.filter(agencia__pseudonimo__in=listaAgencias)

    cuotas_data = []

    for i in range(int(ventas.count())):
        venta = ventas[i]

        for k in range(len(ventas[i].cuotas)):
            cuota = ventas[i].cuotas[k]

            if ventas[i].cuotas[k]["status"] in ["Pagado", "Parcial", "Atrasado"]:
                for pago in cuota["pagos"]:
                    mov = {**getInfoBaseCannon(venta,cuota),**pago}
                    cuotas_data.append(mov)


    
    cuotas_data.reverse()
    return cuotas_data


def dataStructureVentas(sucursal):

    ventas = get_ventasBySucursal(sucursal)
    
    ventasList = []
    for i in range(int(ventas.count())):
        venta = ventas[i]
        
        ventaDict = {
            'nro_cliente' : venta.nro_cliente.nro_cliente,
            'nombre_de_cliente' : venta.nro_cliente.nombre,
            'nro_orden' : venta.nro_orden,
            'nro_cuotas' : venta.nro_cuotas,
            'agencia' : venta.agencia.pseudonimo,
            'campania' : venta.campania,
            'importe' : venta.importe,
            'paquete' : venta.paquete,
            'primer_cuota' : venta.primer_cuota,
            'suscripcion' : venta.anticipo,
            'cuota_comercial' : venta.importe_x_cuota,
            'vendedor' : venta.vendedor.nombre,
            'supervisor' : venta.supervisor.nombre,
        }

        # Agregar el campo si la venta esta AUDITADA       
        if(venta.auditoria[-1]["realizada"]):
            ventaDict["auditada"] = "Si"
            ventaDict["ultima_auditoria"] = venta.auditoria[-1]["grade"]

        # Agregar el campo si la venta esta ADJUDICADA
        if(venta.adjudicado["status"]):
            ventaDict["adjudicado"] = "Si"
            ventaDict["tipo_de_adjudicacion"] = venta.adjudicado["tipo"]

        # Agregar el campo si la venta esta DE BAJA
        if(venta.deBaja["status"]):
            ventaDict["de_baja"] = "Si"
            ventaDict["motivo_de_baja"] = venta.deBaja["motivo"]
            ventaDict["responsable"] = venta.deBaja["responsable"]
        
        # Agregar el campo si la venta esta SUSPENDIDA
        if(venta.suspendida):
            ventaDict["suspendida"] = "Si"

        
        ventaDict['observaciones'] = venta.observaciones

        ventasList.append(ventaDict)

    return ventasList


def dataStructureMovimientosExternos(sucursal):
    from sales.models import MovimientoExterno
    from elanelsystem.views import convertirValoresALista

    movs_externos = ""
    listaAgencias = convertirValoresALista({"agencia":sucursal})["agencia"]
    movs_externos = MovimientoExterno.objects.filter(agencia__pseudonimo__in=listaAgencias)
    return [
        {
            "tipoIdentificacion": movs_externo.tipoIdentificacion,
            "nroIdentificacion": movs_externo.nroIdentificacion,
            "tipoComprobante": movs_externo.tipoComprobante,
            "nroComprobante": movs_externo.nroComprobante,
            "denominacion": movs_externo.denominacion,
            "tipoMoneda": movs_externo.tipoMoneda,
            "tipo_mov": movs_externo.movimiento,
            "monto": movs_externo.dinero,
            "metodoPago": movs_externo.metodoPago,
            "sucursal": movs_externo.agencia.pseudonimo,
            "ente": movs_externo.ente,
            "fecha": movs_externo.fecha,
            "campania": movs_externo.campania,
            "concepto": movs_externo.concepto,
            "premio": movs_externo.premio,
            "adelanto": movs_externo.adelanto,
            } 
        
        for movs_externo in movs_externos]


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
        cuota = cuota[i]
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

#endregion


#region Para enviar correos electrónicos
def send_html_email(subject, template, context, from_email, to_email):
    """
    Envía un correo electrónico HTML.

    :param subject: Asunto del correo electrónico.
    :param template: Ruta al template HTML.
    :param context: Contexto para renderizar el template.
    :param from_email: Dirección de correo del remitente.
    :param to_email: Dirección de correo del destinatario.
    
    """
    html_message = render_to_string(template, context)
    plain_message = strip_tags(html_message)
    
    email = EmailMessage(subject, plain_message, from_email, [to_email])
    email.content_subtype = 'html'  # Define que el contenido es HTML
    email.send()
#endregion