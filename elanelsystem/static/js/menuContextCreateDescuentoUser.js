const usuarios = document.querySelectorAll(".information > .values > .user_item") 

function renderMenuContextDescuento(item){
    let nombre = item.querySelector(".nombreUser").textContent

    return `
    <div class="wrapperContextMenuDescuento">
        <h3>Aplicar descuento a ${nombre}</h3>
        <div class="wrapperButton">
            <button type="button" class="add-button-default" onclick ="newModal(this)" id="descuentoButton">Aplicar descuento</button>
            <button type="button" class="add-button-default" onclick ="newModal(this)" id="premioButton">Aplicar premio</button>

        </div>
    </div> 
    `;
}

var itemDOMSelected;

function contextMenuManagement(usuarios){
    usuarios.forEach(usuario => {
        usuario.addEventListener('contextmenu', function (e) {
            e.preventDefault();
    
            const existingMenu = document.querySelector('.context-menu');
            if (existingMenu) {
                existingMenu.remove();
            }
            itemDOMSelected = usuario;
            console.log(itemDOMSelected)
    
            const contextMenu = document.createElement('div');
            contextMenu.classList.add('context-menu');
            contextMenu.innerHTML = renderMenuContextDescuento(itemDOMSelected);
            document.body.appendChild(contextMenu);
    
            contextMenu.style.top = `${e.clientY}px`;
            contextMenu.style.left = `${e.clientX}px`;
            contextMenu.style.display = 'block';
        });
    });

}
contextMenuManagement(usuarios)

// Evento global para cerrar el menú contextual si se hace clic fuera de él
document.addEventListener('click', function (e) {
    const contextMenu = document.querySelector('.context-menu');

    if (contextMenu && !contextMenu.contains(e.target)) {
        contextMenu.remove();
    }else{
        e.stopPropagation();
    }
});


