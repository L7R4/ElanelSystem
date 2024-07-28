from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *
 
app_name="products"

urlpatterns = [
    path("planes/",CRUDPlanes.as_view(),name="planes"),
    path("products/request/",requestProducts,name="get_products"),
    path("list_products/",ViewProducts.as_view(),name="listProducts")
]