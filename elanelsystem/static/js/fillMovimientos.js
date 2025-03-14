const buttonNext = document.getElementById("buttonNextMov")
const buttonBack = document.getElementById("buttonPreviousMov")
const cuotasPages = document.querySelector(".cuotasPages")
const containerMovimientos = document.querySelector(".values")
let cuotasButtons = document.querySelectorAll(".mov")
let movsPages = document.querySelector(".cuotasPages")

let currentPage = 1;

let inputsFilters = ""
let urlForFilter = ""
let appliedFilters = {};


// Funcion para actualizar la informacion de los movimientos
async function updateMovs(page) {
    let dataMovs = await movsGetChangePage(page); // Solicita los movimientos
    console.log(dataMovs)
    movsPages.textContent = page + " / " + dataMovs["numbers_pages"] // Actualiza en la pagina en la que estamos

    // textFilters(dataMovs["filtros"]) // Actualiza los filtros que estamos usando para mostrar los movimientos
    
    // Verifica si el numero de paginas solicitado es el maximo para blockear el boton de "siguiente"
    page == dataMovs["numbers_pages"] ? buttonNext.classList.add("blocked") : buttonNext.classList.remove("blocked");

    // Verifica si el numero de paginas solicitado es el minimo para blockear el boton de "atras"
    page == 1 ? buttonBack.classList.add("blocked") : buttonBack.classList.remove("blocked");

    // #region Logica para settear los totales de los diferentes tipo de pago 
    resumEfectivo.textContent = "$ " + dataMovs["estadoCuenta"]["efectivo"]
    resumBanco.textContent = "$ " + dataMovs["estadoCuenta"]["banco"]
    resumPosnet.textContent = "$ " + dataMovs["estadoCuenta"]["posnet"]
    resumMerPago.textContent = "$ " + dataMovs["estadoCuenta"]["merPago"]
    resumTrans.textContent = "$ " + dataMovs["estadoCuenta"]["transferencia"]
    resumTotal.textContent = "$ " + dataMovs["estadoCuenta"]["total"]
    // #endregion
    containerMovimientos.innerHTML = ""; // Limpiar el contenedor de movimientos antes de agregar los nuevos


    dataMovs["data"].forEach(element => {
        // Crea un nuevo elemento <li>
        const nuevoElementoLi = document.createElement("li");
        nuevoElementoLi.classList.add("mov");
        nuevoElementoLi.id = `${element.id_cont}`;

        nuevoElementoLi.innerHTML = createItemSegunMovimiento(element) // Establece el contenido HTML del <li> con un string

        containerMovimientos.appendChild(nuevoElementoLi); // Agrega el nuevo <li> al elemento padre (la lista)
    });
    cuotasButtons = document.querySelectorAll(".mov")

    cuotasButtons.forEach(cuota => {
        cuota.addEventListener('click', () => {
            let movSelected = dataMovs["data"].filter(c => c.id_cont == cuota.id)
            let typeMov = "concepto" in movSelected[0]
            modalViewMovimiento(movSelected[0], typeMov)
        })
    });
}

updateMovs(currentPage);

// #region Butones de paginas de movimientos
// Manejar clic en botón de siguiente página
buttonNext.addEventListener('click', () => {
    currentPage += 1;
    updateMovs(currentPage);
});

// Manejar clic en botón de página anterior
buttonBack.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage -= 1;
        updateMovs(currentPage);
    }
});
// #endregion


function createItemSegunMovimiento(mov) {
    let fechaRecortada = mov.fecha.data.slice(0, 10)
    let stringForHTML = `<div><p class="fecha">${fechaRecortada}</p></div>`
    if ("concepto" in mov) {
        let conceptoStringRecortado = mov.concepto.slice(0, 18);
        stringForHTML += `
        <div><p class="concept">${conceptoStringRecortado}</p></div>
        <div><p class="nCuotas"> - </p></div>
        `;
        if ("Ingreso" == mov["tipo_mov"]) {
            stringForHTML += `
            <div><p class="monto">$${mov.monto.data}</p></div>
            <div><p class="monto"> - </p></div>
            `;
        } else if ("Egreso" == mov["tipo_mov"]) {
            stringForHTML += `
            <div><p class="monto"> - </p></div>
            <div><p class="monto">$${mov.monto.data}</p></div>
            `;
        }
    } else {
        let conceptoStringRecortado = mov.nombre_del_cliente.data.slice(0, 18);
        let cuotaStringRecortada = mov.cuota.data.slice(5)
        stringForHTML += `
        <div><p class="concept">${conceptoStringRecortado}</p></div>
        <div><p class="nCuotas">${cuotaStringRecortada} </p></div>
        <div><p class="monto">$${mov.monto.data}</p></div>
        <div><p class="monto"> - </p></div>
        `;
    }
    return stringForHTML;
}


