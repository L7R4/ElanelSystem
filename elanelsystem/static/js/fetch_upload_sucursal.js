let buttonsEnableForms = document.querySelectorAll(".enableForm")
let buttonsDeleteSucursal = document.querySelectorAll(".deleteSucursal")

// SWITCH BUTTONS
function editarSucursal(buttons) {
    buttons.forEach(buttonE => {
        buttonE.addEventListener("click", () => {
            let form = buttonE.offsetParent
            let buttonDesable = form.querySelector(".desableForm")
            let buttonUpload = form.querySelector(".uploadForm")
            let buttonDelete = form.querySelector(".deleteSucursal")
            form.querySelectorAll(".wrapperInput > input").forEach(element => {
                element.classList.add("open")
            });

            buttonE.style.display = "none";
            buttonDelete.style.display = "none";

            buttonDesable.classList.add("active")
            buttonUpload.classList.add("active")

            let buttonsDesableForms = document.querySelectorAll(".desableForm")
            buttonsDesableForms.forEach(buttonD => {
                buttonD.addEventListener("click", () => {
                    form = buttonD.offsetParent

                    form.querySelectorAll(".wrapperInput > input").forEach(element => {
                        element.classList.remove("open")
                    });
                    // buttonUpload = form.querySelector(".uploadForm")
                    let enableForm = form.querySelector(".enableForm")
                    buttonDelete = form.querySelector(".deleteSucursal")

                    if (!form) { return; }

                    buttonD.classList.remove("active")
                    buttonD.previousElementSibling.classList.remove("active")

                    enableForm.style.display = "unset";
                    buttonDelete.style.display = "unset";

                })
            })

            let buttonsUpdateForms = document.querySelectorAll(".uploadForm")
            buttonsUpdateForms.forEach(buttonU => {
                buttonU.addEventListener("click", () => {
                    form = buttonU.offsetParent
                    let enableForm = form.querySelector(".enableForm")
                    buttonDelete = form.querySelector(".deleteSucursal")

                    if (!form) { return; }

                    buttonU.classList.remove("active")
                    buttonU.nextElementSibling.classList.remove("active")

                    enableForm.style.display = "unset";
                    buttonDelete.style.display = "unset";

                    let body = {
                        "sucursalPk": inputID.value,
                        "direccion": inputDireccion.value,
                        "horaApertura": inputHora.value,
                        "gerente": gerenteInput.value
                    }

                    fetchCRUD(body, urlUpdateS).then(data => {
                        form.querySelectorAll(".wrapperInput > input").forEach(element => {
                            element.classList.remove("open")
                        });
                    })

                })
            })
        })
    });
}

editarSucursal(buttonsEnableForms)
removeHTMLSucursal(buttonsDeleteSucursal)

// Para eliminar una sucursal - - - - - - - - - - - -
function removeHTMLSucursal(buttons) {
    buttons.forEach(buttonD => {
        buttonD.addEventListener("click", () => {
            let pk = buttonD.offsetParent.querySelector("#inputID").value
            let body = {
                "pk": pk
            }

            fetchCRUD(body, urlRemoveS).then(data => {
                buttonD.offsetParent.parentElement.remove()
                buttonsEnableForms = document.querySelectorAll(".enableForm")
                editarSucursal(buttonsEnableForms)
            })
        })
    })
}
//  - - - - - - - - - - - - - - - - - - - - - -

