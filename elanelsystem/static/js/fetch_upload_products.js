const urlNewProduct = window.location.pathname
let typeHandle = "moto";

function actualizarPanel(producto) {
    const panel = document.getElementById(`panel-${typeHandle}`);
    const table = panel.querySelector("table > tbody ");
    let row;

    if (typeHandle === 'solucion') {
        row = `
            <tr>
                <td class="valorProduct">$${producto.precio}</td>
                <td class="paqueteProduct">${producto.plan}</td>
                <td class="button_cell">
                    <button class="buttonDeleteItem" type="button">   
                        <img src="${iconDelete}" alt="">
                    </button>
                </td>
            </tr>`;
    } else {
        row = `
        <tr>
            <td class="nombreProduct">${producto.nombre}</td>
            <td class="valorProduct">$${producto.precio}</td>
            <td class="paqueteProduct">${producto.plan}</td>
            <td class="button_cell">
                <button class="buttonDeleteItem" type="button">   
                    <img src="${iconDelete}" alt="">
                </button>
            </td>
        </tr>`;
    }
    table.insertAdjacentHTML("afterbegin", row);

    // Seleccionar la última fila recién añadida y pasarla a `loadListenerDelete`
    const lastRow = table.firstElementChild;
    loadListenerDelete(lastRow)
}

function agregarFormularioNuevoProducto() {
    const panel = document.getElementById(`panel-${typeHandle}`);
    const table = panel.querySelector("table > tbody");
    let row;

    if (!document.querySelector("#rowNewFormProduct")) {
        if (typeHandle === 'solucion') {
            row = `
            <tr id="rowNewFormProduct">
                <td>
                    <div class="containerInputAndOptions">
                        <img id="tipoComprobanteIconDisplay"class="iconDesplegar" src="${logoDisplayMore}" alt="">
                        <input type="text" readonly name="precio" placeholder="Precio" id="precio_input" required autocomplete="off" maxlength="30" class="input-select-custom onlySelect">
                        <ul class="list-select-custom options">
                        ${planes.map(item => `
                            <li>${item.valor_nominal}</li>
                        `).join('')}    
                        </ul>
                    </div>
                </td>
                <td><input name="plan" class="input-read-only-default" type="text" readonly placeholder="Plan" id="paquete_input" /></td>

            </tr>
            `;
        } else {
            row = `
            <tr id="rowNewFormProduct">
                <td><input name="nombre" class="input-read-write-default" type="text" placeholder="Nombre" id="nombre_input" /></td>
                <td>
                    <div class="containerInputAndOptions">
                        <img id="tipoComprobanteIconDisplay"class="iconDesplegar" src="${logoDisplayMore}" alt="">
                        <input type="text" readonly name="precio" placeholder="Precio" id="precio_input" required autocomplete="off" maxlength="30" class="input-select-custom onlySelect">
                        <ul class="list-select-custom options">
                        ${planes.map(item => `
                            <li>${item.valor_nominal}</li>
                        `).join('')}    
                        </ul>
                    </div>
                </td>
                <td><input name="plan" class="input-read-only-default" type="text" readonly placeholder="Plan" id="paquete_input" /></td>
            </tr>
            `;
        }
        cancelarNuevoProducto()
        submitButton()
        table.insertAdjacentHTML("beforeend", row);
        cargarListenersEnInputs()
        listenerParaActualizarCampoPaquete()

    }


}

function listenerParaActualizarCampoPaquete() {
    precio_input.addEventListener("input", () => {
        if (precio_input.value != "") {
            const plan = planes.find((plan) => plan.valor_nominal == precio_input.value)
            paquete_input.value = plan.tipodePlan
        } else {
            paquete_input.value = ""
        }
    })
}


async function guardarProducto() {
    const nombre = document.getElementById(`nombre_input`) ? document.getElementById(`nombre_input`).value : null;
    const paquete = document.getElementById(`paquete_input`).value;
    const precio = document.getElementById(`precio_input`).value;

    let form = {
        "tipo": typeHandle,
        "nombre": nombre,
        "plan": paquete,
        "precio": precio
    }

    let response = await fetchCRUD(form, urlNewProduct)

    if (response["success"]) {
        rowNewFormProduct.remove() // limpiamos el formulario activo
        cancelarNuevoProductoButton.remove() //Eliminamos el boton de cancelar
        submitButtonProducto.remove() //Eliminamos el boton del submit del form
        actualizarPanel(response["producto"])
        agregarButtonAgregarProducto()


    } else {
        console.log("algo salio mal")
    }
}

