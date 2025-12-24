let contendorColaboradores = document.querySelector(".listColaboradoresWrapper > .valuesWrapper > .values ")
const radioFiltros = document.querySelectorAll('.inputSelectTipoColaborador');


let colaboradoresAFiltrar = "todos"
let body = {}
let allColaboradoresData = [];

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
        allColaboradoresData = response.colaboradores_data;
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
        allColaboradoresData = response.colaboradores_data;
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


//#region  Filtros de search colaboradores - - - - - - - - - - - - - - - - -

const searchInput = document.querySelector(".searchColaboradores input");
searchInput.addEventListener("input", () => {
    const term = searchInput.value.trim().toLowerCase();
    // Filtramos contra allColaboradoresData
    const filtrados = allColaboradoresData
        .filter(item => !item.tipo_colaborador.includes("Administracion"))
        .filter(item => item.nombre.toLowerCase().includes(term));
    actualizarResultadosColaboradores(filtrados, contendorColaboradores);
});
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
            <p class="name_user">${item.nombre}</p>
        </div>
        <div class="wrapperComisionColaborador">
            <p class="type_user" >${item.tipo_colaborador}</p>
        </div>
        <div class="wrapperComisionColaborador">
            <p>${formatMoney(item.comisionTotal)}</p>
        </div>
        <div class="wrapperActionsColaborador">
            <button type="button" class="button-default-style ajusteComisionButton" onclick="modal_ajuste_comision(${item.id}, '${item.nombre}', ${item.comisionTotal})">Ajustar comision</button>
            <button type="button" class="iconInfoMore moreInfoComisionButton" onclick="modal_more_info_comision_by_id(${item.id})"><img src=${info_icon} alt=""></button>
            <button type="button" class="iconInfoMore moreInfoComisionButton" onclick="create_excel_detail_info(${item.id},'${inputCampania.value}',${inputSucursal.value})"><img src=${export_icon} alt=""></button>
            ${item.egreso == 1 ? "<div class='status_egreso'></div>" : ""}
        </div>
        
    </li > `;
        contenedor.insertAdjacentHTML("beforeend", divs)

    });
}

function actualizarTotalComisionado(dinero) {
    const spanDinero = document.querySelector("#dineroTotalComisiones");
    let inputDinero = document.querySelector("#totalComisionesInput");
    if (spanDinero) {
        const dineroFormateado = formatMoney(dinero);
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
    return `< a target = "_blank" href = "${urlVentasNoComisionables}" class= "wrapperMessage ${type}" >
    <h3><strong>Alerta</strong> ${messaje} <span>(click para ver)</span></h3>
        </a > `
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

function render_detalle_comision(user_id, user_name, tipo_colaborador, otros_ajustes, detalle) {
    const ventas = detalle.info_total_de_comision.detalle.ventasPropias || {};
    const dias_trabajados = detalle.info_total_de_comision.dias_trabajados
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
        <div class= "wrapperDetalleLiquidacion">
        <div class="titleDetalleLiquidacion">
            <h2>Detalle de ${user_name}</h2>
            <p>${tipo_colaborador}</p>
            <p>${dias_trabajados >= 30 ? "+" : ""}${dias_trabajados} dias</p>

        </div>
    `;

    if (sucursalesKeys.length != 0) {
        sucursalesKeys.forEach(key => {
            console.log(inputSucursal.value)
            console.log(detalle.sucursal)

            const vp_suc = ventasPorSucursal[key] || {};
            const rp_suc = rolPorSucursal[key] || {};
            const sucName = vp_suc.suc_name || rp_suc.suc_name || key;
            const idSuc = vp_suc.suc_id || rp_suc.suc_id

            html += `<div class= "detalle_by_agencia" > <h3>Sucursal ${sucName}</h3>`;
            if (vp_suc == {}) {
                html += `
    <div class= "subDetalleGroup">
                <h3>Ventas propias</h3>
                <div>
                    <p class="messageBackground">No hubo ventas propias</p>
                </div>
            </div >
        `
            } else {
                html += `
        <div class= "subDetalleGroup">
                <h3>Ventas propias</h3>
                <div>
                    <p>Ventas <strong>${vp_suc.cantidadVentas || 0}</strong></p>
                    <p>Productividad <strong>${formatMoney(vp_suc.productividadXVentasPropias || 0)}</strong></p>
                    <p>Cuotas 1 pagadas <strong>${vp_suc.cantidadCuotas1 || 0}</strong></p>
                    <p>Comisión por ventas <strong>${formatMoney(vp_suc.comision_subTotal || 0)}</strong></p>
                    <p>Comisión por cuotas 1 <strong>${formatMoney(vp_suc.comision_x_cuotas1 || 0)}</strong></p>
                    <p>Premio productividad propia <strong>${formatMoney(vp_suc.comision_x_productividad || 0)}</strong></p>
                    ${parseInt(idSuc) == parseInt(inputSucursal.value)
                        ?
                        `<p>Asegurado <strong>${formatMoney(asegurado)}</strong></p>`
                        :
                        ""
                    }
                </div>
            </div >
        `;

            }

            if (tipo_colaborador.toLowerCase() === "supervisor") {
                const r = detalle.info_total_de_comision.detalle.rol;
                html += `
        <div class= "subDetalleGroup">
                <h3>Ventas del equipo</h3>
                <div>
                    <p>Ventas <strong>${rp_suc.cantidad_ventas_x_equipo || 0}</strong></p>
                    <p>Productividad <strong>${formatMoney(rp_suc.productividad_x_equipo || 0)}</strong></p>
                    <p>Comisión ventas equipo <strong>${formatMoney(rp_suc.comision_x_cantidad_ventas || 0)}</strong></p>
                    <p>Premio productividad equipo <strong>${formatMoney(rp_suc.comision_x_productividad || 0)}</strong></p>
                    <p>Premio ventas equipo <strong>${formatMoney(rp_suc.comision_x_ventas_equipo || 0)}</strong></p>
                </div>
            </div>
        `;
            }
            else if (tipo_colaborador.toLowerCase() === "gerente sucursal") {
                html += `
        <div class= "subDetalleGroup">
              <h3>Ventas de la agencia</h3>
              <div>
                <p>Cuotas 0<strong>${rp_suc.suc_info.cantidad_cuotas_0 || 0}</strong></p>
                <p>Premio cuota 0<strong>${formatMoney(rp_suc.premios_por_venta || 0)}</strong></p>
              `;
                ["1", "2", "3", "4"].forEach(nro => {
                    const det = rp_suc.suc_info.detalleCuota?.[`cuotas${nro}`] || {};
                    html += `
                <p>Cuota ${nro} <strong>${det.cantidad || 0} - ${formatMoney(det.comision || 0)}</strong></p>`;
                });
                // sub‐total sucursal
                html += `
                <p class="subTotalAgenciaGerente">Sub‐total de sucursal<strong>${formatMoney(rp_suc.sub_total || 0)}</strong></p></div>
                </div> `;
            }

            html += `</div> `;
        });
    } else {
        html += `
    <div class= "subDetalleGroup">
    <div>
        <p class="messageBackground">El ${tipo_colaborador} no tuvo movimientos</p>
    </div>
        </div>
        `;

    }



    // --------------------------------------------------------
    // 4) Asegurado, ajustes y total final
    // --------------------------------------------------------
    html += `
        <div class= "subDetalleGroup">
        <h3>Ajustes manuales</h3>`;
    if (ajustes.length === 0) {
        html += `<p class= "messageBackground"> No se aplicaron ajustes</p > `;
    } else {
        ajustes.forEach(aj => {
            const signo = aj.ajuste_tipo === "positivo" ? "+" : "-";
            html += `<p> <strong>${signo}$${aj.dinero}</strong> – ${aj.observaciones || "Sin observaciones"}</p> `;
        });
        html += `<p> <strong>Total ajustes:</strong> $${total_ajuste}</p> `;
    }
    html += `</div>
    <div class="resumenTotalComision">
        <h3>Total comisión</h3>
        <p>${formatMoney(comision_total)}</p>
    </div>
        </div> `;

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