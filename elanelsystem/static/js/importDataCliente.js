
function renderFormImportData() {
    return `
    <div id="importDataContainer">
        <h2 class="tittleModal">Importar clientes</h2>
        <form id="importForm" enctype="multipart/form-data">
          ${csrf_token}
          <div id="agenciaWrapper" class="inputWrapper">
            <label class="labelInput">Sucursal</label>
            <div class="containerInputAndOptions">
                <img id="tipoComprobanteIconDisplay"class="iconDesplegar" src="${logoDisplayMore}" alt="">
                <input placeholder="Seleccionar" type="text" readonly name="agencia" id="agenciaInput" required="required" autocomplete="off" maxlength="50" class="checkInput input-select-custom onlySelect">
                <ul id="contenedorAgencia" class="list-select-custom options">
                ${sucursalesDisponibles.map(item => `
                    <li>${item}</li>
                `).join('')}   
                </ul>
            </div>
          </div>
          <div class="containerSelectFile">
            <label for="importDataInput" class="button-default-style ">
                Seleccionar Archivo
            </label>
            <p id="nameFile"></p>
            <input type="file" id="importDataInput" class="checkInput" oninput="displayNameFile(this)" style="display:none;"/>
          </div>
          
        </form>
    </div>
    `
}

function renderMessage(message, iconMessage) {
    return `
        <div id="messageStatusContainer">
            <img src="${iconMessage}" alt="">
            <h2>${message}</h2>
        </div>
    `
}

//#region Manejar el display del loader
function showLoader() {
    document.querySelector('.modalContainerImport').children[0].style.display = "none";
    document.getElementById('wrapperLoader').style.display = 'flex';
}

function hiddenLoader() {
    document.getElementById('wrapperLoader').style.display = 'none';
}
//#endregion

function newModalImport() {
    let modal = new tingle.modal({
        footer: true,
        closeMethods: [''],
        cssClass: ['modalContainerImport'],

        onOpen: function () {
            cargarListenersEnInputs() // Para cargar los listeners de los inputs selects custom
            enableImportButton()
        },
        onClose: function () {
            modal.destroy();
        },
    });

    // set content
    modal.setContent(renderFormImportData());


    // add a button
    modal.addFooterBtn('Importar', 'tingle-btn tingle-btn--primary', async function () {

        const inputFile = document.getElementById('importDataInput').files[0];
        let body = {
            "file": inputFile,
            "agencia": agenciaInput.value,
        }

        showLoader()
        setTimeout(async function () {
            let response = await fetchFunction(body, urlImportData);

            if (response.status) {
                console.log("Salio todo bien");
                hiddenLoader();
                modal.close();
                modal.destroy();
            } else {
                console.log("Salio todo mal");
                hiddenLoader();

                modal.close();
                modal.destroy();
            }
            newModalMessage(response.message, response.iconMessage);
        }, 5000);  // 10,000 milisegundos = 10 segundos
        // let response = await fetchFunction(body,urlImportData)
        // if(response.status){
        //     console.log("Salio todo bien")
        //     modal.close();
        //     modal.destroy();
        // }
        // else{
        //     console.log("Salio todo mal")
        //     modal.close();
        //     modal.destroy();
        // }
        // newModalMessage(response.message,response.iconMessage)

    });

    // add another button
    modal.addFooterBtn('Cancelar', 'tingle-btn tingle-btn--default', function () {
        // here goes some logic
        modal.close();
        modal.destroy();
    });

    // open modal
    modal.open();

    // Se bloquea hasta que los campos esten todos completos
    document.querySelector(".tingle-btn--primary").disabled = true;

}

function enableImportButton() {
    // Obtener el botón de importar
    const importButton = document.querySelector(".tingle-btn--primary");

    // Obtener los inputs que queremos validar
    const agenciaInput = document.getElementById("agenciaInput");
    const importDataInput = document.getElementById("importDataInput");

    // Función que verifica si los inputs están completos
    function checkInputs() {
        console.log("asda")
        if (agenciaInput.value && importDataInput.files.length > 0) {
            importButton.disabled = false;  // Habilitar el botón
            importButton.classList.remove("disabled")

        } else {
            importButton.disabled = true;  // Deshabilitar el botón
            importButton.classList.add("disabled")

        }
    }
    checkInputs()
    // Escuchar cambios en ambos inputs
    agenciaInput.addEventListener("input", checkInputs);
    importDataInput.addEventListener("input", checkInputs);
}

function newModalMessage(message, iconMessage) {
    let modalMessage = new tingle.modal({
        footer: true,
        closeMethods: ['overlay', 'button', 'escape'],
        cssClass: ['modalContainerMessage'],

    });

    // set content
    modalMessage.setContent(renderMessage(message, iconMessage));


    modalMessage.addFooterBtn('Cerrar', 'tingle-btn tingle-btn--default', function () {
        // here goes some logic
        modalMessage.close();
        modalMessage.destroy();
    });

    // open modal
    modalMessage.open();
}

function displayNameFile(input) {
    if (input.files[0]) {
        document.getElementById("nameFile").textContent = input.files[0].name

    } else {
        document.getElementById("nameFile").textContent = ""
    }
}
//#region Fetch data
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

async function fetchFunction(body, url) {
    try {
        let formData = new FormData();
        formData.append('file', body.file);  // Añadir el archivo
        formData.append('agencia', body.agencia);  // Añadir la agencia

        let response = await fetch(url, {
            method: 'POST',
            body: formData,
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
//#endregion - - - - - - - - - - - - - - -
