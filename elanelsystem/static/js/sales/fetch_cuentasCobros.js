let buttonsDeleteCuenta = document.querySelectorAll(".deleteCuenta")
let buttonAddCuenta = document.getElementById("buttonAddCuenta")
let wrapperListCuentaCobros = document.getElementById("wrapperListCuentaCobros")

//#region Para eliminar una sucursal - - - - - - - - - - - -
function removeHTMLCuenta(button) {
    button.addEventListener("click", () => {
        let alias = button.parentElement.parentElement.querySelector("#inputAlias").value
        
        // Crear Modal Tingle de Confirmacion
        let modalConfirmacion = new tingle.modal({
            footer: true,
            stickyFooter: false,
            closeMethods: ['overlay', 'button', 'escape'],
            closeLabel: "Cerrar",
            cssClass: ['modalConfirmacion']
        });

        modalConfirmacion.setContent(`
            <div class="messageConfirmModal" style="text-align: center; padding: 1rem 0;">
                <i class="fa-solid fa-triangle-exclamation" style="font-size: 4rem; color: #ef4444; margin-bottom: 1.5rem; display: block;"></i>
                <h2>¿Eliminar Cuenta?</h2>
                <p style="margin-top: 1rem; line-height: 1.5;">¿Estás seguro de que deseas eliminar la cuenta de cobro con el alias <strong>"${alias}"</strong>?<br>Esta acción es permanente.</p>
            </div>
        `);

        modalConfirmacion.addFooterBtn('<i class="fa-solid fa-circle-xmark"></i> Cancelar', 'tingle-btn tingle-btn--default', function() {
            modalConfirmacion.close();
        });

        modalConfirmacion.addFooterBtn('<i class="fa-solid fa-trash-can"></i> Eliminar', 'tingle-btn tingle-btn--danger', function() {
            let body = {
                "alias": alias
            }
            fetchCRUD(body, urlRemoveC).then(data => {
                button.parentElement.parentElement.parentElement.remove();
                modalConfirmacion.close();
                
                // Mostrar Modal de respuesta/éxito
                let modalRespuesta = new tingle.modal({
                    closeMethods: ['overlay', 'button', 'escape'],
                    closeLabel: "Cerrar"
                });
                modalRespuesta.setContent(`
                    <div style="text-align: center; padding: 2rem 0;">
                        <i class="fa-solid fa-circle-check" style="font-size: 4rem; color: #10b981; margin-bottom: 1.5rem; display: block;"></i>
                        <h2>Eliminado con Éxito</h2>
                        <p style="margin-top: 1rem;">La cuenta se ha eliminado correctamente.</p>
                    </div>
                `);
                modalRespuesta.open();
                setTimeout(() => { modalRespuesta.close(); }, 1500);
            }).catch(err => {
                modalConfirmacion.close();
            });
        });

        modalConfirmacion.open();
    })
}

// Listeners para eliminar cuentas existentes
buttonsDeleteCuenta.forEach(button => {
    removeHTMLCuenta(button)
})
//#endregion  - - - - - - - - - - - - - - - - - - - - - -


//#region Funciones para manejo de DOM - - - - - - - - - - -
function newCuenta_HTML(csrf) {
    let stringForHTML = `
    <div class="cuentaItem new glass-panel">
        <form method="POST" id="addCuentaForm">
            ${csrf}
            <div class="cuenta-card-header">
                <i class="fa-solid fa-plus branch-title-icon"></i>
                <h2>Nueva Cuenta</h2>
            </div>
            <div class="containerInputs">
                <div class="wrapperInputNew">
                    <label class="labelInput"><i class="fa-solid fa-tag"></i> Nombre / Alias</label>
                    <input type="text" placeholder="Ej. MercadoPago" id="inputAlias" name="inputAlias" autocomplete="off" required>
                </div>
            </div>
            <div class="buttonsActions">
                <button type="button" class="add-button-default" id="buttonConfirmAddCuenta">
                    <i class="fa-solid fa-circle-check"></i> Confirmar
                </button>
                <button type="button" class="button-default-style" id="buttonStopAddCuenta">
                    <i class="fa-solid fa-circle-xmark"></i> Cancelar
                </button>
            </div>
        </form>
    </div> `
    wrapperListCuentaCobros.insertAdjacentHTML('beforeend', stringForHTML);
}