const headersPanel = document.querySelectorAll(".headerPanel")
headersPanel.forEach(element => {
    element.addEventListener("click", () => {
        // Primero virificamos si existe el boton de "Agregar producto", ya que sino existe
        // porque se elimino, entonces hay que volver a colocarlo
        agregarButtonAgregarProducto()

        typeHandle = element.id.slice(1)
        let panelActive = document.querySelector(`#panel-${typeHandle}`)

        limpiarPanelActivos() // limpiamos los paneles activos
        element.classList.add("active")

        if (document.querySelector("#rowNewFormProduct")) { // Verificamos si existe el formulario, si es asi tmb eliminar
            rowNewFormProduct.remove()
        }
        if (document.querySelector("#cancelarNuevoProductoButton")) { // Verificamos si existe el boton de cancelar, si es asi, eliminar
            cancelarNuevoProductoButton.remove()
        }
        if (document.querySelector("#submitButtonProducto")) { // Verificamos si existe el submit del form, si es asi, eliminar
            submitButtonProducto.remove()
        }

        panelActive.classList.add("active")
    })
});


function limpiarPanelActivos() {
    //Para gestionar los paneles
    const panelsActivos = document.querySelectorAll("#formNewProuducto > .panel.active")
    panelsActivos.forEach(element => element.classList.remove("active"));

    // Para gestionar los headers de los paneles
    const headersPanel = document.querySelectorAll(".headerPanel")
    headersPanel.forEach(element => element.classList.remove("active"));


}


function cancelarNuevoProducto() {
    const buttonCancelar = `<button class="button-default-style" id="cancelarNuevoProductoButton">Cancelar</button>`

    const panel = document.getElementById(`panel-${typeHandle}`);
    const wrapperButtonOfTable = panel.querySelector(".buttonsActions");

    wrapperButtonOfTable.insertAdjacentHTML("beforeend", buttonCancelar);
    wrapperButtonOfTable.querySelector(".agregarNuevoProductoButton").remove() //Eliminamos el boton de agregar producto

    if (document.querySelector("#cancelarNuevoProductoButton")) {
        cancelarNuevoProductoButton.addEventListener("click", () => {
            rowNewFormProduct.remove() // limpiamos el formulario activo
            cancelarNuevoProductoButton.remove() //Eliminamos el boton de cancelar
            submitButtonProducto.remove() //Eliminamos el boton del submit del form
            agregarButtonAgregarProducto()
        })
    }
}


function agregarButtonAgregarProducto() {
    const panel = document.getElementById(`panel-${typeHandle}`);
    const wrapperButtonOfTable = panel.querySelector(".buttonsActions");
    if (!wrapperButtonOfTable.querySelector(".agregarNuevoProductoButton")) {
        const buttonAgregar = `<button class="add-button-default agregarNuevoProductoButton" type="button" onclick="agregarFormularioNuevoProducto()">Agregar producto</button>`
        wrapperButtonOfTable.insertAdjacentHTML("beforeend", buttonAgregar); //Agregamos nuevamente el boton de agregar producto
    }
}

function submitButton() {
    const panel = document.getElementById(`panel-${typeHandle}`);
    const wrapperButtonOfTable = panel.querySelector(".buttonsActions");
    if (!wrapperButtonOfTable.querySelector("#submitButtonProducto")) {
        const buttonSubmit = `<button id="submitButtonProducto" class="add-button-default" type="button" onclick="guardarProducto()">Guardar producto</button>`
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
    modal.setContent("<h2>¿Estás seguro de que deseas eliminar este producto?</h2>");

    // Botón de confirmación
    modal.addFooterBtn("Eliminar", "tingle-btn tingle-btn--danger", async function () {
        // Aquí llamamos a la función de eliminación, pasando la fila correspondiente
        eliminarProducto(fila);
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

// Función para eliminar el producto
async function eliminarProducto(fila) {
    const nombreProducto = fila.querySelector("td.nombreProduct") ? fila.querySelector("td.nombreProduct").textContent : `${fila.querySelector("td.valorProduct").textContent}`;

    let form = {
        "nombre": nombreProducto,
    };

    // Realizar la solicitud al backend para eliminar el producto
    showLoader()
    let response = await fetchCRUD(form, urlDeleteP);
    if (response["status"]) {
        hiddenLoader()
        fila.remove(); // Eliminar la fila de la tabla en caso de éxito
    } else {
        hiddenLoader()
        console.log("Error al eliminar el producto.");
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
