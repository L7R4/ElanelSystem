let typeHandle = "motos";


function actualizarPanel(producto) {
    const panel = document.getElementById(`panel-${typeHandle}`);
    const table = panel.querySelector("table > tbody ");
    let row;

    if (tipo === 'soluciones') {
        row = `
            <tr>
                <td>$${producto.precio}</td>
                <td>${producto.plan}</td>
            </tr>`;
    } else {
        row = `
        <tr>
            <td>${producto.nombre}</td>
            <td>${producto.precio}</td>
            <td>${producto.plan}</td>
        </tr>`;
    }
    table.insertAdjacentHTML("beforeend", row);
}
{/* <input name="precio" type="number" placeholder="Precio" id="precio" /> */}

function agregarFormularioNuevoProducto() {
    const panel = document.getElementById(`panel-${typeHandle}`);
    const table = panel.querySelector("table > tbody");
    let row;

    if(!document.querySelector("#rowNewFormProduct")){
        if (typeHandle === 'soluciones') {
            row = `
            <tr id="rowNewFormProduct">
                <td>
                    <div class="containerInputAndOptions">
                        <img id="tipoComprobanteIconDisplay"class="iconDesplegar" src="${logoDisplayMore}" alt="">
                        <input type="text" readonly name="precio" id="id_precio" required autocomplete="off" maxlength="30" class="input-select-custom onlySelect">
                        <ul class="list-select-custom options">
                        ${planes.map(item => `
                            <li>${item.valor_nominal}</li>
                        `).join('')}    
                        </ul>
                    </div>
                </td>
                <td><input name="plan" type="text" placeholder="Plan" id="paquete" /></td>

            </tr>
            `;
        } else {
            row = `
            <tr id="rowNewFormProduct">
                <td><input name="nombre" type="text" placeholder="Nombre" id="nombre" /></td>
                <td>
                    <div class="containerInputAndOptions">
                        <img id="tipoComprobanteIconDisplay"class="iconDesplegar" src="${logoDisplayMore}" alt="">
                        <input type="text" readonly name="precio" id="id_precio" required autocomplete="off" maxlength="30" class="input-select-custom onlySelect">
                        <ul class="list-select-custom options">
                        ${planes.map(item => `
                            <li>${item.valor_nominal}</li>
                        `).join('')}    
                        </ul>
                    </div>
                </td>
                <td><input name="plan" type="text" placeholder="Plan" id="paquete" /></td>
            </tr>
            `;
        }
        cancelarNuevoProducto()
        table.insertAdjacentHTML("beforeend", row);
        cargarListenersEnInputs()
        listenerParaActualizarCampoPaquete()
        
    }
    

}

function listenerParaActualizarCampoPaquete() {
    id_precio.addEventListener("input", ()=>{
        if(id_precio.value != ""){
            const plan = planes.find((plan)=> plan.valor_nominal == id_precio.value)
            paquete.value = plan.tipodePlan
        }else{
            paquete.value = ""
        }
    })
}


async function guardarProducto() {
    const nombre = document.getElementById(`nombre`) ? document.getElementById(`nombre`).value : null;
    const plan = document.getElementById(`paquete`) ? document.getElementById(`paquete`).value : null;
    const precio = document.getElementById(`precio`).value;

    let form = {
        "tipo": typeHandle,
        "nombre": nombre,
        "plan": plan,
        "precio": precio
    }

    let response = await fetchCRUD(form,urlNewProduct)

    if(response["success"]){
        rowNewFormProduct.remove()
        actualizarPanel(typeHandle,response["producto"])
        
    }else{
        console.log("algo salio mal")
    }
}

const headersPanel = document.querySelectorAll(".headerPanel")
headersPanel.forEach(element => {
    element.addEventListener("click", ()=>{
        typeHandle = element.id.slice(1)
        let panelActive = document.querySelector(`#panel-${typeHandle}`)

        limpiarPanelActivos() // limpiamos los paneles activos
        element.classList.add("active")

        if(document.querySelector("#rowNewFormProduct")){ // Verificamos si existe el formulario, si es asi tmb eliminar
            rowNewFormProduct.remove() 
        }
        if(document.querySelector("#cancelarNuevoProductoButton")){ // Verificamos si existe el boton de cancelar, si es asi, eliminar
            cancelarNuevoProductoButton.remove()
        }

        panelActive.classList.add("active")
    })
});

function limpiarPanelActivos() {
    //Para gestionar los paneles
    const panelsActivos = document.querySelectorAll(".panel-container > .panel.active")
    panelsActivos.forEach(element => element.classList.remove("active"));

    // Para gestionar los headers de los paneles
    const headersPanel = document.querySelectorAll(".headerPanel")
    headersPanel.forEach(element => element.classList.remove("active"));


}


function cancelarNuevoProducto() {
    const buttonCancelar = `<button class="" id="cancelarNuevoProductoButton">Cancelar</button>`

    const panel = document.getElementById(`panel-${typeHandle}`);
    const table = panel.querySelector("table");
    table.insertAdjacentHTML("afterend", buttonCancelar);

    if(document.querySelector("#cancelarNuevoProductoButton")){
        cancelarNuevoProductoButton.addEventListener("click", ()=>{
            rowNewFormProduct.remove() // limpiamos el formulario activo
            cancelarNuevoProductoButton.remove()
        })
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
