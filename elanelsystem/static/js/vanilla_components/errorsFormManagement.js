function mostrarErrores(errores, formulario) {
    // Limpiar los mensajes de error anteriores
    let messagesError = document.querySelectorAll('.message-error');
    messagesError.forEach(mensaje => mensaje.remove());

    // Recorrer el objeto de errores
    for (let [name, mensaje] of Object.entries(errores)) {
        // Buscar el input correspondiente por su atributo name
        const input = formulario.querySelector(`input[name="${name}"]`);
        if (input) {
            // Crear una etiqueta p para el mensaje de error
            const p = document.createElement('p');
            p.textContent = mensaje;
            p.classList.add('message-error'); // Clase para estilos

            // Insertar la etiqueta p después del input
            input.insertAdjacentElement('afterend', p);
        }
    }
}
