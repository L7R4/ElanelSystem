from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import CRUDPlanes
 
app_name="products"

urlpatterns = [
    path("planes/",CRUDPlanes.as_view(),name="planes")
]