let itemsGrupo = document.querySelectorAll("#itemsGrupos > ul > li")
let itemsPermisos = document.querySelectorAll("#itemsPermisos > ul > input")
let itemsPermisosLabels = document.querySelectorAll("#itemsPermisos > ul > label")
let sendUpdatePermisos = document.getElementById("updatePermisosGrupo")
let groupToChange;
let backgroundPermission = document.querySelector(".backgroundPermission")
const formUpdatePermisos = document.getElementById("updatePermisos")

// FUNCTION FETCH - - - - - - - - - 
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
async function fetchCRUD(body,url) {
    try{
        let response = await fetch(url,{
            method: "POST",
            body: JSON.stringify(body),
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
            }
        })
        if(!response.ok){
            throw new Error("Error")
        }
        const data = await response.json();
        return data;
    }catch(error){
    }
}
// - - - - - - - - - - - - - - - - -

// Solicitar los permisos de acuerdo al grupo seleccionado
async function permisosGet(group) {
    const response = await fetch(`/usuario/administracion/requestpermisos/?group=${group}`, {
        method: 'get',
        headers: {'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'},
        cache: 'no-store',
    });
    const data = await response.json();
    return data;
}


//  - - - - - - -  - - - - 
itemsGrupo.forEach(item => {
    selectGroupListener(item);
})

function selectGroupListener(grupo) {
    grupo.addEventListener("click", async()=>{
        if (grupo.classList.contains("itemPicked")){
            clearActiveOfGroups()
            backgroundPermission.classList.remove("active")
            formUpdatePermisos.style.pointerEvents ="none"
            sendUpdatePermisos.classList.remove("enabled")
        }
        else{
            clearActiveOfGroups()
            grupo.classList.add("itemPicked")
            let group = grupo.textContent
            groupToChange = group
            let permisosActives = await permisosGet(group);
            Array.from(itemsPermisos).map(e => {
                if(permisosActives["perms"].includes(e.nextElementSibling.textContent)){
                    e.checked = true;
                    e.nextElementSibling.classList.add("perActive")
                }
                else{
                    e.checked = false;
                    e.nextElementSibling.classList.remove("perActive")
                }
            })
            backgroundPermission.classList.add("active")
            formUpdatePermisos.style.pointerEvents ="unset"
            sendUpdatePermisos.classList.add("enabled")
        }
    });
}



// SELECCION DE PERMISOS PARA GRUPOS
itemsPermisos.forEach(element => {
    element.addEventListener("change",()=>{
        element.checked ? element.nextElementSibling.classList.add("perActive") : element.nextElementSibling.classList.remove("perActive");
    })
});



function updatePermisos(grupo) {
    // Obtener todos los checkboxes del formulario
    let checkboxes = document.querySelectorAll('#itemsPermisos > ul > input[type="checkbox"]:checked');
    // Crear un array para almacenar los valores seleccionados
    let permisosSeleccionados = [];

    // Iterar sobre los checkboxes seleccionados y agregar sus valores al array
    checkboxes.forEach(checkbox => {
        permisosSeleccionados.push(checkbox.value);
    });

    let body = {
        "permisos": permisosSeleccionados,
        "grupo": grupo,
    }

    fetchCRUD(body, updatePermisosURL).then(data =>{
        let successMessage = document.querySelector(".wrapperMessageSuccess")
        successMessage.children[0].children[0].textContent = grupo
        successMessage.classList.add("active")
        clearActivePermisos()
        backgroundPermission.classList.remove("active")
        setTimeout(()=>{
            successMessage.classList.remove("active")
        },3000)
    })

}



sendUpdatePermisos.addEventListener("click",()=>{
    updatePermisos(groupToChange);
    sendUpdatePermisos.classList.remove("enabled")
    clearActiveOfGroups()
})

function clearActiveOfGroups() {
    itemsGrupo.forEach(e => e.classList.remove("itemPicked"))
}
function clearActivePermisos() {
    itemsPermisosLabels.forEach(e => e.classList.remove("perActive"))
}


// Menu conceptual al apretar click derecho - - - - - - 
itemsGrupo.forEach(element => {
    menuConceptual_click_derecho(element,urlImageDelete)
});

function menuConceptual_click_derecho(item,urlImageDelete) {
    item.addEventListener('contextmenu', function (e) {
            // Prevenir el menú contextual predeterminado del navegador
            e.preventDefault();
            
            clearActiveOfGroups()
            clearActivePermisos()
            backgroundPermission.classList.remove("active")
            sendUpdatePermisos.classList.remove("enabled")
            
            if(document.getElementById("contextMenu")){
                document.getElementById("contextMenu").remove()
            }

            let positionX = e.clientX + "px"
            let positionY = e.clientY + "px"
            // Crear tu propio menú contextual personalizado
            let stringForHTML = `<div id="contextMenu" style="left: ${positionX}; top: ${positionY};"><div class="option"><img src="${urlImageDelete}" alt=""><h5>Eliminar grupo: ${element.textContent}</h5></div></div>`
        
            // Agregar el menú al cuerpo del documento
            document.body.insertAdjacentHTML('beforeend', stringForHTML);
            let contextMenu = document.getElementById("contextMenu");

    
            // Agregar un event listener para cerrar el menú cuando se haga clic fuera de él
            document.addEventListener('click', function closeContextMenu() {
                contextMenu.remove();
                document.removeEventListener('click', closeContextMenu);
            });
            
            // Detener la propagación del evento click dentro del menú para evitar que se cierre
            contextMenu.addEventListener('click', function (e) {
                e.stopPropagation();
            });
            

            // Puedes agregar aquí los event listeners para los botones dentro del menú
            let contextMenuItems = contextMenu.querySelectorAll(".option")
            contextMenuItems.forEach(e =>{
                e.addEventListener('click', function () {
                    let htmlConfirmarDelete = `<div id="confirmarDelete"><h5>¿Seguro que quieres eliminar este grupo?</h5><div><button id="confirmDelete" type="button">Si</button><button id="notConfirmDelete" type="button">No</button></div></div>`
                    contextMenu.children[0].classList.add("blocked")
                    contextMenu.insertAdjacentHTML('beforeend', htmlConfirmarDelete);

                    confirmDelete.addEventListener("click",()=>{
                        // Elimnar el grupo
                        contextMenu.remove();
                        let grupo = element.textContent
                        let body = {
                            "grupo": grupo
                        }
                        
                        fetchCRUD(body,deleteGrupoURL).then(data=>{
                            element.remove()
                        })
                    })

                    notConfirmDelete.addEventListener("click",()=>{
                        // No elimnar el grupo y cerrar el context menu
                        contextMenu.remove();
                    })
                });
            })
        })
}

//  - - - - - - - - - - - - - - - - - - - - - - - - - -

