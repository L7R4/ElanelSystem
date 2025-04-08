let contendorColaboradores = document.querySelector(".listColaboradoresWrapper > .valuesWrapper > .values ")
const radioFiltros = document.querySelectorAll('.inputSelectTipoColaborador');


let colaboradoresAFiltrar = "todos"
let body ={}

//Funcion para habilitar panel de comision
function habilitarPanelComision() {
    return inputCampania.value != "" && inputSucursal.value != ""
}


//#region Filtro sucursal - - - - - - - - - - - - 
let inputSucursal = document.getElementById("sucursalInput")
inputSucursal.addEventListener("input", async ()=>{
    
    if(habilitarPanelComision()){

        body.sucursal = inputSucursal.value;
        body.campania = inputCampania.value;
        body.tipoColaborador = colaboradoresAFiltrar;
        
        let response = await fetchFunction(body,urlRequestColaboradores)
        console.log(response)   
        actualizarResultadosColaboradores(response["colaboradores_data"],contendorColaboradores)
        actualizarTotalComisionado(response["totalDeComisiones"])


    }else{
        contendorColaboradores.innerHTML = ""
        actualizarTotalComisionado(0)
    }
    update_textPreValues_to_values()

})
//#endregion  - - - - - - - - - - - - - - - - - - - 


//#region Filtro campaña - - - - - - - - - - - - 
let inputCampania = document.getElementById("campaniaInput")
inputCampania.addEventListener("input", async ()=>{
    
    if(habilitarPanelComision()){
        body.sucursal = inputSucursal.value;
        body.campania = inputCampania.value;
        body.tipoColaborador = colaboradoresAFiltrar;

        let response = await fetchFunction(body,urlRequestColaboradores)
        console.log(response)
        actualizarResultadosColaboradores(response["colaboradores_data"],contendorColaboradores)
        actualizarTotalComisionado(response["totalDeComisiones"])


    }
    else{
        contendorColaboradores.innerHTML = ""
        actualizarTotalComisionado(0)
    }
    update_textPreValues_to_values()


})
//#endregion  - - - - - - - - - - - - - - - - - - - 


//#region  Filtros de radios - - - - - - - - - - - - - - - - -

radioFiltros.forEach(radio => {
    radio.addEventListener('change', async () => {
        console.log("Funciona input de tipo de colaboradores")
        colaboradoresAFiltrar = radio.value // Actuliza el valor de la variable global para posibles filtros
        body.sucursal = inputSucursal.value;
        body.campania = inputCampania.value;
        body.tipoColaborador = colaboradoresAFiltrar;

        let response = await fetchFunction(body, urlRequestColaboradores)
        console.log(response)
        actualizarResultadosColaboradores(response["colaboradores_data"],contendorColaboradores)
        actualizarTotalComisionado(response["totalDeComisiones"])
    });
})
//#endregion  - - - - - - - - - - - - - - - - - - - - - - - - - -



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
        let response = await fetch(url, {
            method: 'POST',
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
//#endregion - - - - - - - - - - - - - - -


//#region Funciones para actualizar panel de comisiones de colaboradores sin administradores
let itemsColaboradores;
function actualizarResultadosColaboradores(resultados, contenedor) {
    console.log(resultados)
  // Limpia el contenedor de los datos
  contenedor.innerHTML = "";
  itemsColaboradores = resultados.filter(item => !item.tipo_colaborador.includes("Administracion"))

  // Se reccore los datos filtrados
  itemsColaboradores.forEach((item) => {
    let divs ="";
    // Se reccore los campos de cada elemento y se lo guarda en un div
    divs += `<li id="idColaborador_${item.id}">
        <div class="wrapperNombreColaborador">
            <p>${item.nombre}</p>
        </div>
        <div class="wrapperComisionColaborador">
            <p>$ ${item.comisionTotal}</p>
        </div>
        <div>
            <button type="button" class="button-default-style" id="liquidarButton" onclick="modal_ajuste_comision(${item.id}, '${item.nombre}')">Ajustar comision</button>
        </div>
    </li>`;
    contenedor.insertAdjacentHTML("beforeend",divs)
  
});
}

function render_form_ajuse_comision(nombre_usuario) {
    return `<form method="POST" class="modal_form" id="formNewMov">

            <div class="wrapperTittle">
                <h3 class="labelInput">Ajustar comisiones a ${nombre_usuario}</h3>
            </div>
            ${CSRF_TOKEN}

            <div class="wrapperInput">
                <h3 class="labelInput">Dinero</h3>
                <input type="number" name="dinero" id="dineroAjusteInput" class="input-read-write-default">
            </div>
            <div class="wrapperInputObservaciones">
                <label for="observacionesInput">Observaciones</label>
                <textarea name="observaciones" id="observacionesInput" cols="30" rows="10"></textarea>
            </div>
        </form>`
}

function modal_ajuste_comision(id_usuario, nombre_usuario){
    let modal = new tingle.modal({
        footer: true,
        closeMethods: [''],
        cssClass: ['moda_container_ajusteComision'],

        onOpen: function () {
            initCustomSingleSelects()
        },

        onClose: function () {
            modal.destroy();
        },
    });
    console.log(id_usuario, nombre_usuario)


    // set content
    modal.setContent(render_form_ajuse_comision(nombre_usuario));


    // add a button
    modal.addFooterBtn('Guardar', 'tingle-btn tingle-btn--primary', async function () {

        body = {
            "campania": document.querySelector("#campaniaInput").value,
            "agencia": document.querySelector("#sucursalInput").value,
        }
        console.log(body)
        // showLoader()
        // let response = await fetchCRUD(body, urlLiquidacion)

        // if (response.status) {
        //     console.log("Salio todo bien");
        //     hiddenLoader();
        //     modal.close();
        //     modal.destroy();
        // }else{
        //     console.log("Salio mal")
        //     hiddenLoader()
        //     modal.close();
        //     modal.destroy();
        // }
    });

    modal.addFooterBtn('Cancelar', 'tingle-btn tingle-btn--default', function () {
        modal.close();
        modal.destroy();
    });

    modal.open();
}

function actualizarTotalComisionado(dinero){
    let totalComisionesTextColaboradores = document.querySelector("#totalComisionesTextColaboradores_wrapper > h3")
    totalComisionesTextColaboradores.textContent = "Total $" + dinero
}

function update_textPreValues_to_values() {
    let textPreValues = document.querySelector("#textPreValuesColaboradores")
    let valuesWrapper = document.querySelector(".listColaboradoresWrapper > .valuesWrapper")
    let wrapperButtonsActions = document.querySelector(".wrapperButtonsActions")

    if(habilitarPanelComision()){
        textPreValues.classList.add("hidden")
        valuesWrapper.classList.remove("preValues")
        wrapperButtonsActions.classList.remove("hidden")
    }else{
        textPreValues.classList.remove("hidden")
        valuesWrapper.classList.add("preValues")
        wrapperButtonsActions.classList.add("hidden")

    }


}


//#endregion  - - - - - - - - - - - - - - - - - - - - - - - - - -



