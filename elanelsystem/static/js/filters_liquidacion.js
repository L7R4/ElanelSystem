let contendorColaboradores = document.querySelector(".listColaboradoresWrapper > .valuesWrapper > .values ")
const radioFiltros = document.querySelectorAll('.inputSelectTipoColaborador');


let colaboradoresAFiltrar = "todos"
let body = {}

//Funcion para habilitar panel de comision
function habilitarPanelComision() {
    return inputCampania.value != "" && inputSucursal.value != ""
}


//#region Filtro sucursal - - - - - - - - - - - - 
let inputSucursal = document.getElementById("sucursalInput")
inputSucursal.addEventListener("input", async () => {

    if (habilitarPanelComision()) {

        body.sucursal = inputSucursal.value;
        body.campania = inputCampania.value;
        body.tipoColaborador = colaboradoresAFiltrar;
        showLoader()
        let response = await fetchFunction(body, urlRequestColaboradores)
        hiddenLoader()
        console.log(response)
        actualizarResultadosColaboradores(response["colaboradores_data"], contendorColaboradores)
        actualizarTotalComisionado(response["totalDeComisiones"])

        if (response["messageAlert"]) {
            let messageDOM = messageAlert(response["messageAlert"], "alert")
            toggleMessage(document.querySelector(".wrapperHeader"), messageDOM)
        }

    } else {
        contendorColaboradores.innerHTML = ""
        actualizarTotalComisionado(0)
    }
    update_textPreValues_to_values()

})
//#endregion  - - - - - - - - - - - - - - - - - - - 


//#region Filtro campaña - - - - - - - - - - - - 
let inputCampania = document.getElementById("campaniaInput")
inputCampania.addEventListener("input", async () => {

    if (habilitarPanelComision()) {
        body.sucursal = inputSucursal.value;
        body.campania = inputCampania.value;
        body.tipoColaborador = colaboradoresAFiltrar;

        showLoader()
        let response = await fetchFunction(body, urlRequestColaboradores)
        hiddenLoader()
        console.log(response)
        actualizarResultadosColaboradores(response["colaboradores_data"], contendorColaboradores)
        actualizarTotalComisionado(response["totalDeComisiones"])

        if (response["messageAlert"]) {
            let messageDOM = messageAlert(response["messageAlert"], "alert")
            toggleMessage(document.querySelector(".wrapperHeader"), messageDOM)
        }

    }
    else {
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
        showLoader()
        let response = await fetchFunction(body, urlRequestColaboradores)
        hiddenLoader()
        console.log(response)
        actualizarResultadosColaboradores(response["colaboradores_data"], contendorColaboradores)
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
        let divs = "";
        // Se reccore los campos de cada elemento y se lo guarda en un div
        divs += `<li id="idColaborador_${item.id}">
        <div class="wrapperNombreColaborador">
            <p>${item.nombre}</p>
        </div>
        <div class="wrapperComisionColaborador">
            <p>$ ${item.comisionTotal}</p>
            <button type="button" class="iconInfoMore moreInfoComisionButton" onclick="modal_more_info_comision_by_id(${item.id})"><img src=${info_icon} alt=""></button>
            <button type="button" class="iconInfoMore moreInfoComisionButton" onclick="create_excel_detail_info(${item.id},'${inputCampania.value}',${inputSucursal.value})"><img src=${export_icon} alt=""></button>
        </div>
        <div>
            <button type="button" class="button-default-style ajusteComisionButton" onclick="modal_ajuste_comision(${item.id}, '${item.nombre}', ${item.comisionTotal})">Ajustar comision</button>
        </div>
        
    </li>`;
        contenedor.insertAdjacentHTML("beforeend", divs)

    });
}

function actualizarTotalComisionado(dinero) {
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

    if (habilitarPanelComision()) {
        textPreValues.classList.add("hidden")
        valuesWrapper.classList.remove("preValues")
        wrapperButtonsActions.classList.remove("hidden")
    } else {
        textPreValues.classList.remove("hidden")
        valuesWrapper.classList.add("preValues")
        wrapperButtonsActions.classList.add("hidden")

    }
}


//#endregion  - - - - - - - - - - - - - - - - - - - - - - - - - -


//#region Manejo de posibles mensajes

