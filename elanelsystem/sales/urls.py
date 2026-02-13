from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from configuracion import views
from .views import *
from .utils import exportar_excel  # Importa la función de exportación
from .views import GraficosDashboard,DashboardColaboradores
from .views import ventas_analytics_api, exportar_ventas_excel, exportar_pagos_cannon_excel
from .views import graficos
app_name="sales"

urlpatterns = [

    path("resumen/",Resumen.as_view(),name="resumen"),

    #region URLs Ventas ----------------------------------
    path("ventas/importar/",importVentas,name="importVentas"),
    path("ventas/cliente/<int:pk>/crear_venta/",CrearVenta.as_view(),name="create_sale"),
    path("ventas/get_vendedores_supervisores/",requestVendedores_Supervisores,name="requestVendedores_Supervisores"),
    path("ventas/detalles", VentasDetalles.as_view(),name="detallesVentas"),
    path("ventas/detalle_venta/<int:pk>/",DetailSale.as_view(),name="detail_sale"),

    path("ventas/detalle_venta/<int:pk>/eliminar_venta/",eliminarVenta,name="delete_sale"),
    path("ventas/detalle_venta/descuento_cuota/",aplicarDescuentoCuota,name="descCuota"),
    path("ventas/detalle_venta/get_specific_cuota/",getUnaCuotaDeUnaVenta,name="getCuota"),
    path("ventas/detalle_venta/pay_cuota/",pagarCuota,name="payCuota"),
    # path("ventas/detalle_venta/anular_cuota/",anularCuota,name="anularCuota"),

    path("ventas/detalle_venta/<int:pk>/dar_baja/",darBaja,name="darBaja"),
    path("ventas/<int:pk>/adjudicacion/sorteo/",CreateAdjudicacion.as_view(),name="adjSorteo"),
    path("ventas/<int:pk>/adjudicacion/negociacion/",CreateAdjudicacion.as_view(),name="adjNegociacion"),
    path("ventas/<int:pk>/cambiopack",ChangePack.as_view(),name="cambioPack"),
    path("ventas/<int:pk>/cambiotitularidad",ChangeTitularidad.as_view(),name="changeTitu"),
    path("ventas/ventas_suspendidas",PanelVentasSuspendidas.as_view(),name="ventasSuspendidas"),
    path("ventas/simulador_plan_recupero/<int:pk>/",SimuladorPlanRecupero.as_view(),name="simuladorPlanrecupero"),
    path("ventas/crear_plan_recupero/<int:pk>/",PlanRecupero.as_view(),name="planRecupero"),
    
    path("ventas/detalle_venta/solcitud_anulacion_cuota/",solicitudBajaCuota,name="solicitudAnulacionCuota"),
    path('ventas/detalle_venta/autorizar-baja/<int:ventaID>/<str:cuota>/', darAutorizacionBajaCuota, name='autorizar_baja_cuota'),
    path('ventas/detalle_venta/pagina_confirmacion_baja_cuota/', pagina_confirmacion, name='pagina_confirmacion_baja_cuota'),
    path('ventas/detalle_venta/confirma-baja-cuota/', darBajaCuota, name='darBajaCuota'),

    path('ventas/comisionables/',VentasComisionables.as_view(),name='ventas_comisionables'),
    # endpoint AJAX para toggle
    path('ventas/comisionable-toggle/',toggle_comisionable,name='toggle_comisionable'),
    # endpoint para el dashboard de gráficos
    path('graficos/', GraficosDashboard.as_view(), name='graficos'),
    path('graficos/cannon/', graficos_pagos_cannon, name='graficos_cannon'),
    path('dashboard/colaboradores/', DashboardColaboradores.as_view(), name='dashboard_colaboradores'),
    path('api/autocomplete-colaborador/', autocomplete_colaborador, name='autocomplete_colaborador'),
    path('api/ventas-colaborador/', ventas_colaborador, name='ventas_colaborador'),
    path('api/ventas-analytics/', ventas_analytics_api, name='ventas_analytics_api'),
    path('api/pagos-cannon-analytics/', pagos_cannon_analytics_api, name='pagos_cannon_analytics_api'),
    path('api/exportar-ventas-excel/', exportar_ventas_excel, name='exportar_ventas_excel'),
    path('api/exportar-pagos-cannon-excel/', exportar_pagos_cannon_excel, name='exportar_pagos_cannon_excel'),
    #endregion ----------------------------------------------------------

    #region URLs Caja -----------------------------------------------------
    path("ventas/caja/",Caja.as_view(),name="caja"),
    path("arqueo/", CierreCaja.as_view(), name="arqueo"),
    path("arqueo/old/", OldArqueosView.as_view(), name="oldArqueos"),
    path("arqueo/saldo/", ArqueoSaldoAPI.as_view(), name="arqueoSaldo"),

    path("ventas/movs_pagos/", movs_pagos_list_api, name="movs_pagos_list"),
    path("ventas/movs_pagos/<str:kind>/<int:pk>/", movs_pagos_detail_api, name="movs_pagos_detail"),
    #endregion -----------------------------------------------------------
    
    #region URLs PDFs ------------------------------------------------------
    path("ventas/pdf/baja/<int:pk>",viewsPDFBaja,name="bajaPDF"),
    path("ventas/pdf/titularidad/<int:pk>/<int:idCambio>",viewPDFTitularidad,name="tituPDF"),
    path("ventas/pdf/arqueo/<int:pk>/",viewPDFArqueo,name="arqueoPDF"),
    path("ventas/pdf/informe/", viewsPDFInforme, name="ventas_pdf_informe"),
    path("ventas/excel/informe/", viewsExcelInforme, name="ventas_excel_informe"),
    # path('ventas/detalle_venta/recibo/pago/<int:pk>/', viewPDFReciboCuota, name='getReciboCuota'),
    #     path(
    #     "ventas/detalle_venta/recibo-json/pago/<int:pk>/",
    #     recibo_pago_json,
    #     name="recibo-pago-json"
    # ),
    path('ventas/detalle_venta/recibo-preview/<int:pk>/', recibo_preview, name='recibo-preview'),
    #endregion ---------------------------------------------------------
        
    #region URLs PostVentas --------------------------------------------
    path("ventas/postventas/", PostVenta.as_view(), name="postVentaList"),
    path("ventas/auditorias/api/", auditorias_api, name="auditorias_api"),
    path("ventas/auditorias/crear/", crear_auditoria, name="crear_auditoria"),
    path('ventas/postventas/informe/', viewsPDFInformePostVenta, name='postVentaPDF'),
    #endregion ---------------------------------------------------------
    
    #region URLs Specifics Functions ------------------------------------------------------------
    # path('ventas/detalles/', requestDetallesVentas, name='requestDetallesVentas'),
    # path('ventas/request_ventas/', requestVentasAuditoria, name='requestVentasAuditorias'),

    path('requestmovs/', requestMovimientos, name='rmovs'),
    path('create_new_mov/', createNewMov, name='create_new_mov'),
    #endregion --------------------------------------------------------------------------------

    path("api/cotizaciones/dolar/", cotizaciones_dolar, name="cotizaciones_dolar"),
]
