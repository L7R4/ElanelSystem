from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import Resumen,CrearVenta, DetailSale,Caja,CreateAdjudicacion,requestCuotas,viewsPDFBaja,ChangePack
 
app_name="sales"

urlpatterns = [
    path("resumen/",Resumen.as_view(),name="resumen"),
    path("ventas/cliente/<int:pk>/crear_venta/",CrearVenta.as_view(),name="create_sale"),
    # path("ventas/<int:pk>/crear_venta",CrearVenta.as_view(),name="create_sale"),
    path("ventas/detalle_venta/<int:pk>/",DetailSale.as_view(),name="detail_sale"),
    path("ventas/<int:pk>/adjudicacion/sorteo/",CreateAdjudicacion.as_view(),name="adjSorteo"),
    path("ventas/<int:pk>/adjudicacion/negociacion/",CreateAdjudicacion.as_view(),name="adjNegociacion"),
    path("ventas/<int:pk>/cambiopack",ChangePack.as_view(),name="cambioPack"),
    path('request-cuotas/', requestCuotas, name='rc'),
    path("ventas/caja/",Caja.as_view(),name="caja"),
    path("ventas/pdf/baja/<int:pk>",viewsPDFBaja,name="bajaPDF"),
]
