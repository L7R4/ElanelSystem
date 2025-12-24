let buttonsEnableForms = document.querySelectorAll(".enableForm")
let buttonsDeleteCuenta = document.querySelectorAll(".deleteCuenta")
let buttonAddCuenta = document.getElementById("buttonAddCuenta")



//#region Para eliminar una sucursal - - - - - - - - - - - -
function removeHTMLCuenta(button) {
    button.addEventListener("click", () => {
        let alias = button.parentElement.parentElement.querySelector("#inputAlias").value
        let body = {
            "alias": alias
        }
        fetchCRUD(body, urlRemoveC).then(data => {
            console.table(button)
            button.parentElement.parentElement.parentElement.remove()
        })
    })
}

// Listeners para eliminar una sucursal
buttonsDeleteCuenta.forEach(button => {
    removeHTMLCuenta(button)
})
//#endregion  - - - - - - - - - - - - - - - - - - - - - -


//#region Funciones para manejo de DOM - - - - - - - - - - -
function newCuenta_HTML(csrf) {
    let stringForHTML = `
    <div class="cuentaItem new">
        <form method="POST" id="addCuentaForm">
        ${csrf}
        <div class="containerInputs">
            <div class="wrapperInputNew">
                <label for="">Alias</label>
                <input type="text" class="open" id="inputAlias" name="inputAlias">
            </div>
        </div>
        <div class="buttonsActions">
            <button type="button" class="add-button-default" id="buttonConfirmAddCuenta">Confirmar</button>
            <button type="button" class="button-default-style" id="buttonStopAddCuenta">Cancelar</button>
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
    let stringForHTML =
        `
        <div class="cuentaItem">
                <form method="POST" class="formCuenta">
                    ${csrf}
                    
                    <div class="containerInputs">
                        <div class="wrapperInput">
                            <label for="">Alias</label>
                            <input type="text" class="" id="inputAlias" name="inputAlias" value="${alias}">
                        </div>
                    </div>
                    
                    <div class="buttonsActions">
                        <button type="button" class="uploadForm add-button-default">Confirmar</button>
                        <button type="button" class="desableForm button-default-style">Cancelar</button>
                        <button type="button" class="deleteCuenta delete-button-default" >Eliminar</button>
                    </div>
                </form>
        </div>
    `
    wrapperListCuentaCobros.insertAdjacentHTML('beforeend', stringForHTML);

}

buttonAddCuenta.addEventListener("click", () => {
    newCuenta_HTML(CSRF_TOKEN)
    buttonAddCuenta.classList.add("blocked")
    buttonConfirmAddCuenta.addEventListener("click", () => {
        let inputAlias = document.querySelector(".cuentaItem.new #inputAlias")

        let body = {
            'alias': inputAlias.value
        }

        fetchCRUD(body, urlAddC).then(data => {
            createNewItemSucursal_HTML(CSRF_TOKEN, data['alias']);
            cleanAddCuenta()
            buttonAddCuenta.classList.remove("blocked")

            // Obtener el ultimo item creado y agregarle el listener al boton de eliminar
            let lastCuentaCreada = document.querySelector(".cuentaItem:last-child")
            let buttonDeleteCuenta = lastCuentaCreada.querySelector(".deleteCuenta")
            
            removeHTMLCuenta(buttonDeleteCuenta)
        })
    })

    buttonStopAddCuenta.addEventListener("click", () => {
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

