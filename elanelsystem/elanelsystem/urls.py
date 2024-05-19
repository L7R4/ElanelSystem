"""
URL configuration for elanelsystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_vxiew(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import logout_then_login
from .views import *
from sales.utils import exportar_excel

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", IndexLoginView.as_view(),name="indexLogin"),
    path("logout/", logout_view,name="logout"),
    path("",include("sales.urls", namespace="sales")),
    path("",include("users.urls", namespace="users")),
    path("",include("products.urls", namespace="products")),
    path("",include("liquidacion.urls", namespace="liquidacion")),

    # Path para manejo de filtros
    # path("data/filter/",filterManage, name="filterManage"),


    #region Reports ---------------------------------
    path('ventas/reportes/', ReportesView.as_view(), name='reporteView'),
    path('ventas/excel/exportar/', exportar_excel, name='exportExcel'),
    
    #endregion --------------------------------------
]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