function messageAlert(messaje, type) {
    return `<a target="_blank" href="${urlVentasNoComisionables}" class="wrapperMessage ${type}">
            <h3><strong>Alerta</strong> ${messaje} <span>(click para ver)</span></h3>
        </a>`
}

function toggleMessage(container, messageDOM) {
    if (container.querySelector(".wrapperMessage")) {
        let messageWrapper = container.querySelector(".wrapperMessage");
        messageWrapper.remove();
    } else {
        container.insertAdjacentHTML("beforeend", messageDOM)
    }
}

//#endregion

//#region Manejar el display del loader
function showLoader(container = false) {
    if (container) {
        document.querySelector(container).children[0].style.display = "none";
    }

    document.getElementById('wrapperLoader').style.display = 'flex';
}

function hiddenLoader() {
    document.getElementById('wrapperLoader').style.display = 'none';
}
//#endregion


// #region Obtener mas info sobre la liquidacion
// function render_detalle_comision(user_id, user_name, tipo_colaborador, otros_ajustes, detalle) {


//     const ventas = detalle.info_total_de_comision.detalle.ventasPropias || {};
//     const rol = detalle.info_total_de_comision.detalle.rol || {};
//     const ajustes = otros_ajustes || [];

//     let total_ajuste = 0;
//     ajustes.forEach(aj => {
//         if (aj.ajuste_tipo === "positivo") total_ajuste += aj.dinero;
//         else if (aj.ajuste_tipo === "negativo") total_ajuste -= aj.dinero;
//     });

//     const comision_ventas = ventas.comision_x_cantidad_ventas || 0;
//     const comision_cuotas = ventas.comision_x_cuotas1 || 0;
//     const premio_productividad_propia = ventas.premio_x_productividad_ventas_propias || 0;

//     const premio_ventas_equipo = rol.comision_x_ventas_equipo || 0;
//     const premio_productividad_equipo = rol.comision_x_productividad || 0;
//     const comision_ventas_equipo = rol.comision_x_cantidad_ventas || 0;

//     const comision_total = detalle.comisionTotal
//     const asegurado = detalle.info_total_de_comision.asegurado

//     let html = `<div class="wrapperDetalleLiquidacion">
//         <h2>Detalle de ${user_name}</h2>`;

//     html += `
//     <div class="subDetalleGroup">
//         <h3>Ventas propias</h3>
//         <p><strong>Cantidad de ventas:</strong> ${ventas.cantidadVentas || 0}</p>
//         <p><strong>Productividad propia:</strong> $${ventas.productividadXVentasPropias || 0}</p>
//         <p><strong>Cuotas 1 pagadas:</strong> ${ventas.cantidadCuotas1 || 0}</p>
//         <p><strong>Comisión por ventas:</strong> $${comision_ventas}</p>
//         <p><strong>Comisión por cuotas 1:</strong> $${comision_cuotas}</p>
//         <p><strong>Premio por productividad propia:</strong> $${premio_productividad_propia}</p>
//     </div>`;

//     if (tipo_colaborador.toLowerCase() === "supervisor") {
//         html += `
//         <div class="subDetalleGroup">
//             <h3>Equipo</h3>
//             <p><strong>Cantidad de ventas del equipo:</strong> ${rol.cantidadVentasXEquipo || 0}</p>
//             <p><strong>Productividad del equipo:</strong> $${rol.productividadXVentasEquipo || 0}</p>
//             <p><strong>Comision por cantidad de ventas del equipo:</strong> $${comision_ventas_equipo}</p>
//             <p><strong>Premio por cantidad de ventas del equipo:</strong> $${premio_ventas_equipo}</p>
//             <p><strong>Premio por productividad del equipo:</strong> $${premio_productividad_equipo}</p>
//         </div>`;
//     }

//     if (tipo_colaborador.toLowerCase() === "gerente sucursal") {

//         Object.values(rol).forEach(valor => {

//             const agenciaId = valor["suc_id"]
//             const agenciaName = valor["suc_name"]
//             const agenciaInfo = valor["suc_info"]
//             const premios_x_venta = valor["premios_por_venta"]
//             const sub_total = valor["sub_total"]
//             // <p><strong>Premio por cuotas 0:</strong> $${premios.premio_x_cantidad_ventas_agencia || 0}</p>

