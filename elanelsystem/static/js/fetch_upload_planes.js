const urlNewPlan = window.location.pathname

function actualizarPanel(plan) {
    const panel = document.getElementById(`panel`);
    const table = panel.querySelector("table > tbody ");
    let row = `
        <tr>
            <td>${plan.precio}</td>
            <td>${plan.paquete}</td>
            <td>${plan.suscripcion}</td>
            <td>${plan.primer_cuota}</td>
            <td>${plan.p_24}</td>
            <td>${plan.p_30}</td>
            <td>${plan.p_48}</td>
            <td>${plan.p_60}</td>
        </tr>`;

    table.insertAdjacentHTML("beforeend", row);
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
