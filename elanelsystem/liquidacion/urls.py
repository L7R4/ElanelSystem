from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *
 
app_name="liquidacion"

urlpatterns = [
    path("ventas/liquidaciones/panel/", LiquidacionesPanel.as_view(),name="liquidacionesPanel"),
    path("ventas/liquidaciones/comisiones/", LiquidacionesComisiones.as_view(),name="liquidacionesComisiones"),
    path("ventas/liquidaciones/requestColaboradores/", requestColaboradoresWithComisiones,name="requestColaboradoresWithComisiones"),
    path('ventas/liquidaciones/comisiones/nuevo_ajuste/', crearAjusteComision, name='crearAjusteComision'),
    # path("ventas/liquidaciones/new_ausencia_tardanza/", newAusenciaTardanza,name="newAusenciaTardanza"),
    path("ventas/liquidaciones/requestColaboradores_tardanzasAusencias/", requestColaboradores_TardanzasAusencias,name="requestColaboradores_TardanzasAusencias"),
    path("ventas/liquidaciones/ranking/", LiquidacionesRanking.as_view(),name="liquidacionesRanking"),
    path("ventas/liquidaciones/ausencias_tardanzas/", LiquidacionesAusenciaYTardanzas.as_view(),name="liquidacionesAusenciaYTardanzas"),    
    path("ventas/liquidaciones/pdf/pre_liquidacion/", preViewPDFLiquidacion, name="preViewPDFLiquidacion"),
    path('ventas/liquidaciones/pdf/liquidacion/<int:id>/', viewPDFLiquidacion, name='viewPDFLiquidacion'),
    path('ventas/liquidaciones/detalles/<slug:tipo_slug>/', DetallesComisionesView.as_view(), name='detallesComisionesView'),


    path("ventas/liquidaciones/historial/", HistorialLiquidaciones.as_view(), name="historialLiquidaciones"),
    
]