// Actualiza los filtros que estamos usando para mostrar los movimientos
function textFilters(dicc) {
    let stringForHTML = ""

    if (dicc.length != 0) {
        const wrapperFiltroTexto = document.querySelector(".wrapperFiltroTexto > ul")
        for (var i = 0; i < dicc.length; i++) {
            for (let clave in dicc[i]) {
                stringForHTML += `<li class="fitroItem">${clave}: <strong>${dicc[i][clave]}</strong></li>`;
            }
        }
        wrapperFiltroTexto.innerHTML = stringForHTML
    }
}

function modalViewMovimiento(mov, type_mov) {
    let modal = new tingle.modal({
        footer: true,
        closeMethods: [''],
        cssClass: ['modalContainerViewMov'],

        onOpen: function () {
            // enableAuditarButton()
        },
        onClose: function () {
            modal.destroy();
        },
    });

    // set content
    template = type_mov ? renderViewMovimiento(mov) : renderViewCannon(mov)
    modal.setContent(template);


    // add a button
    // modal.addFooterBtn('Auditar', 'tingle-btn tingle-btn--primary buttonAuditControl', async function () {

    //     let form = document.querySelector("#containerModularForm")
    //     showLoader()
    //     let response = await sendGradeVenta(form)
    //     console.log(response);

    //     if (response.status) {
    //         console.log("Salio todo bien");
    //         hiddenLoader();
    //         refreshVenta(response);

    //         const ventaElement = document.getElementById(venta_id);
    //         const button = ventaElement.querySelector('.displayDetailInfoButton'); // Ajusta el selector según tu caso
    //         if (button) toggleWrapperDetail(button);

    //         modal.close();
    //         modal.destroy();
    //     } else {
    //         console.log("Salio todo mal");
    //         hiddenLoader();

    //         modal.close();
    //         modal.destroy();
    //     }
    //     newModalMessage(response["message"], response["iconMessage"]);

    // });

    // add another button
    modal.addFooterBtn('Cerrar', 'tingle-btn tingle-btn--default button-default-style', function () {
        modal.close();
        modal.destroy();
    });

    // open modal
    modal.open();

    // // Se bloquea hasta que los campos esten todos completos
    // document.querySelector(".tingle-btn--primary").disabled = true;
}

function renderViewCannon(mov) {
    let stringForHTML = `
    <div class="cannon-info">
        <h2>Información del Cannon</h2>
        <div>
            <p><strong>Número de Venta:</strong></p>
            <div>
                <p>${mov["nro_operacion"]["data"]}</p>
            </div>
        </div>
        <div>
            <p><strong>Número de Cliente:</strong></p>
            <div>
                <p>${mov["nro_del_cliente"]["data"]}</p>
            </div>
        </div>
        <div>
            <p><strong>Número de Cuota:</strong></p>
            <div>
                <p>${mov["cuota"]["data"]}</p>
            </div>
        </div>
        <div>
            <p><strong>Monto:</strong></p>
            <div>
                <p>$${mov["monto"]["data"]}</p>
            </div>
        </div>
        <div>
            <p><strong>Método de Pago:</strong></p>
            <div>
                <p>${mov["metodoPago"]["data"]}</p>
            </div>
        </div>
        <div>
            <p><strong>Cobrador:</strong></p>
            <div>
                <p>${mov["cobrador"]["data"]}</p>
            </div>
        </div>
        <div>
            <p><strong>Fecha de Pago:</strong></p>
            <div>
                <p>${mov["fecha"]["data"]}</p>
            </div>
        </div>
        <div>
            <p><strong>Sucursal:</strong></p>
            <div>
                <p>${mov["agencia"]["data"]}</p>
            </div>
        </div>
    </div>
    `;
    return stringForHTML;
}

function renderViewMovimiento(mov) {
    let stringForHTML = `
    <div class="movimiento-info">
        <h2>Información del Movimiento</h2>
        <div>
            <p><strong>Tipo de Comprobante:</strong></p>
            <div>
                 <p>${mov["tipoComprobante"]}</p>
            </div>
        </div>
        <div>
            <p><strong>Número de Comprobante:</strong></p>
            <div>
                <p>${mov["nroComprobante"]}</p>
            </div>
        </div>
        <div>
            <p><strong>Tipo de Identificación:</strong></p> 
            <div>
                <p>${mov["tipoIdentificacion"]}</p>
            </div>
        </div>
        <div>
            <p><strong>Número de Identificación:</strong></p> 
            <div>
                <p>${mov["nroIdentificacion"]}</p>
            </div>
        </div>
        <div>
            <p><strong>Denominación:</strong></p> 
            <div>
                <p>${mov["denominacion"]}</p>
            </div>
        </div>
        <div>
            <p><strong>Tipo de Moneda:</strong></p> 
            <div>
                <p>${mov["tipoMoneda"]}</p>
            </div>
        </div>
        <div>
            <p><strong>Monto:</strong></p> 
            <div>
                <p>$${mov["monto"]}</p>
            </div>
        </div>
        <div>
            <p><strong>Método de Pago:</strong></p> 
            <div>
                <p>${mov["metodoPago"]}</p>
            </div>
        </div>
        <div>
            <p><strong>Fecha:</strong></p> 
            <div>
                <p>${mov["fecha"]}</p>
            </div>
        </div>
        <div>
            <p><strong>Ente:</strong></p> 
            <div>
                <p>${mov["ente"]}</p>
            </div>
        </div>
        <div>
            <p><strong>Concepto:</strong></p> 
            <div>
                <p>${mov["concepto"]}</p>
            </div>
        </div>
    </div>
    `;
    return stringForHTML;
}

