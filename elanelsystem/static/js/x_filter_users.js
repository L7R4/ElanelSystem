//#region Funcion del formulario FETCH
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

async function formFETCH(form, url) {
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
            },
            body: JSON.stringify(form)
        })
        if (!res.ok) {
            throw new Error("Error")
        }
        const data = await res.json()
        return data;
    } catch (error) {
    }
}
//#endregion  

const url = window.location.pathname
const formFilter = document.getElementById('formFilter');
const inputsFormFilter = formFilter.querySelectorAll('input:not([name="csrfmiddlewaretoken"])');
const tableInformation = document.querySelector('table.information > .values');
const buttonCleanFilter = document.getElementById("buttonCleanFilter")

// Funcion para crear el boton de filtrar en caso de que no exista
function createFilterButton() {
    // Obtener todos los inputs del formulario, excluyendo el CSRF token
    const inputs = Array.from(inputsFormFilter)
  
    // Verificar si todos los inputs tienen valores diferentes a ""
    const allFilled = inputs.some(input => input.value.trim() !== "");
  
    if (allFilled && !document.getElementById('submitFilter')) {
      const buttonHTML = `<button type="button" id="submitFilter" class="add-button-default">Filtrar</button>`;
      formFilter.insertAdjacentHTML('beforeend', buttonHTML);
      document.getElementById('submitFilter').addEventListener('click', submitFilter);
    } 
    else if (!allFilled && document.getElementById('submitFilter')) {
      // Remover el botón si ya existe y los inputs están vacíos
      document.getElementById('submitFilter').remove();
    }
}
  

// Funcion para añadir nuevamente el evento click a las filas y poder rediccionar al dar click.
function addRowClickEvent() {
    document.querySelectorAll('.customer_item').forEach(row => {
      row.addEventListener('click', function() {
        window.location.href = row.getAttribute('data-url');
      });
    });
}


async function submitFilter() {
    const formData = {
      sucursal: document.getElementById('sucursalInput').value,
      search: document.getElementById('user_search').value,
    };

    let response = await formFETCH(formData, url)
    tableInformation.innerHTML = '';
    response["users"].forEach(user => {
        const sucursales = user.sucursales.map(s => `${s}`).join('');
        tableInformation.innerHTML += `
          <tr class="user_item" data-url="${user.url}">
            <td class="nombreUser">${user.nombre}</td>
            <td><p>${user.dni}</p></td>
            <td class="emailUser">${user.email}</td>
            <td><p>${sucursales}</p></td>
            <td><p>${user.tel}</p></td>
            <td><p>${user.rango}</p></td>
          </tr>
        `;
    });
    addRowClickEvent();

    let usuarios = document.querySelectorAll(".information > .values > .user_item") 
    contextMenuManagement(usuarios); // Vuelvo a reasignar los listener para aplicar los descuentos/premios

    buttonCleanFilter.classList.add("active") // Al presionar el boton filtrar aparece el boton de limpiar filtros
}

// Evento de "input" para mostrar botón "Filtrar" dinámicamente
inputsFormFilter.forEach(input => {
    input.addEventListener('input', createFilterButton);
});


// Quita el boton de limpiar filtros cuando se da click
buttonCleanFilter.addEventListener("click",()=>{
    buttonCleanFilter.classList.remove("active")
})

