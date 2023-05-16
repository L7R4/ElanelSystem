from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import CrearUsuario,ListaUsers,ListaClientes
 
app_name="users"

urlpatterns = [
    path("usuario/crear_usuario/",CrearUsuario.as_view(),name="create_user"),
    path("usuario/lista_usuarios/",ListaUsers.as_view(),name="list_users"),
    path("usuario/lista_clientes/",ListaClientes.as_view(),name="list_customers"),
]