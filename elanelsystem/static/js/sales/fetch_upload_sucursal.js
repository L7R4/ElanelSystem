
document.addEventListener('DOMContentLoaded', () => {
    loadInitsInputsHora_libreria()
})
//#region Crear una nueva sucursal  - - - - - - - - - - - - - - - - - - - - - -
function createNewItemSucursal_HTML(csrf, pk, name, direccion, hora, gerente) {
    let buttons = buttonEditSucursal()
    let uniqueHoraId = 'inputHora' + Date.now();

    let stringForHTML =
        `
        <div class="sucursalItem" id="s_${pk}">
            <h2>${name}</h2>
            <form method="POST" class="formSucursal">
                ${csrf}
                <input type="hidden" class="input-id" name="inputID" value="${pk}">

                <div class="containerInputs">
                    <div class="wrapperInput">
                        <label for="">Dirección</label>
                        <input type="text" class="input-direccion" name="inputDireccion" value="${direccion}">
                    </div>
                    <div class="wrapperInput hora">
                        <label for="">Hora de entrada</label>
                        <input type="text" class="input-hora" name="inputHora" id="${uniqueHoraId}" value="${hora}">
                    </div>
                     <div id="selectWrapperSelectGerente" class="wrapperSelectFilter wrapperInput">
                        <label class="labelInput">Gerente</label>
                        <div class="containerInputAndOptions">
                        <img id="sucursalIconDisplay" class="iconDesplegar" src="${imgArrowDown}" alt="">
                        <input type="hidden" value="${gerente.id}" name="gerente" required="" autocomplete="off" maxlength="100" class="input-gerente">
                            <div class="onlySelect pseudo-input-select-wrapper">
                                <h3>${gerente.nombre}</h3>
                            </div>
                            <ul class="list-select-custom options">
                            ${gerentesDisponibles.map(gerente => `<li data-value="${gerente.id}">${gerente.nombre}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>

                ${buttons}
            </form>
        </div>
    `
    wrapperListSucursales.insertAdjacentHTML('beforeend', stringForHTML);

    // Inicializar los listeners de los custom-selects
    initSelect(document.querySelector(`#s_${pk} .pseudo-input-select-wrapper`))

    initSelectHora(document.getElementById(`${uniqueHoraId}`))


}

// Para confirmar la creacion de la sucursal
function confirmCreateAgencia() {
    const form = document.getElementById("addSucursalForm")
    const modal = new tingle.modal({
        footer: true,
        closeMethods: ['button', 'overlay'],
        cssClass: ['modalConfirmacion'],

        onClose: function () {
            modal.destroy();
        },
    });

    // Contenido del modal
    modal.setContent("<h2>¿Estás seguro de que deseas crear esta sucursal?</h2>");

    // Botón de confirmación
    modal.addFooterBtn("Confirmar", "tingle-btn tingle-btn--primary add-button-default", async function () {

        let body = {
            "provincia": form.querySelector(".input-provincia").value,
            "localidad": form.querySelector(".input-localidad").value,
            "gerente": form.querySelector(".input-gerente").value,
            "direccion": form.querySelector(".input-direccion").value,
            "horaApertura": form.querySelector(".input-hora").value,
        }
        showLoader()
        let response = await fetchCRUD(body, urlAddS)
        hiddenLoader()


        if (response.status) {
            document.querySelector(".sucursalItem.new").remove()
            createNewItemSucursal_HTML(CSRF_TOKEN, response["pk"], response["name"], response["direccion"], response["hora"], response["gerente"]);

        }
        showReponseModal(response.message, response.iconMessage)
        modal.close();
    });

    // Botón de cancelación
    modal.addFooterBtn("Cancelar", "tingle-btn tingle-btn--default button-default-style", function () {
        modal.close();
    });

    // Abre el modal
    modal.open();
}


// Para cerrar el formulario de creacion de nueva agencia
function closeFormNewAgencia() {
    if (document.getElementById("addSucursalForm")) {
        document.querySelector(".sucursalItem.new").remove()
    }
}
//#endregion  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

