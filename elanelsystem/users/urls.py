from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *
from sales.views import CrearUsuarioYCambiarTitu
 
app_name="users"

urlpatterns = [
    path("usuario/crear_usuario/",CrearUsuario.as_view(),name="create_user"),
    path("usuario/lista_usuarios/",ListaUsers.as_view(),name="list_users"),
    path("usuario/detalleusuario/<int:pk>/",DetailUser.as_view(),name="detailUser"),
    path("cliente/lista_clientes/",ListaClientes.as_view(),name="list_customers"),
    path("usuario/administracion/requestusuarios/",requestUsuarios,name="requestUsuarios"),
    path("usuario/administracion/requestusuarios_acargo/",requestUsuariosAcargo,name="requestUsuarios_acargo"),
    path("cliente/crear_cliente/",CrearCliente.as_view(),name="create_customer"),
    path("cliente/<int:pk>/operaciones/",CuentaUser.as_view(),name="cuentaUser"),
    path("crearclienteycambiar/<int:pk>/",CrearUsuarioYCambiarTitu.as_view(),name="crearYCambiar"),
    path("usuario/administracion/",PanelAdmin.as_view(),name="panelAdmin"),
    path("usuario/administracion/permisos/",PanelPermisos.as_view(),name="panelPermisos"),

    #region Sucursal CRUD - - - - - - - -
    path("usuario/administracion/sucursales/",PanelSucursales.as_view(),name="panelSucursales"),
    path("usuario/administracion/sucursales/add",addSucursal,name="addSucursal"),
    path("usuario/administracion/sucursales/remove",removeSucursal,name="removeSucursal"),
    path("usuario/administracion/sucursales/update",updateSucursal,name="updateSucursal"),
    #endregion - - - - - - - - - - - - - - 

    #region Permisos - - - - - - -  - - - - - - - - - - - -
    path("usuario/administracion/requestpermisos/",requestPermisosDeGrupo,name="requestPermisos"),
    path("usuario/administracion/updatepermisos/",updatePermisosAGrupo,name="updatePermisos"),
    path("usuario/administracion/createnewgroup/",createNewGroup,name="newGroup"),
    path("usuario/administracion/deletenewgroup/",deleteGrupo,name="deleteGroup"),
    #endregion  - - - - - - - - - - - - - - - - - - - - - - - -

    path("usuario/pdf/ficha_creacion/<int:pk>",viewsPDFNewUser,name="newUserPDF"),

]