function menuConceptual_click_derecho(item) {
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
            let stringForHTML = `<div id="contextMenu" style="left: ${positionX}; top: ${positionY};"><div class="option"><img src="${urlImageDelete}" alt=""><h5>Eliminar grupo: ${item.textContent}</h5></div></div>`
        
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
                    let htmlConfirmarDelete = `
                    <div id="confirmarDelete">
                        <h5>Autorizado por:</h5>
                        <input type="text" class="input-read-write-default" name="autorizacion_input" required id="id_autorizacion_input">

                        <div>
                            <button id="confirmEdit" type="button">Guardar</button>
                            <button id="notConfirmEdit" type="button">Cancelar</button>
                        </div>
                    </div>`
                    contextMenu.children[0].classList.add("blocked")
                    contextMenu.insertAdjacentHTML('beforeend', htmlConfirmarDelete);

                    confirmDelete.addEventListener("click",()=>{
                        id_autorizado_por.value = id_autorizacion_input.value 
                    })

                    notConfirmEdit.addEventListener("click",()=>{
                        // No elimnar el grupo y cerrar el context menu
                        contextMenu.remove();
                    })
                });
            })
        })
}