function cleanAddCuenta() {
    if (document.getElementById("addCuentaForm")) {
        document.querySelector(".cuentaItem.new").remove()
    }
}
//#endregion  - - - - - - - - - - - - - - - - - - - - - - 

//#region Crear una nueva sucursal  - - - - - - - - - - - - - - - - - - - - - -
function createNewItemSucursal_HTML(csrf, alias) {
    let stringForHTML = `
        <div class="cuentaItem glass-panel">
            <form method="POST" class="formCuenta">
                ${csrf}
                <div class="cuenta-card-header">
                    <i class="fa-solid fa-wallet branch-title-icon"></i>
                    <h2>Alias de Cuenta</h2>
                </div>
                <div class="containerInputs">
                    <div class="wrapperInput">
                        <label class="labelInput"><i class="fa-solid fa-tag"></i> Nombre / Alias</label>
                        <input type="text" class="input-alias-style" id="inputAlias" name="inputAlias" value="${alias}" readonly>
                    </div>
                </div>
                <div class="buttonsActions">
                    <button type="button" class="deleteCuenta delete-button-default">
                        <i class="fa-solid fa-trash-can"></i> Eliminar
                    </button>
                </div>
            </form>
        </div>`
    wrapperListCuentaCobros.insertAdjacentHTML('beforeend', stringForHTML);
}

buttonAddCuenta.addEventListener("click", () => {
    newCuenta_HTML(CSRF_TOKEN)
    buttonAddCuenta.classList.add("blocked")
    
    // Enfocar el input alias inmediatamente
    document.querySelector(".cuentaItem.new #inputAlias").focus();

    document.getElementById("buttonConfirmAddCuenta").addEventListener("click", () => {
        let inputAlias = document.querySelector(".cuentaItem.new #inputAlias")

        if(!inputAlias.value.trim()){
            inputAlias.style.borderColor = "#ef4444";
            return;
        }

        let body = {
            'alias': inputAlias.value.trim()
        }

        fetchCRUD(body, urlAddC).then(data => {
            createNewItemSucursal_HTML(CSRF_TOKEN, data['alias']);
            cleanAddCuenta()
            buttonAddCuenta.classList.remove("blocked")

            // Obtener el ultimo item creado y agregarle el listener al boton de eliminar
            let lastCuentaCreada = document.querySelector(".cuentaItem:last-child")
            let buttonDeleteCuenta = lastCuentaCreada.querySelector(".deleteCuenta")
            
            removeHTMLCuenta(buttonDeleteCuenta)

            // Modal de éxito al agregar
            let modalExito = new tingle.modal({
                closeMethods: ['overlay', 'button', 'escape'],
                closeLabel: "Cerrar"
            });
            modalExito.setContent(`
                <div style="text-align: center; padding: 2rem 0;">
                    <i class="fa-solid fa-circle-check" style="font-size: 4rem; color: #10b981; margin-bottom: 1.5rem; display: block;"></i>
                    <h2>Creada con Éxito</h2>
                    <p style="margin-top: 1rem;">La cuenta de cobro se ha registrado correctamente.</p>
                </div>
            `);
            modalExito.open();
            setTimeout(() => { modalExito.close(); }, 1500);
        })
    })

    document.getElementById("buttonStopAddCuenta").addEventListener("click", () => {
        cleanAddCuenta()
        buttonAddCuenta.classList.remove("blocked")
    })
})
//#endregion  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


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
                "Content-Type": "application/json"
            }
        })
        if (!response.ok) {
            throw new Error("Error")
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(error);
    }
}
