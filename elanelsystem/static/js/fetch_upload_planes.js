const urlNewPlan = window.location.pathname

function actualizarPanel(plan) {
    const panel = document.getElementById(`panel`);
    const table = panel.querySelector("table > tbody ");
    let row = `
        <tr>
            <td class="valorPlan">$${plan.precio}</td>
            <td>${plan.paquete}</td>
            <td>${plan.suscripcion}</td>
            <td>${plan.primer_cuota}</td>
            <td>${plan.p_24}</td>
            <td>${plan.p_30}</td>
            <td>${plan.p_48}</td>
            <td>${plan.p_60}</td>
            <td class="button_cell">
                <button class="buttonDeleteItem" type="button">   
                    <img src="${iconDelete}" alt="">
                </button>
            </td>
        </tr>`;

    table.insertAdjacentHTML("afterbegin", row);

    // Seleccionar la última fila recién añadida y pasarla a `loadListenerDelete`
    const lastRow = table.firstElementChild;
    loadListenerDelete(lastRow)
}


function agregarFormularioNuevoPlan() {
    const panel = document.getElementById(`panel`);
    const table = panel.querySelector("table > tbody");

    if (!document.querySelector("#rowNewFormPlan")) {
        let row = `
            <tr id="rowNewFormPlan">
                <td>
                    <input name="precio" class="input-read-write-default" type="number" placeholder="Valor nominal" id="precio_input" />
                </td>
                <td>
                    <div class="containerInputAndOptions">
                        <img id="tipoComprobanteIconDisplay"class="iconDesplegar" src="${logoDisplayMore}" alt="">
                        <input type="text" readonly name="paquete" placeholder="Paquete" id="id_paquete" required autocomplete="off" maxlength="30" class="input-select-custom onlySelect">
                        <ul class="list-select-custom options">
                            <li>Basico</li>
                            <li>Estandar</li>  
                            <li>Premium</li>  
                        </ul>
                    </div>
                </td>
                <td>
                    <input name="suscripcion" class="input-read-write-default" type="number" placeholder="Suscripcion" id="suscripcion_input" />
                </td>
                <td>
                    <input name="primer_cuota" class="input-read-write-default" type="number" placeholder="Primer cuota" id="primer_cuota_input" />
                </td>
                <td>
                    <input name="p_24" class="input-read-write-default" type="number" placeholder="% 24 Cuota" id="p_24_input" />
                </td>
                <td>
                    <input name="p_30" class="input-read-write-default" type="number" placeholder="% 30 Cuota" id="p_30_input" />
                </td>
                <td>
                    <input name="p_48" class="input-read-write-default" type="number" placeholder="% 48 Cuota" id="p_48_input" />
                </td>
                <td>
                    <input name="p_60" class="input-read-write-default" type="number" placeholder="% 60 Cuota" id="p_60_input" />
                </td>
            </tr>
            `;
        cancelarNuevoProducto()
        submitButton()
        table.insertAdjacentHTML("beforeend", row);
        cargarListenersEnInputs()
    }
}


async function guardarPlan() {
    const precio = document.getElementById(`precio_input`).value;
    const paquete = document.getElementById(`id_paquete`).value;
    const suscripcion = document.getElementById(`suscripcion_input`).value;
    const primer_cuota = document.getElementById(`primer_cuota_input`).value;
    const p_24 = document.getElementById(`p_24_input`).value;
    const p_30 = document.getElementById(`p_30_input`).value;
    const p_48 = document.getElementById(`p_48_input`).value;
    const p_60 = document.getElementById(`p_60_input`).value;

    let form = {
        "paquete": paquete,
        "suscripcion": suscripcion,
        "precio": precio,
        "primer_cuota": primer_cuota,
        "p_24": p_24,
        "p_30": p_30,
        "p_48": p_48,
        "p_60": p_60,
    }

    let response = await fetchCRUD(form, urlNewPlan)

    if (response["success"]) {
        actualizarPanel(response["plan"])
        rowNewFormPlan.remove() // limpiamos el formulario activo
        cancelarNuevoPlanButton.remove() //Eliminamos el boton de cancelar
        submitButtonPlan.remove() // Eliminamos el boton de submit del form
        agregarButtonAgregarPlan()

    } else {
        console.log(response["message"])
        // Realizar modal para notificar que algo fallo
    }
}


