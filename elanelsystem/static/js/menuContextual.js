function createContextMenu(htmlContent, element) {
    // Crear el elemento del menú contextual
    const contextMenu = document.createElement('div');
    contextMenu.classList.add('context-menu');


    // Mostrar el menú al hacer clic derecho
    element.addEventListener('contextmenu', function (e) {
        e.preventDefault();
        contextMenu.innerHTML = htmlContent;
        document.body.appendChild(contextMenu);
        contextMenu.style.top = `${e.clientY}px`;
        contextMenu.style.left = `${e.clientX}px`;
        contextMenu.style.display = 'block';
    });

    // Ocultar el menú al hacer clic en cualquier otro lugar
    document.addEventListener('click', function () {
        contextMenu.remove();
    });

    // Evitar que el menú se cierre al hacer clic dentro de él
    contextMenu.addEventListener('click', function (e) {
        e.stopPropagation();
    });
}
