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
            <button type="button" class="iconInfoMore moreInfoComisionButton" onclick="modal_more_info_comision_by_id(${item.id})"><img src=${info_icon} alt=""></button>
        </div>
        <div>
            <button type="button" class="button-default-style ajusteComisionButton" onclick="modal_ajuste_comision(${item.id}, '${item.nombre}', ${item.comisionTotal})">Ajustar comision</button>
        </div>
    </li>`;
    contenedor.insertAdjacentHTML("beforeend",divs)
  
});
}

function actualizarTotalComisionado(dinero){
    const spanDinero = document.querySelector("#dineroTotalComisiones");
    let inputDinero = document.querySelector("#totalComisionesInput");
    if (spanDinero) {
        const dineroFormateado = new Intl.NumberFormat("es-AR").format(dinero);
        spanDinero.textContent = dineroFormateado;
        inputDinero.value = dinero
    }
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



// #region Obtener mas info sobre la liquidacion
function render_detalle_comision(user_id, user_name, tipo_colaborador, otros_ajustes, detalle) {
    const ventas = detalle.ventasPropias?.detalle || {};
    const premios = detalle.premios?.detalle || {};
    const rol = detalle.rol?.detalle || {};
    const ajustes = otros_ajustes || [];

    let total_ajuste = 0;
    ajustes.forEach(aj => {
        if (aj.ajuste_tipo === "positivo") total_ajuste += aj.dinero;
        else if (aj.ajuste_tipo === "negativo") total_ajuste -= aj.dinero;
    });

    const comision_ventas = ventas.comisionXCantidadVentasPropias || 0;
    const comision_cuotas = ventas.comisionXCuotas1 || 0;
    const premio_productividad_propia = premios.premio_x_productividad_ventas_propias || 0;
    const premio_ventas_equipo = premios.premio_x_cantidad_ventas_equipo || 0;
    const premio_productividad_equipo = premios.premio_x_productividad_ventas_equipo || 0;
    const comision_ventas_equipo = detalle.rol.comision_subtotal || 0;
    const comision_total = comision_ventas_equipo + comision_ventas + comision_cuotas + premio_productividad_propia + premio_ventas_equipo + premio_productividad_equipo + total_ajuste;

    let html = `<div class="wrapperDetalleLiquidacion">
        <h2>Detalle de ${user_name}</h2>`;

    if (tipo_colaborador.toLowerCase() === "vendedor" || tipo_colaborador.toLowerCase() === "supervisor") {
        html += `
        <div class="subDetalleGroup">
            <h3>Ventas propias</h3>
            <p><strong>Cantidad de ventas:</strong> ${ventas.cantidadVentas || 0}</p>
            <p><strong>Productividad propia:</strong> $${ventas.productividadXVentasPropias || 0}</p>
            <p><strong>Cuotas 1 pagadas:</strong> ${ventas.cantidadCuotas1 || 0}</p>
            <p><strong>Comisión por ventas:</strong> $${comision_ventas}</p>
            <p><strong>Comisión por cuotas 1:</strong> $${comision_cuotas}</p>
            <p><strong>Premio por productividad propia:</strong> $${premio_productividad_propia}</p>
        </div>`;
    }

    if (tipo_colaborador.toLowerCase() === "supervisor") {
        html += `
        <div class="subDetalleGroup">
            <h3>Equipo</h3>
            <p><strong>Cantidad de ventas del equipo:</strong> ${rol.cantidadVentasXEquipo || 0}</p>
            <p><strong>Productividad del equipo:</strong> $${rol.productividadXVentasEquipo || 0}</p>
            <p><strong>Comision por cantidad de ventas del equipo:</strong> $${comision_ventas_equipo}</p>
            <p><strong>Premio por cantidad de ventas del equipo:</strong> $${premio_ventas_equipo}</p>
            <p><strong>Premio por productividad del equipo:</strong> $${premio_productividad_equipo}</p>
        </div>`;
    }

    if (tipo_colaborador.toLowerCase() === "gerente de sucursal") {
        html += `<h3 class="textCenter">Sin información</h3>`;
    }

    html += `
        <div class="subDetalleGroup">
            <h3>Ajustes manuales</h3>`;

    if (ajustes.length === 0) {
        html += `<p>No se aplicaron ajustes.</p>`;
    } else {
        ajustes.forEach((aj, i) => {
            const signo = aj.ajuste_tipo === "positivo" ? "+" : "-";
            html += `<p><strong>${signo}$${aj.dinero}</strong> - ${aj.observaciones || "Sin observaciones"}</p>`;
        });
        html += `<p><strong>Total ajustado:</strong> $${total_ajuste}</p>`;
    }

    html += `</div>
        <div class="subDetalleGroup resumenTotalComision">
            <h3>Total final de comisión:</h3>
            <p><strong>$${comision_total}</strong></p>
        </div>
    </div>`;

    return html;
}


function modal_more_info_comision_by_id(user_id) {
    const colaborador = itemsColaboradores.find(item => item.id === user_id);
    if (!colaborador) return;

    modal_more_info_comision(
        colaborador.id,
        colaborador.nombre,
        colaborador.tipo_colaborador,
        colaborador.ajustes_comision,
        colaborador.info_total_de_comision?.detalle || {}
    );
}

function modal_more_info_comision(user_id, user_name, tipo_colaborador, otros_ajustes, detalle) {
    let modal = new tingle.modal({
        footer: true,
        closeMethods: [''],
        cssClass: ['moda_container_more_info'],
        onOpen: function () {},
        onClose: function () { modal.destroy(); },
    });

    modal.setContent(render_detalle_comision(user_id, user_name, tipo_colaborador, otros_ajustes, detalle));

    modal.addFooterBtn('Cerrar', 'tingle-btn tingle-btn--default button-default-style', function () {
        modal.close();
        modal.destroy();
    });

    modal.open();
}
// #endregion