//             html += `
//                 <div class="subDetalleGroup">
//                     <h3>Sucursal ${agenciaName}</h3>
//                     <p><strong>Cantidad de cuotas 0:</strong> ${agenciaInfo.cantidad_cuotas_0 || 0}</p>
//                     <p><strong>Premio por cuotas 0:</strong> $${premios_x_venta}</p>


//                     <p><strong>Cantidad de cuotas 1:</strong> ${agenciaInfo.detalleCuota.cuotas1.cantidad || 0}</p>
//                     <p><strong>Comision por cuotas 1:</strong> $${agenciaInfo.detalleCuota.cuotas1.comision || 0}</p>

//                     <p><strong>Cantidad de cuotas 2:</strong> ${agenciaInfo.detalleCuota.cuotas2.cantidad || 0}</p>
//                     <p><strong>Comision por cuotas 2:</strong> $${agenciaInfo.detalleCuota.cuotas2.comision || 0}</p>

//                     <p><strong>Cantidad de cuotas 3:</strong> ${agenciaInfo.detalleCuota.cuotas3.cantidad || 0}</p>
//                     <p><strong>Comision por cuotas 3:</strong> $${agenciaInfo.detalleCuota.cuotas3.comision || 0}</p>

//                     <p><strong>Cantidad de cuotas 4:</strong> ${agenciaInfo.detalleCuota.cuotas4.cantidad || 0}</p>
//                     <p><strong>Comision por cuotas 4:</strong> $${agenciaInfo.detalleCuota.cuotas4.comision || 0}</p>

//                     <p><strong>Comision por cartera:</strong> ${sub_total || 0}</p>
//                 </div>`
//                 ;
//         });


//     }
//     html += `
//         <div class="subDetalleGroup asegurado">
//             <p><strong>Asegurado:</strong> $${asegurado}</p>
//         </div>`;

//     html += `
//         <div class="subDetalleGroup">
//             <h3>Ajustes manuales</h3>`;

//     if (ajustes.length === 0) {
//         html += `<p>No se aplicaron ajustes.</p>`;
//     } else {
//         ajustes.forEach((aj, i) => {
//             const signo = aj.ajuste_tipo === "positivo" ? "+" : "-";
//             html += `<p><strong>${signo}$${aj.dinero}</strong> - ${aj.observaciones || "Sin observaciones"}</p>`;
//         });
//         html += `<p><strong>Total ajustado:</strong> $${total_ajuste}</p>`;
//     }

//     html += `</div>
//         <div class="subDetalleGroup resumenTotalComision">
//             <h3>Total final de comisión:</h3>
//             <p><strong>$${comision_total}</strong></p>
//         </div>
//     </div>`;

//     return html;
// }