// Para eliminar una sucursal - - - - - - - - - - - -
function deleteAgencia(buttonDelete) {
    let agenciaWrapperClicked = buttonDelete.parentElement.parentElement.parentElement

    const modal = new tingle.modal({
        footer: true,
        closeMethods: ['button', 'overlay'],
        cssClass: ['modalConfirmacion'],

        onClose: function () {
            modal.destroy();
        },
    });

    // Contenido del modal
    modal.setContent("<h2>¿Estás seguro de que deseas eliminar esta sucursal?</h2>");

    // Botón de confirmación
    modal.addFooterBtn("Eliminar", "tingle-btn tingle-btn--danger delete-button-default", async function () {
        const form = agenciaWrapperClicked.querySelector(".formSucursal");
        let pk = form.querySelector(".input-id").value
        let body = {
            "pk": pk
        }

        showLoader()
        let response = await fetchCRUD(body, urlRemoveS)
        hiddenLoader()

        if (response.status) {
            agenciaWrapperClicked.remove()
            // MOdal de exito de eliminacion
        } else {
            // Modal de fracaso de eliminacion
        }
        showReponseModal(response.message, response.iconMessage)

        modal.close();
    });

    // Botón de cancelación
    modal.addFooterBtn("Cancelar", "tingle-btn tingle-btn--default button-default-style", function () {
        modal.close();
    });

    // Abre el modal
    modal.open();
}

// Para deshabilitar el modo edicion de la sucursal
function desableForm(button) {
    let agenciaWrapperClicked = button.parentElement.parentElement.parentElement
    agenciaWrapperClicked.classList.remove("enable")
    bloquear_desbloquear_Inputs(agenciaWrapperClicked)

    let buttons = buttonEditSucursal()
    agenciaWrapperClicked.querySelector(".buttonsActions").remove()
    let formulario = agenciaWrapperClicked.querySelector(".formSucursal")
    formulario.insertAdjacentHTML('beforeend', buttons);
}

// Para habilitar el modo edicion de la sucursal
function editarSucursal(button) {
    let agenciaWrapperClicked = button.parentElement.parentElement.parentElement
    agenciaWrapperClicked.classList.add("enable")
    bloquear_desbloquear_Inputs(agenciaWrapperClicked)

    let buttons = buttonConfirmSucursal(true)
    agenciaWrapperClicked.querySelector(".buttonsActions").remove()
    let formulario = agenciaWrapperClicked.querySelector(".formSucursal")
    formulario.insertAdjacentHTML('beforeend', buttons);

}

// Para confirmar la edicion de la sucursal
function confirmEditAgencia(button) {
    let agenciaWrapperClicked = button.parentElement.parentElement.parentElement

    const modal = new tingle.modal({
        footer: true,
        closeMethods: ['button', 'overlay'],
        cssClass: ['modalConfirmacion'],

        onClose: function () {
            modal.destroy();
        },
    });

    // Contenido del modal
    modal.setContent("<h2>¿Estás seguro de que deseas editar esta sucursal?</h2>");

    // Botón de confirmación
    modal.addFooterBtn("Confirmar", "tingle-btn tingle-btn--primary add-button-default", async function () {
        const form = agenciaWrapperClicked.querySelector(".formSucursal");
        let body = {
            "sucursalPk": form.querySelector(".input-id").value,
            "direccion": form.querySelector(".input-direccion").value,
            "horaApertura": form.querySelector(".input-hora").value,
            "gerente": form.querySelector(".input-gerente").value  // o similar
        }

        console.log(body)

        showLoader()
        let response = await fetchCRUD(body, urlUpdateS)
        hiddenLoader()

        agenciaWrapperClicked.classList.remove("enable")
        bloquear_desbloquear_Inputs(agenciaWrapperClicked)

        showReponseModal(response.message, response.iconMessage)
        modal.close();
    });

    // Botón de cancelación
    modal.addFooterBtn("Cancelar", "tingle-btn tingle-btn--default button-default-style", function () {
        agenciaWrapperClicked.classList.remove("enable")
        bloquear_desbloquear_Inputs(agenciaWrapperClicked)
        modal.close();
    });

    let buttons = buttonEditSucursal()
    agenciaWrapperClicked.querySelector(".buttonsActions").remove()
    let formulario = agenciaWrapperClicked.querySelector(".formSucursal")
    formulario.insertAdjacentHTML('beforeend', buttons);

    // Abre el modal
    modal.open();
}



// DOM Botones para el estado de "Vista" de la sucursal
function buttonEditSucursal() {
    return `<div class="buttonsActions">
                <button type="button" onclick="editarSucursal(this)" class="enableForm add-button-default">Editar</button>
                <button type="button" onclick="deleteAgencia(this)" class="deleteSucursal delete-button-default" >Eliminar</button>
            </div>`
}

// DOM Botones para el estado de "Edicion o creacion" de la sucursal
function buttonConfirmSucursal(edit) {
    if (edit) {
        return `<div class="buttonsActions">
                    <button type="button" onclick="confirmEditAgencia(this)" class="uploadForm add-button-default">Confirmar</button>
                    <button type="button" onclick="desableForm(this)" class="desableForm button-default-style">Cancelar</button>
                </div>`
    } else {
        return `<div class="buttonsActions">
                    <button type="button" onclick="confirmCreateAgencia()" class="uploadForm add-button-default">Confirmar</button>
                    <button type="button" onclick="closeFormNewAgencia()"class="desableForm button-default-style">Cancelar</button>
                </div>`
    }
}