// Funciones para manejo de DOM - - - - - - - - - - -
function newSucursal_HTML(csrf) {
    let stringForHTML = `
    <div class="sucursalItem new">
        <form method="POST" id="addSucursalForm">
        ${csrf}
        <div class="containerInputs">
            <div class="wrapperInputNew">
                <label for="">Provincia</label>
                <input type="text" class="open" name="provincia" id="provincia">
            </div>
            <div class="wrapperInputNew">
                <label for="">Localidad</label>
                <input type="text" class="open" name="localidad" id="localidad">
            </div>
            <div class="wrapperInputNew">
                <label for="">Dirección</label>
                <input type="text" class="open" id="newDireccion" name="direccion">
            </div>
            <div class="wrapperInputNew">
                <label for="">Hora de apertura</label>
                <input type="text" class="open" id="newHora" name="horaApertura">
            </div>
            
            <div id="selectWrapperSelectGerente" class="wrapperSelectFilter">
                <label class="labelInput">Gerente</label>
                <div class="containerInputAndOptions">
                   <img id="sucursalIconDisplay" class="iconDesplegar" src="${imgArrowDown}" alt="">
                    <input type="text" readonly="" name="gerente" id="gerenteInput" required="" autocomplete="off" maxlength="100" class="input-select-custom onlySelect">
                    <ul class="list-select-custom options">
                    ${gerentesDisponibles.map(gerente => `<li>${gerente.nombre}</li>`).join('')}
                    </ul>
                </div>
            </div>
        </div>
        <div class="buttonsActions">
            <button type="button" class="add-button-default" id="buttonConfirmAddSucursal">Confirmar</button>
            <button type="button" class="button-default-style" id="buttonStopAddSucursal">Cancelar</button>
        </div>
        </form>
    </div> `
    wrapperListSucursales.insertAdjacentHTML('beforeend', stringForHTML);

}

function cleanAddSucursal() {
    if (document.getElementById("addSucursalForm")) {
        document.querySelector(".sucursalItem.new").remove()
    }
}
//  - - - - - - - - - - - - - - - - - - - - - - 

// Crear una nueva sucursal  - - - - - - - - - - - - - - - - - - - - - -
function createNewItemSucursal_HTML(csrf, pk, name, direccion, hora) {
    let stringForHTML =
        `
        <div class="sucursalItem">
            <h2>${name}</h2>
            <form method="POST" class="formSucursal">
                ${csrf}
                <input type="hidden" id="inputID" name="inputID" value="${pk}">

                <div class="containerInputs">
                    <div class="wrapperInput">
                        <label for="">Dirección</label>
                        <input type="text" id="inputDireccion" name="inputDireccion" value="${direccion}">
                    </div>
                    <div class="wrapperInput">
                        <label for="">Hora de entrada</label>
                        <input type="text" id="inputHora" name="inputHora" value="${hora}">
                    </div>
                     <div id="selectWrapperSelectGerente" class="wrapperSelectFilter">
                        <label class="labelInput">Gerente</label>
                        <div class="containerInputAndOptions">
                        <img id="sucursalIconDisplay" class="iconDesplegar" src="${imgArrowDown}" alt="">
                            <input type="text" readonly="" name="gerente" id="gerenteInput" required="" autocomplete="off" maxlength="100" class="input-select-custom onlySelect">
                            <ul class="list-select-custom options">
                            ${gerentesDisponibles.map(gerente => `<li>${gerente.nombre}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="buttonsActions">
                    <button type="button" class="uploadForm add-button-default">Confirmar</button>
                    <button type="button" class="desableForm button-default-style">Cancelar</button>
                    <button type="button" class="enableForm add-button-default">Editar</button>
                    <button type="button" class="deleteSucursal delete-button-default" >Eliminar</button>
                </div>
            </form>
        </div>
    `
    wrapperListSucursales.insertAdjacentHTML('beforeend', stringForHTML);

}

buttonAddSucursal.addEventListener("click", () => {
    newSucursal_HTML(CSRF_TOKEN)
    cargarListenersEnInputs()
    buttonAddSucursal.classList.add("blocked")
    buttonConfirmAddSucursal.addEventListener("click", () => {
        let body = {
            "provincia": provincia.value,
            "localidad": localidad.value,
            "direccion": newDireccion.value,
            "gerente": gerenteInput.value,
            "horaApertura": newHora.value,
        }

        fetchCRUD(body, urlAddS).then(data => {
            createNewItemSucursal_HTML(CSRF_TOKEN, data["pk"], data["name"], data["direccion"], data["hora"], data["gerente"]);
            cleanAddSucursal()
            buttonAddSucursal.classList.remove("blocked")

            buttonsEnableForms = document.querySelectorAll(".enableForm")
            editarSucursal(buttonsEnableForms)

            buttonsDeleteSucursal = document.querySelectorAll(".deleteSucursal")
            removeHTMLSucursal(buttonsDeleteSucursal)
        })
    })

    buttonStopAddSucursal.addEventListener("click", () => {
        cleanAddSucursal()
        buttonAddSucursal.classList.remove("blocked")
    })

})
//  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


// FUNCTION FETCH - - - - - - - - - 
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
// - - - - - - - - - - - - - - - - -