function render_detalle_comision(user_id, user_name, tipo_colaborador, otros_ajustes, detalle) {
    const ventas = detalle.info_total_de_comision.detalle.ventasPropias || {};
    const rol = detalle.info_total_de_comision.detalle.rol || {};
    const ajustes = otros_ajustes || [];
    const ventasPorSucursal = ventas.detalle || {};
    const rolPorSucursal = rol.detalle || {};
    const sucursalesKeys = [
        ...new Set([
            ...Object.keys(ventasPorSucursal),
            ...Object.keys(rolPorSucursal)
        ])
    ];

    // Calculamos ajustes totales
    let total_ajuste = 0;
    ajustes.forEach(aj => {
        total_ajuste += aj.ajuste_tipo === "positivo" ? aj.dinero : -aj.dinero;
    });

    // Extraemos datos generales
    const comision_total = detalle.comisionTotal;
    const asegurado = detalle.info_total_de_comision.asegurado;

    // Preparamos el HTML inicial
    let html = `
      <div class="wrapperDetalleLiquidacion">
        <h2>Detalle de ${user_name}</h2>
    `;

    sucursalesKeys.forEach(key => {
        const vp_suc = ventasPorSucursal[key] || {};
        const rp_suc = rolPorSucursal[key] || {};
        const sucName = vp_suc.suc_name || rp_suc.suc_name || key;

        html += `<div class="detalle_by_agencia"><h3>Sucursal ${sucName}</h3>`;

        // — Ventas propias en esta sucursal —
        if (vp_suc.cantidadVentas != null) {
            html += `

            <div class="subDetalleGroup">
                <h3>Ventas propias</h3>
                <p><strong>Ventas:</strong> ${vp_suc.cantidadVentas || 0}</p>
                <p><strong>Productividad:</strong> $${vp_suc.productividadXVentasPropias || 0}</p>
                <p><strong>Cuotas 1 pagadas:</strong> ${vp_suc.cantidadCuotas1 || 0}</p>
                <p><strong>Comisión por ventas:</strong> $${vp_suc.comision_subTotal || 0}</p>
                <p><strong>Comisión por cuotas 1:</strong> $${vp_suc.comision_x_cuotas1 || 0}</p>
                <p><strong>Premio productividad propia:</strong> $${vp_suc.comision_x_productividad || 0}</p>
            </div>
        `;
        }

        if (tipo_colaborador.toLowerCase() === "supervisor") {
            const r = detalle.info_total_de_comision.detalle.rol;
            html += `
            <div class="subDetalleGroup">
              <h3>Ventas del equipo</h3>
              <p><strong>Ventas:</strong> ${rp_suc.cantidad_ventas_x_equipo || 0}</p>
              <p><strong>Productividad:</strong> $${rp_suc.productividad_x_equipo || 0}</p>
              <p><strong>Comisión ventas equipo:</strong> $${rp_suc.comision_x_cantidad_ventas || 0}</p>
              <p><strong>Premio productividad equipo:</strong> $${rp_suc.comision_x_productividad || 0}</p>
              <p><strong>Premio ventas equipo:</strong> $${rp_suc.comision_x_ventas_equipo || 0}</p>
            </div>
          `;
        }
        else if (tipo_colaborador.toLowerCase() === "gerente sucursal") {
            html += `
            <div class="subDetalleGroup">
              <h3>Ventas de la agencia</h3>
              <p><strong>Cuotas 0:</strong> ${vp_suc.cantidad_cuotas_0 || 0}</p>
              <p><strong>Premio cuota 0:</strong> $${rp_suc.premios_por_venta || 0}</p>
          `;
            ["1", "2", "3", "4"].forEach(nro => {
                const det = rp_suc.suc_info.detalleCuota?.[`cuotas${nro}`] || {};
                html += `
                <p><strong>Cuota ${nro}:</strong> ${det.cantidad || 0} unidades — Comisión: $${det.comision || 0}</p>
            `;
            });
            // sub‐total sucursal
            html += `<p><strong>Sub‐total sucursal:</strong> $${rp_suc.sub_total || 0}</p></div>`;
        }

        html += `</div>`;
    });



    // --------------------------------------------------------
    // 4) Asegurado, ajustes y total final
    // --------------------------------------------------------
    html += `
        <div class="subDetalleGroup asegurado">
            <p><strong>Asegurado:</strong> $${asegurado}</p>
        </div>
        <div class="subDetalleGroup">
            <h3>Ajustes manuales</h3>`;
    if (ajustes.length === 0) {
        html += `<p>No se aplicaron ajustes.</p>`;
    } else {
        ajustes.forEach(aj => {
            const signo = aj.ajuste_tipo === "positivo" ? "+" : "-";
            html += `<p><strong>${signo}$${aj.dinero}</strong> – ${aj.observaciones || "Sin observaciones"}</p>`;
        });
        html += `<p><strong>Total ajustes:</strong> $${total_ajuste}</p>`;
    }
    html += `</div>
        <div class="subDetalleGroup resumenTotalComision">
            <h3>Total comisión:</h3>
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
        colaborador || {}
    );
}

function modal_more_info_comision(user_id, user_name, tipo_colaborador, otros_ajustes, detalle) {
    let modal = new tingle.modal({
        footer: true,
        closeMethods: [''],
        cssClass: ['moda_container_more_info'],
        onOpen: function () { },
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



// #region Para exportar datos que se esta liquidando
async function create_excel_detail_info(userId, campania, agenciaId) {

    const body = { user_id: userId, campania: campania, agencia_id: agenciaId };
    const csrftoken = getCookie("csrftoken");

    showLoader();
    const resp = await fetch(urlExportDetallesComision, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
    });
    hiddenLoader();

    if (!resp.ok) throw new Error("Error al generar Excel");
    const blob = await resp.blob();
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = resp.headers.get("filename");
    link.click();
}
// #endregion