// DOM Para crear el formulario para la creacion de una nueva sucursal
function newSucursalForm_HTML() {
    let buttons = buttonConfirmSucursal(false)
    // Genera un id único para el input de hora
    let uniqueHoraId = 'newHora_' + Date.now();

    let stringForHTML = `
    <div class="sucursalItem new">
        <form method="POST" id="addSucursalForm">
        ${CSRF_TOKEN}
        <div class="containerInputs">
            <div class="wrapperInputNew">
                <label for="">Provincia</label>
                <input type="text" class="open input-provincia" name="provincia" id="provincia">
            </div>
            <div class="wrapperInputNew">
                <label for="">Localidad</label>
                <input type="text" class="open input-localidad" name="localidad" id="localidad">
            </div>
            <div class="wrapperInputNew">
                <label for="">Dirección</label>
                <input type="text" class="open input-direccion" id="newDireccion" name="direccion">
            </div>
            <div class="wrapperInputNew hora">
                <label for="">Hora de apertura</label>
                <input type="text" class="open input-hora" placeholder="Seleccionar" readonly id="${uniqueHoraId}" name="horaApertura">
            </div>
            
            <div id="selectWrapperSelectGerente" class="wrapperSelectFilter wrapperInputNew">
                <label class="labelInput">Gerente</label>
                <div class="containerInputAndOptions">
                   <img id="sucursalIconDisplay" class="iconDesplegar" src="${imgArrowDown}" alt="">
                   <input type="hidden" name="gerente" placeholder="Seleccionar" required="" autocomplete="off" maxlength="100" class="input-gerente">
                    <div class="onlySelect pseudo-input-select-wrapper">
                        <h3></h3>
                    </div>
                    <ul class="list-select-custom options">
                    ${gerentesDisponibles.map(gerente => `<li data-value="${gerente.id}">${gerente.nombre}</li>`).join('')}
                    </ul>
                </div>
            </div>
        </div>
        ${buttons}
        </form>
    </div> `
    wrapperListSucursales.insertAdjacentHTML('beforeend', stringForHTML);

    initSelect(document.querySelector(`#addSucursalForm .pseudo-input-select-wrapper`))

    // Inicializar el evento para la seleccion de la hora
    initSelectHora(document.getElementById(`${uniqueHoraId}`))

}

// Funcion para manejar la habilitacion de los inputs
function bloquear_desbloquear_Inputs(agenciaWrapperDOM) {
    if (agenciaWrapperDOM.classList.contains("enable")) {

        agenciaWrapperDOM.querySelectorAll(".containerInputs input").forEach(element => {
            element.classList.add("open")
        });
        agenciaWrapperDOM.querySelectorAll(".pseudo-input-select-wrapper").forEach(element => {
            element.classList.add("open")
        });

    } else {
        agenciaWrapperDOM.querySelectorAll(".containerInputs input").forEach(element => {
            element.classList.remove("open")
        });
        agenciaWrapperDOM.querySelectorAll(".pseudo-input-select-wrapper").forEach(element => {
            element.classList.remove("open")
        });
    }
}

//#region FUNCTION FETCH - - - - - - - - - 
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
                "Content-Type": "application/json",
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
//#endregion - - - - - - - - - - - - - - - - -


function showReponseModal(contenido, icon) {
    const modal = new tingle.modal({
        footer: true,
        closeMethods: ['button', 'overlay'],
        cssClass: ['modalResponse'],
        onClose: () => modal.destroy()
    });

    modal.setContent(`<div class="messageReponseModal">
            <img src="${icon}"/>
            <h2>${contenido}</h2>
        </div>`);

    // modal.addFooterBtn(btnConfirmText, "tingle-btn tingle-btn--danger", async function () {
    //     modal.close();
    // });

    modal.addFooterBtn("Cerrar", "tingle-btn tingle-btn--default button-default-style", function () {
        modal.close();
    });

    modal.open();
}

//#region Manejar el display del loader
function showLoader() {
    document.querySelector('.modalConfirmacion').children[0].style.display = "none";
    document.getElementById('wrapperLoader').style.display = 'flex';

}

function hiddenLoader() {
    document.getElementById('wrapperLoader').style.display = 'none';
}
//#endregion

function loadInitsInputsHora_libreria() {
    const inputsHora = document.querySelectorAll(".wrapperInput.hora > input")
    console.log(inputsHora)

    inputsHora.forEach((input, index) => {
        let uniqueHoraId = `inputHora_${index}`;
        input.id = uniqueHoraId
        initSelectHora(document.getElementById(`${input.id}`))
    });
}