// function renderViewMovimiento(mov) {
//     let stringForHTML = `
//     <form method="POST" class="containerModularForm" id="containerModularForm">
//         ${CSRF_TOKEN}
//         <input type="hidden" name="idVenta" id="idVenta" value="${venta_id}" readonly>
//         <h2>Selecciona el estado de la auditoria</h2>
//         <div class="wrapperButtonsGrade">
//             <div class="buttonsWrapper">
//                 <input type="radio" name="grade" id="aprobarI" value="a">
//                 <label for="aprobarI" id="aprobarLabel" class="labelInputGrade">Aprobar</label>
//                 <input type="radio" name="grade" id="desaprobarI" value="d">
//                 <label for="desaprobarI" id="desaprobarLabel" class="labelInputGrade">Desaprobar</label>
//             </div>
//         </div>
//         <div class="wrapperFormComentario">
//             <div class="wrapperInputComent">
//                 <label for="comentarioInput">Comentario</label>
//                 <textarea name="comentarioInput" id="comentarioInput" cols="30" rows="10"></textarea>
//             </div>
//         </div>
//     </form>
//     `;
//     return stringForHTML;
// }
{/* <div class="calendar" id="calendar"></div> */ }
function renderTemplateFormFilter(uniqueFechaId) {
    return `
        <form method="GET" id="filterForm" class="filterForm">
                <div class="wrapperCalendario wrapperTypeFilter wrapperSelectCustom">
                    <h3 class="labelInput">Fecha</h3>
                    <div class="containerCalendario">
                        <input id="${uniqueFechaId}" name="fecha" class="pseudo-input-select-wrapper filterInput" type="text" placeholder="Choose date" readonly />
                    </div>
                </div>

                <div id="selectWrapperSelectTypePayments" class="wrapperTypeFilter wrapperSelectCustom">
                    <h3 class="labelInput">Metodo de pago</h3>
                    <div class="containerInputAndOptions">
                      <img class="iconDesplegar" src="{% static 'images/icons/arrowDown.png' %}" alt="">
                      <input type="hidden" class="filterInput" name="metodoPago" id="tipoDePago" placeholder="Seleccionar" autocomplete="off" readonly>
                      <div class="multipleSelect pseudo-input-select-wrapper">
                            <h3></h3>
                      </div>
                      <ul class="list-select-custom options">
                            ${metodos_de_pago.map(mp => `
                                <li data-value="${mp.id}">${mp.nombre}</li>
                            `).join('')}
                      </ul>
                    </div>
                </div>

                <div id="selectWrapperSelectCobrador" class="wrapperSelectFilter wrapperInput wrapperSelectCustom">
                    <label class="labelInput">Cuenta de cobro</label>
                    <div class="containerInputAndOptions">
                        <img id="cobradorIconDisplay" class="iconDesplegar" src="{% static 'images/icons/arrowDown.png' %}" alt=""/>
                        
                        <input type="hidden" class="filterInput" name="cobrador" required="" autocomplete="off" maxlength="100" class="input-metodoPago">
                        
                        <div class="multipleSelect pseudo-input-select-wrapper">
                            <h3></h3>
                        </div>
                        <ul class="list-select-custom options">
                        ${cuentas_de_cobro.map(ag => `
                            <li data-value="${ag.id}">${ag.nombre}</li>
                        `).join('')}
                        </ul>
                    </div>
                </div>
                
                <div id="selectWrapperSelectAgency" class="wrapperTypeFilter wrapperSelectCustom">
                    <h3 class="labelInput">Agencia</h3>
                    <div class="containerInputAndOptions">
                      <img class="iconDesplegar" src="{% static 'images/icons/arrowDown.png' %}" alt="">
                      <input type="hidden" class="filterInput" name="agencia" id="sucursalInput" placeholder="Seleccionar" autocomplete="off" readonly>
                      <div class="multipleSelect pseudo-input-select-wrapper">
                            <h3></h3>
                        </div>
                      <ul class="list-select-custom options">
                        ${agencias.map(ag => `
                            <li data-value="${ag.id}">${ag.pseudonimo}</li>
                        `).join('')}
                      </ul>
                    </div>
                </div>
                
                <div id="selectWrapperSelectCampania" class="wrapperTypeFilter wrapperSelectCustom">
                    <h3 class="labelInput">Campaña</h3>
                    <div class="containerInputAndOptions">
                        <img class="iconDesplegar" src="{% static 'images/icons/arrowDown.png' %}" alt="">
                        <input type="hidden" class="filterInput" name="ente" id="campaniaInput" placeholder="Seleccionar" autocomplete="off" readonly>
                        <div class="multipleSelect pseudo-input-select-wrapper">
                            <h3></h3>
                        </div>
                        <ul class="list-select-custom options">
                            ${campanias.map(ca => `
                                <li data-value="${ca}">${ca}</li>
                            `).join('')}
                        </ul>
                    </div>
                </div>

                <div id="selectWrapperSelectCampania" class="wrapperTypeFilter wrapperSelectCustom">
                    <h3 class="labelInput">Tipo de Movimiento</h3>
                    <div class="containerInputAndOptions">
                        <img class="iconDesplegar" src="{% static 'images/icons/arrowDown.png' %}" alt="">
                        <input type="hidden" class="filterInput" name="tipo_mov" id="campaniaInput" placeholder="Seleccionar" autocomplete="off" readonly>
                        <div class="multipleSelect pseudo-input-select-wrapper">
                              <h3></h3>
                        </div>
                        <ul class="list-select-custom options">
                            <li data-value="Ingreso">Ingreso</li>
                            <li data-value="Egreso">Egreso</li>
                        </ul>
                    </div>
                </div>          
            </form>
    `

}

