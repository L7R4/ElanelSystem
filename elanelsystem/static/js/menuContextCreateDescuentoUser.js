const usuarios = document.querySelectorAll(".information > .values > .user_item")
var ldcv;
var userSelectedDOM;

document.addEventListener("DOMContentLoaded", function () {
    ldcv = new ldcover({
        root: ".ldcv"
    });
});

function contextMenuManagement(usuarios) {
    usuarios.forEach(usuario => {
        usuario.addEventListener('contextmenu', function (e) {
            e.preventDefault();

            userSelectedDOM = usuario;
            let nombre_usuario = userSelectedDOM.querySelector(".nombreUser").textContent;

            ldcv.toggle();
            updateNameContext(nombre_usuario);
        });
    });
}

function updateNameContext(nombre_usuario) {
    let contextMenu = document.querySelector(".wrapperContextMenuDescuento");
    let nombre = contextMenu.querySelector(".nombreUsuario");
    nombre.textContent = nombre_usuario;
}

contextMenuManagement(usuarios);

