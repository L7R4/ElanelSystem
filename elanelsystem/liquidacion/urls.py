from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *
 
app_name="liquidacion"

urlpatterns = [
    path("ventas/liquidaciones/panel/", LiquidacionesPanel.as_view(),name="liquidacionesPanel"),
    path("ventas/liquidaciones/comisiones/", LiquidacionesComisiones.as_view(),name="liquidacionesComisiones"),
    path("ventas/liquidaciones/requestColaboradores/", requestColaboradoresWithComisiones,name="requestColaboradoresWithComisiones"),
    path("ventas/liquidaciones/new_ausencia_tardanza/", newAusenciaTardanza,name="newAusenciaTardanza"),
    path("ventas/liquidaciones/requestColaboradores_tardanzasAusencias/", requestColaboradores_TardanzasAusencias,name="requestColaboradores_TardanzasAusencias"),
    path("ventas/liquidaciones/ranking/", LiquidacionesRanking.as_view(),name="liquidacionesRanking"),
    path("ventas/liquidaciones/detalle_ventas/", LiquidacionesDetallesVentas.as_view(),name="liquidacionesDetalleVentas"),
    path("ventas/liquidaciones/detalle_cuotas_adelantadas/", LiquidacionesDetallesCuotasAdelantadas.as_view(),name="liquidacionesDetalleCuotasAdelantadas"),
    path("ventas/liquidaciones/ausencias_tardanzas/", LiquidacionesAusenciaYTardanzas.as_view(),name="liquidacionesAusenciaYTardanzas"),    
    path("ventas/liquidaciones/pdf/liquidacion/", viewPDFLiquidacion, name="viewPDFLiquidacion"),    
]
