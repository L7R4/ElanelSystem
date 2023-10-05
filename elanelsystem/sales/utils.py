from django.template.loader import get_template
from weasyprint import HTML,CSS
import elanelsystem.settings as settings
import os

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