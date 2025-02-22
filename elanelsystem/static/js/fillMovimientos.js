const buttonNext = document.getElementById("buttonNextMov")
const buttonBack = document.getElementById("buttonPreviousMov")
const cuotasPages = document.querySelector(".cuotasPages")
const containerMovimientos = document.querySelector(".values")
let cuotasButtons = document.querySelectorAll(".mov")
let movsPages = document.querySelector(".cuotasPages")

const mainModal = document.querySelector(".main_modalCuota")
const closeModalMovsButtons = document.querySelectorAll(".closeModalCuotaInformation")
const queryString = window.location.search;
let currentPage = 1;
const inputsOnlyEgreso = document.querySelectorAll(".onlyEgreso")
const inputsOnlyIngreso = document.querySelectorAll(".onlyIngreso")


// Funcion para obtener todos los movimientos por pagina 
async function movsGet(page) {
    const response = await fetch(`/requestmovs/?page=${page}&` + queryString.slice(1), {
        method: 'get',
        headers: { 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' },
        cache: 'no-store',
    });
    if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
    }
    const data = await response.json();
    return data;
}

// Funcion para actualizar la informacion de los movimientos
async function updateMovs(page) {
    let dataMovs = await movsGet(page); // Solicita los movimientos
    console.log(dataMovs)
    movsPages.textContent = page + " / " + dataMovs["numbers_pages"] // Actualiza en la pagina en la que estamos

    textFilters(dataMovs["filtros"]) // Actualiza los filtros que estamos usando para mostrar los movimientos
    refillFilterValues()
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
            <div><p class="monto">$${mov.monto}</p></div>
            <div><p class="monto"> - </p></div>
            `;
        } else if ("Egreso" == mov["tipo_mov"]) {
            stringForHTML += `
            <div><p class="monto"> - </p></div>
            <div><p class="monto">$${mov.monto}</p></div>
            `;
        }
    } else {
        let conceptoStringRecortado = mov.nombre_del_cliente.data.slice(0, 18);
        let cuotaStringRecortada = mov.cuota.data.slice(5)
        stringForHTML += `
        <div><p class="concept">${conceptoStringRecortado}</p></div>
        <div><p class="nCuotas">${cuotaStringRecortada} </p></div>
        <div><p class="monto">$${mov.monto}</p></div>
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


function refillFilterValues() {
    const queryString = window.location.search;
    const params = new URLSearchParams(queryString);


    document.querySelectorAll('#filterForm input[name]').forEach(input => {
        const paramName = input.name; // Nombre del parámetro del input
        const paramValue = params.get(paramName); // Obtiene el valor del parámetro de la URL

        // Si existe un valor para ese parámetro, lo asigna al input
        if (paramValue) {
            input.value = paramValue;

            // Si el input es de tipo radio, selecciona el radio button correspondiente
            if (input.type === 'radio' && input.value === paramValue) {
                input.checked = true;
            }

            // Si el input es de tipo texto (como los menús desplegables), actualiza el menú
            if (input.type === 'text') {
                const list = input.nextElementSibling; // La lista desplegable asociada
                if (list) {
                    list.querySelectorAll('li').forEach(li => {
                        if (li.getAttribute('data-value') === paramValue) {
                            li.classList.add('selected');
                        } else {
                            li.classList.remove('selected');
                        }
                    });
                }
            }
        }
    });
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
    console.log(mov)
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
