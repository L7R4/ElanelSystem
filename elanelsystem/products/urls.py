from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *
 
app_name="products"

urlpatterns = [
    path("planes/",Planes.as_view(),name="planes"),
    path("planes/delete/",deletePlan,name="delete_plan"),

    path("products/request/",requestProducts,name="get_products"),
    path("products/delete/",deleteProduct,name="delete_product"),

    path("list_products/",ViewProducts.as_view(),name="listProducts")
]