function cancelarNuevoProducto() {
    const buttonCancelar = `<button class="button-default-style" type="button" id="cancelarNuevoPlanButton">Cancelar</button>`

    const panel = document.getElementById(`panel`);
    const wrapperButtonOfTable = panel.querySelector(".buttonsActions");

    wrapperButtonOfTable.insertAdjacentHTML("beforeend", buttonCancelar);
    wrapperButtonOfTable.querySelector("#agregarNuevoPlanButton").remove() //Eliminamos el boton de agregar plan

    if (document.querySelector("#cancelarNuevoPlanButton")) {
        cancelarNuevoPlanButton.addEventListener("click", () => {
            rowNewFormPlan.remove() // limpiamos el formulario activo
            cancelarNuevoPlanButton.remove() //Eliminamos el boton de cancelar
            submitButtonPlan.remove() //Eliminamos el boton del submit del form
            agregarButtonAgregarPlan()
        })
    }
}


function agregarButtonAgregarPlan() {
    const panel = document.getElementById(`panel`);
    const wrapperButtonOfTable = panel.querySelector(".buttonsActions");
    if (!wrapperButtonOfTable.querySelector("#agregarNuevoPlanButton")) {
        const buttonAgregar = `<button class="add-button-default" id="agregarNuevoPlanButton" type="button" onclick="agregarFormularioNuevoPlan()">Agregar plan</button>`
        wrapperButtonOfTable.insertAdjacentHTML("beforeend", buttonAgregar); //Agregamos nuevamente el boton de agregar plan
    }
}


function submitButton() {
    const panel = document.getElementById(`panel`);
    const wrapperButtonOfTable = panel.querySelector(".buttonsActions");
    if (!wrapperButtonOfTable.querySelector("#submitButtonPlan")) {
        const buttonSubmit = `<button id="submitButtonPlan" class="add-button-default" type="button" onclick="guardarPlan()">Guardar plan</button>`
        wrapperButtonOfTable.insertAdjacentHTML("beforeend", buttonSubmit); //Agregamos nuevamente el boton de agregar plan
    }
}

// #region Codigo para la eliminacion de un producto

const filas = document.querySelectorAll("table > tbody > tr");
console.log(filas)
filas.forEach(fila => {
    loadListenerDelete(fila)
});

// Función para mostrar el modal de confirmación
function mostrarModalConfirmacionParaEliminar(fila) {
    const modal = new tingle.modal({
        footer: true,
        closeMethods: ['button', 'overlay'],
        cssClass: ['modalConfirmacion'],

        onClose: function () {
            modal.destroy();
        },
    });

    // Contenido del modal
    modal.setContent("<h2>¿Estás seguro de que deseas eliminar este plan?</h2>");

    // Botón de confirmación
    modal.addFooterBtn("Eliminar", "tingle-btn tingle-btn--danger", async function () {
        // Aquí llamamos a la función de eliminación, pasando la fila correspondiente
        eliminarPlan(fila);
        modal.close();
    });

    // Botón de cancelación
    modal.addFooterBtn("Cancelar", "tingle-btn tingle-btn--default", function () {
        modal.close();
    });

    // Abre el modal
    modal.open();
}


// Funcion para cargar los listener del boton de eliminar para la fila
function loadListenerDelete(fila) {
    let button = fila.querySelector(".buttonDeleteItem")

    // Mostrar el botón al pasar el mouse por encima
    fila.addEventListener("mouseover", () => {
        button.style.display = "inline";
    });

    // Ocultar el botón al salir con el mouse
    fila.addEventListener("mouseout", () => {
        button.style.display = "none";
    });

    // Evento para abrir el modal de confirmación al hacer clic en "Eliminar"
    button.addEventListener("click", () => {
        mostrarModalConfirmacionParaEliminar(fila); // Pasamos la fila actual para su posible eliminación
    });
}

// Función para eliminar el plan
async function eliminarPlan(fila) {
    const valorPlan = fila.querySelector("td.valorPlan").textContent.slice(1);

    let form = {
        "valor": valorPlan,
    };

    // Realizar la solicitud al backend para eliminar el producto
    showLoader()
    let response = await fetchCRUD(form, urlDeleteP);
    if (response["status"]) {
        hiddenLoader()
        fila.remove(); // Eliminar la fila de la tabla en caso de éxito
    } else {
        hiddenLoader()
        console.log("Error al eliminar el plan.");
    }
}

//#endregion


//#region Manejar el display del loader
function showLoader() {
    document.getElementById('wrapperLoader').style.display = 'flex';
}

function hiddenLoader() {
    document.getElementById('wrapperLoader').style.display = 'none';
}
//#endregion


// #region FUNCTION FETCH - - - - - - - - - 
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


async function fetchCRUD(body, url) {
    try {
        let response = await fetch(url, {
            method: "POST",
            body: JSON.stringify(body),
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
            }
        })
        if (!response.ok) {
            throw new Error("Error")
        }
        const data = await response.json();
        return data;
    } catch (error) {
    }
}
// #endregion - - - - - - - - - - - - - - - - -
