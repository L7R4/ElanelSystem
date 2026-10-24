from django.urls import path

from . import views

app_name = "documentos"

urlpatterns = [
    path("documentos/", views.menu_documentos, name="menu"),
    path("documentos/subir/<slug:categoria>/", views.subir_documento, name="subir"),
    path("documentos/listado/", views.listado_documentos, name="listado"),
    path("documentos/eliminar/<int:pk>/", views.eliminar_documento, name="eliminar"),
]