function modalFilter() {
    console.log(appliedFilters)

    let modal = new tingle.modal({
        footer: true,
        closeMethods: ['overlay', 'button', 'escape'],
        cssClass: ['modalContainerFilter'],

        onOpen: function () {
            // enableAuditarButton()
            initMultipleCustomSelects(appliedFilters)
        },
        onClose: function () {
            deleteCalendarDOM()
            modal.destroy();
        },
    });

    // set content

    let uniqueFechaId = 'newFecha_' + Date.now();
    template = renderTemplateFormFilter(uniqueFechaId)
    modal.setContent(template);
    initSelectFecha(document.getElementById(`${uniqueFechaId}`))
    ordersZindexSelects()

    inputsFilters = document.querySelectorAll('.filterInput')
    
    // add a button
    modal.addFooterBtn('Filtrar', 'tingle-btn tingle-btn--primary add-button-default', async function () {
        let response = await movsGetFilter(inputsFilters)
        storeAppliedFilters(inputsFilters)
        if (response.status) {
            console.log("Salio todo bien");
            // hiddenLoader();
            updateMovs(currentPage);
            modal.close();
            modal.destroy();
        } else {
            console.log("Salio todo mal");
            // hiddenLoader();
            modal.close();
            modal.destroy();
        }
    });

    // add another button
    modal.addFooterBtn('Cancelar', 'tingle-btn tingle-btn--default button-default-style', function () {
        modal.close();
        modal.destroy();
    });

    // open modal
    modal.open();
}


// Funcion para obtener todos los movimientos por pagina 
async function movsGetFilter(inputs) {
    let url = createParamsUrl(inputs)
    console.log(`inputs: ${inputs}`)
    console.log(`url: ${url}`)
    urlForFilter = url

    const response = await fetch(`/requestmovs/?page=1${urlForFilter}`, {
        method: 'get',
        headers: { 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' },
        // cache: 'no-store',
    });
    if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
    }
    const data = await response.json();
    return data;
}


async function movsGetChangePage(page) {
    let url = `/requestmovs/?page=${page}${urlForFilter}`
    const response = await fetch(url, {
        method: 'get',
        headers: { 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' },
        // cache: 'no-store',
    });
    if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
    }
    const data = await response.json();
    return data;
}

function createParamsUrl(inputs) {
    let urlParams = ""

    inputs.forEach(input => {
        if (input.value.trim() !== "") {
            urlParams += "&";

            const inputName = input.name; // Obtener el atributo 'name' del input
            const inputValue = input.value; // Obtener el valor seleccionado
            let newParam = `${inputName}=${inputValue}`;
            urlParams += newParam;
        }
    })
    return urlParams
}


function storeAppliedFilters(inputs) {
    appliedFilters = {};
    inputs.forEach(input => {
        if (input.value.trim() !== "") {
            let textElement = input.parentElement.querySelector('h3');
            appliedFilters[input.name] = { "data": input.value, "text": textElement.textContent };
        }
    });
}

