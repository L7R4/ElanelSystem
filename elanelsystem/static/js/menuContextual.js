var itemDOMSelected;
function createContextMenu(htmlContent, element) {

    // Mostrar el menú al hacer clic derecho
    element.addEventListener('contextmenu', function (e) {
        e.preventDefault();

        const existingMenu = document.querySelector('.context-menu');
        if (existingMenu) {
            existingMenu.remove();
        }
        itemDOMSelected = element;
        console.log(itemDOMSelected)

        const contextMenu = document.createElement('div');
        contextMenu.classList.add('context-menu');
        contextMenu.innerHTML = htmlContent;
        document.body.appendChild(contextMenu);

        contextMenu.style.top = `${e.clientY}px`;
        contextMenu.style.left = `${e.clientX}px`;
        contextMenu.style.display = 'block';
    });

}
// Evento global para cerrar el menú contextual si se hace clic fuera de él
document.addEventListener('click', function (e) {
    const contextMenu = document.querySelector('.context-menu');

    if (contextMenu && !contextMenu.contains(e.target)) {
        contextMenu.remove();
    }else{
        e.stopPropagation();
    }
});
