import uuid

from django.conf import settings
from django.db import models

from elanelsystem.storage_backends import SupabaseDocumentStorage


def ruta_por_categoria(instance, filename):
    return f"{instance.categoria}/{uuid.uuid4().hex}_{filename}"


EXTENSIONES_IMAGEN = {"jpg", "jpeg", "png", "gif", "webp", "svg", "bmp"}
EXTENSIONES_PDF = {"pdf"}

ICONOS_POR_EXTENSION = {
    "pdf": ("fa-file-pdf", "pdf"),
    "doc": ("fa-file-word", "word"),
    "docx": ("fa-file-word", "word"),
    "xls": ("fa-file-excel", "excel"),
    "xlsx": ("fa-file-excel", "excel"),
    "csv": ("fa-file-excel", "excel"),
    "ppt": ("fa-file-powerpoint", "ppt"),
    "pptx": ("fa-file-powerpoint", "ppt"),
    "zip": ("fa-file-zipper", "otro"),
    "rar": ("fa-file-zipper", "otro"),
    "txt": ("fa-file-lines", "otro"),
}


class Documento(models.Model):
    CATEGORIAS = [
        ("carta_documento", "Carta Documento"),
        ("liquidacion_pdf", "PDF de Liquidación"),
        ("recibo", "Recibo"),
        ("word", "Documento Word"),
        ("excel", "Planilla Excel"),
        ("imagen", "Imagen"),
        ("otro", "Otro"),
    ]

    categoria = models.CharField(max_length=30, choices=CATEGORIAS)
    archivo = models.FileField(upload_to=ruta_por_categoria, storage=SupabaseDocumentStorage())
    nombre_original = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255, blank=True)
    subido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_subida"]

    def __str__(self):
        return f"{self.get_categoria_display()} - {self.nombre_original}"

    @property
    def extension(self):
        return self.nombre_original.rsplit(".", 1)[-1].lower() if "." in self.nombre_original else ""

    @property
    def es_imagen(self):
        return self.extension in EXTENSIONES_IMAGEN

    @property
    def es_pdf(self):
        return self.extension in EXTENSIONES_PDF

    @property
    def es_previsualizable(self):
        return self.es_imagen or self.es_pdf

    @property
    def icono_fa(self):
        return ICONOS_POR_EXTENSION.get(self.extension, ("fa-file", "otro"))[0]

    @property
    def icono_color(self):
        return ICONOS_POR_EXTENSION.get(self.extension, ("fa-file", "otro"))[1]
