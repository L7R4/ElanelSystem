from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *
from .utils import exportar_excel  # Importa la función de exportación
app_name="sales"

urlpatterns = [

    path("resumen/",Resumen.as_view(),name="resumen"),
    
    #region URLs Ventas ----------------------------------
    path("ventas/importar/",importVentas,name="importVentas"),
    path("ventas/cliente/<int:pk>/crear_venta/",CrearVenta.as_view(),name="create_sale"),
    path("ventas/get_vendedores_supervisores/",requestVendedores_Supervisores,name="requestVendedores_Supervisores"),
    path("ventas/detalle_venta/<int:pk>/",DetailSale.as_view(),name="detail_sale"),
    path("ventas/detalle_venta/<int:pk>/eliminar_venta/",eliminarVenta,name="delete_sale"),
    path("ventas/detalle_venta/descuento_cuota/",aplicarDescuentoCuota,name="descCuota"),
    path("ventas/detalle_venta/get_specific_cuota/",getUnaCuotaDeUnaVenta,name="getCuota"),
    path("ventas/detalle_venta/pay_cuota/",pagarCuota,name="payCuota"),
    path("ventas/detalle_venta/anular_cuota/",anularCuota,name="anularCuota"),

    path("ventas/detalle_venta/<int:pk>/dar_baja/",darBaja,name="darBaja"),
    path("ventas/<int:pk>/adjudicacion/sorteo/",CreateAdjudicacion.as_view(),name="adjSorteo"),
    path("ventas/<int:pk>/adjudicacion/negociacion/",CreateAdjudicacion.as_view(),name="adjNegociacion"),
    path("ventas/<int:pk>/cambiopack",ChangePack.as_view(),name="cambioPack"),
    path("ventas/<int:pk>/cambiotitularidad",ChangeTitularidad.as_view(),name="changeTitu"),
    path("ventas/ventas_suspendidas",PanelVentasSuspendidas.as_view(),name="ventasSuspendidas"),
    path("ventas/simulador_plan_recupero/<int:pk>/",SimuladorPlanRecupero.as_view(),name="simuladorPlanrecupero"),
    path("ventas/crear_plan_recupero/<int:pk>/",PlanRecupero.as_view(),name="planRecupero"),

    #endregion ----------------------------------------------------------

    #region URLs Caja -----------------------------------------------------
    path("ventas/caja/",Caja.as_view(),name="caja"),
    path("ventas/caja/arqueo/",CierreCaja.as_view(),name="cierreDeCaja"),
    path("ventas/caja/arqueosanteriores",OldArqueosView.as_view(),name="oldArqueos"),
    #endregion -----------------------------------------------------------
    
    #region URLs PDFs ------------------------------------------------------
    path("ventas/pdf/baja/<int:pk>",viewsPDFBaja,name="bajaPDF"),
    path("ventas/pdf/titularidad/<int:pk>/<int:idCambio>",viewPDFTitularidad,name="tituPDF"),
    path("ventas/pdf/arqueo/<int:pk>/",viewPDFArqueo,name="arqueoPDF"),
    path('ventas/pdf/informe/', viewsPDFInforme, name='informePDF'),
    path('ventas/pdf/informesend/', viewPDFInformeAndSend, name='informeSend'),
    #endregion ---------------------------------------------------------
        
    #region URLs PostVentas --------------------------------------------
    path('ventas/postventas/', PostVenta.as_view(), name='postVentaList'),
    path('ventas/postventas/filtrar/', filtroVentasAuditoria, name='postVentaListFiltered'),
    path('ventas/postventas/informe/', viewsPDFInformePostVenta, name='postVentaPDF'),
    #endregion ---------------------------------------------------------
    
    #region URLs Specifics Functions ------------------------------------------------------------
    path('ventas/request_ventas/', requestVentas, name='requestVentas'),
    path('requestmovs/', requestMovimientos, name='rmovs'),
    path('create_new_mov/', createNewMov, name='create_new_mov'),
    #endregion --------------------------------------------------------------------------------

    #region URLS API PARA EL CRM
    # path('requestmovscrm/', requestMovimientosCRM, name='requestMovsCRM'),
    #endregion
]
