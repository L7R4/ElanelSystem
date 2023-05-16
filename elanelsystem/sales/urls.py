from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import Resumen,CrearVenta
 
app_name="sales"

urlpatterns = [
    path("resumen/",Resumen.as_view(),name="resumen"),
    path("ventas/crear_venta",CrearVenta.as_view(),name="create_sale")
]
