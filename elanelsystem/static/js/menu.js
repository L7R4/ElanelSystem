let path_name = window.location.pathname;
const list_menu = document.querySelectorAll(".list > li > a");
const button_menu = document.querySelector(".toggle-button")
const menu = document.getElementById("menu")

if (path_name.includes("resumen")) {
    ClearClass()
    resumen.parentElement.classList.add("in_path")
}else if(path_name.includes("cliente")){
    ClearClass()
    clientes.parentElement.classList.add("in_path")
}else if(path_name.includes("detalle_venta")){
    ClearClass()
    clientes.parentElement.classList.add("in_path")

}else if(path_name.includes("caja")){
    ClearClass()
    caja.parentElement.classList.add("in_path")

}else if(path_name.includes("colaboradores")){
    ClearClass()
    colaboradores.parentElement.classList.add("in_path")
}else if(path_name.includes("/usuario/crear_usuario/")){
    ClearClass()
    add_user.parentElement.classList.add("in_path")
}else if(path_name.includes("usuario")){
    ClearClass()
    usuarios.parentElement.classList.add("in_path")
}
else if(path_name.includes("planes")){
    ClearClass()
    planes.parentElement.classList.add("in_path")
}

button_menu.addEventListener("click", ()=>{
    menu.classList.toggle("active")
    if (!menu.classList.contains("active")) {
        list_menu.forEach(element => {
            element.children[1].style.display = "none"
        })
    }else if(menu.classList.contains("active")){
        list_menu.forEach(element => {
            element.children[1].style.display = "block"
        }) 
    }
    
})

function ClearClass() {
    list_menu.forEach(element => {
        element.classList.remove("in_path")
    });
}

