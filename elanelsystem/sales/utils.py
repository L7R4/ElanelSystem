from django.template.loader import get_template
from weasyprint import HTML,CSS
import elanelsystem.settings as settings
import os
import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.db.models import Max





def printPDF(data,url,productoName):
    template = get_template("pdfForBaja.html")
    context = data
    html_template = template.render(context)
    css_url = os.path.join(settings.BASE_DIR, "static/css/pdfForBaja.css")
    if not os.path.exists(settings.PDF_STORAGE_DIR):
        os.makedirs(settings.PDF_STORAGE_DIR)
    pdf = HTML(string=html_template,base_url=url).write_pdf(target=productoName, stylesheets = [CSS(css_url)])
    # print(pdf)
    return pdf

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

def filterMovs(data,params):
    paramsDict = params.dict()

    if(len(paramsDict.keys()) > 1):
        clearContext = {key: value for key, value in paramsDict.items() if value != '' and key != 'page'}
        # Si algun campo de fecha esta en la busqueda que filtre por la fecha
        if("fecha_inicial" in clearContext.keys() or "fecha_final" in clearContext.keys()):
            try:
                # Por si existen las 2 fechas
                data = filtroMovimientos_fecha(clearContext["fecha_inicial"],data,clearContext["fecha_final"])
                
            except KeyError as e:
                try:
                    # Por si solamente se pides de una fecha hacia delante
                    data = filtroMovimientos_fecha(clearContext["fecha_inicial"],data,"")
                    
                except KeyError as e:
                    # Por si solamente se pide hasta una determinada fecha
                    data = filtroMovimientos_fecha("",data,clearContext["fecha_final"])

            #Limpar el context del queryDict quitando la fecha inicial y final para que no haya errores para filtrar los otros campos
            clearContext = {key: value for key, value in clearContext.items() if key not in ('fecha_inicial', 'fecha_final')}
            # data = [item for item in contextByDateFiltered if all(item[key] == value for key, value in clearContext.items())]
            
            for key, values in clearContext.items():
                selected_values = [item.strip() for item in values.split('-')]
                data = [item for item in data if any(item.get(key, '').strip() == value for value in selected_values)]
        else:
            for key, values in clearContext.items():
                selected_values = [item.strip() for item in values.split('-')]
                data = [item for item in data if any(item.get(key, '').strip() == value for value in selected_values)]
    return data


def sendEmailPDF(email,pdf_path,sujeto):
        try:
            subject = sujeto
            from_email =  settings.EMAIL_HOST_USER
            to_email = [email]

            # Cargar la plantilla de correo electrónico HTML
            # email_template = get_template(os.path.join(settings.BASE_DIR, "templates/mailPlantilla.html"))
            # context = {}
            # email_content = email_template.render(context)

            # email = EmailMultiAlternatives(subject, '', from_email, to_email,bcc=[settings.EMAIL_HOST_USER])
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

def obtener_ultima_campania():
    # Lo importo aca para evitar el error de dependencias circulares
    from sales.models import Ventas

    # Obtener el número de campaña más alto
    ultima_campania = Ventas.objects.aggregate(Max('campania'))['campania__max']
    if(ultima_campania == None):
        return 0
    else:
        return ultima_campania

def clearNameSucursal(sucursal):
    return sucursal.localidad +", "+ sucursal.provincia

def searchSucursalFromStrings(sucursal):
    from users.models import Sucursal
    sucursalObject = ""
    
    if(sucursal == "Sucursal central"):
        sucursalObject = Sucursal.objects.get(pseudonimo="Sucursal central")  
    else:  
        localidad_buscada, provincia_buscada = map(str.strip, sucursal.split(","))
        sucursalObject = Sucursal.objects.get(localidad = localidad_buscada, provincia = provincia_buscada)

    return sucursalObject