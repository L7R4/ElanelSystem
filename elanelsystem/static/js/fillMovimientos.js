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

    movsPages.textContent = page + " / " + dataMovs["numbers_pages"] // Actualiza en la pagina en la que estamos

    textFilters(dataMovs["filtros"]) // Actualiza los filtros que estamos usando para mostrar los movimientos

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
            mainModal.classList.add("active")
            mainModal.style.opacity = "1"
            let movSelected = dataMovs["data"].filter(c => c.id_cont == cuota.id)
            let typeMov = "concepto" in movSelected[0]
            fillModalWithMovData(movSelected[0], typeMov)
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

closeModalMovsButtons.forEach(element => {
    element.addEventListener('click', () => {
        mainModal.style.opacity = "0"
        setTimeout(() => {
            modalForMovsExternos.style.visibility = "hidden"
            modalForCuotas.style.visibility = "hidden"
            mainModal.classList.remove("active")
        }, 300)

    })
});






function createItemSegunMovimiento(mov) {
    let fechaRecortada = mov.fecha.slice(0, 10)

    let stringForHTML = `<div><p class="fecha">${fechaRecortada}</p></div>`
    if ("concepto" in mov) {
        let conceptoStringRecortado = mov.concepto.slice(0, 18);
        stringForHTML += `
        <div><p class="concept">${conceptoStringRecortado}</p></div>
        <div><p class="nCuotas"> - </p></div>
        `;
        if ("Ingreso" == mov["tipo_mov"]) {
            stringForHTML += `
            <div><p class="monto">$${mov.pagado}</p></div>
            <div><p class="monto"> - </p></div>
            `;
        } else if ("Egreso" == mov["tipo_mov"]) {
            stringForHTML += `
            <div><p class="monto"> - </p></div>
            <div><p class="monto">$${mov.pagado}</p></div>
            `;
        }
    } else {
        let conceptoStringRecortado = mov.nombre_del_cliente.slice(0, 18);
        let cuotaStringRecortada = mov.cuota.slice(5)
        stringForHTML += `
        <div><p class="concept">${conceptoStringRecortado}</p></div>
        <div><p class="nCuotas">${cuotaStringRecortada} </p></div>
        <div><p class="monto">$${mov.pagado}</p></div>
        <div><p class="monto"> - </p></div>
        `;
    }
    return stringForHTML;
}

// Actualiza rellena el modal de acuerdo al tipo de 

function fillModalWithMovData(mov, movSelected) {
    console.log(mov)
    if (movSelected) {
        if (mov["tipo_mov"] == "Ingreso") {
            inputsOnlyEgreso.forEach(element => element.style.display = "none");
            inputsOnlyIngreso.forEach(element => element.style.display = "unset");
        } else {
            inputsOnlyIngreso.forEach(element => element.style.display = "none");
            inputsOnlyEgreso.forEach(element => element.style.display = "unset");
        }
        modalForMovsExternos.style.visibility = "visible"

        tipoComprobanteMovExterno.innerHTML = mov["tipoComprobante"]
        nroComprobanteMovExterno.innerHTML = mov["nroComprobante"]
        tipoIdentificaionMovExterno.innerHTML = mov["tipoIdentificacion"]
        nroIdentificacionMovExterno.innerHTML = mov["nroIdentificacion"]
        denominacionMovExterno.innerHTML = mov["denominacion"]
        tipoMonedaMovExterno.innerHTML = mov["tipoMoneda"]
        dineroMovExterno.innerHTML = mov["pagado"]
        metodoPagoMovExterno.innerHTML = mov["tipo_pago"]
        fechaMovExterno.innerHTML = mov["fecha"]
        enteMovExterno.innerHTML = mov["ente"]
        conceptoMovExterno.innerHTML = mov["concepto"]

    } else {
        modalForCuotas.style.visibility = "visible"

        numeroVenta.innerHTML = mov["nro_operacion"]
        numeroCliente.innerHTML = mov["nro_cliente"]
        numeroCuota.innerHTML = mov["cuota"]
        dinero.innerHTML = mov["pagado"]
        metodoPago.innerHTML = mov["tipo_pago"]
        cobrador.innerHTML = mov["cobrador"]
        fechaPago.innerHTML = mov["fecha"]
        sucursal.innerHTML = mov["sucursal"]

    }

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






