const queryParams = {}; // Variable para almacenar los valores de los inputs

// Generar los elementos `<li>` en el dropdown
function generarLiOptions(input, data) {
    let [campo, tipoDeObjeto] = input.name.split('_'); // Desestructurar nombre del input
    queryParams[campo] = input.value; // Actualizar queryParams

    const dropdown = input.parentElement.querySelector(`.list-selectSearch-custom`);
    dropdown.innerHTML = ''; // Limpiar dropdown
    dropdown.style.display = 'block'; // Mostrar dropdown

    if (data.length === 0) {
        const li = document.createElement('li');
        li.textContent = 'Sin resultados';
        li.classList.add('no-results');
        dropdown.appendChild(li);
    } else {
        data.forEach(option => {
            const li = document.createElement('li');
            li.textContent = option.nombre; // Mostrar el campo nombre del JSON recibido
            li.addEventListener('click', () => {
                input.value = option.nombre; // Seleccionar valor
                queryParams[campo] = option.nombre; // Actualizar queryParams con la selección
                dropdown.style.display = 'none'; // Ocultar dropdown
            });
            dropdown.appendChild(li);
        });
    }
}

// Realizar la búsqueda y actualizar el dropdown
function searchElement(url, input) {
    let [campo] = input.name.split('_'); // Obtener el campo del input
    queryParams[campo] = input.value.trim(); // Actualizar queryParams con el valor actual del input

    // Si el input está vacío, limpiar parámetros y enviar solicitud sin filtros
    if (!input.value.trim()) {
        delete queryParams[campo]; // Eliminar del objeto queryParams si está vacío
    }

    // Generar la URL con parámetros si hay valores en queryParams
    const fullUrl = Object.keys(queryParams).length > 0
        ? `${url}?${new URLSearchParams(queryParams)}`
        : url;

    fetch(fullUrl)
        .then(response => {
            if (!response.ok) throw new Error('Error en la solicitud');
            return response.json();
        })
        .then(data => {
            generarLiOptions(input, data);
        })
        .catch(err => {
            console.error('Error fetching options:', err);
        });
}

