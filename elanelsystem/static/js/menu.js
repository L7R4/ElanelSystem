let path_name = window.location.pathname;
const list_menu = document.querySelectorAll(".list > li > a");
const button_menu = document.querySelector(".toggle-button")
const menu = document.getElementById("menu")

if (path_name.includes("resumen")) {
    ClearClass()
    resumen.classList.add("in_path")
}else if(path_name.includes("clientes")){
    ClearClass()
    clientes.classList.add("in_path")
}else if(path_name.includes("ventas")){
    ClearClass()
    ventas.classList.add("in_path")
}else if(path_name.includes("caja")){
    ClearClass()
    caja.classList.add("in_path")
}else if(path_name.includes("estados")){
    ClearClass()
    estados.classList.add("in_path")
}else if(path_name.includes("colaboradores")){
    ClearClass()
    colaboradores.classList.add("in_path")
}else if(path_name.includes("/usuario/crear_usuario/")){
    ClearClass()
    add_user.classList.add("in_path")
}else if(path_name.includes("usuario")){
    ClearClass()
    usuarios.classList.add("in_path")
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

