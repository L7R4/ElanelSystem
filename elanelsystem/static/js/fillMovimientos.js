const buttonNext = document.getElementById("buttonNextMov")
const buttonBack = document.getElementById("buttonPreviousMov")
const cuotasPages = document.querySelector(".cuotasPages")
const containerMovimientos = document.querySelector(".values")
let cuotasButtons =  document.querySelectorAll(".mov")
let movsPages = document.querySelector(".cuotasPages")

const mainModal = document.querySelector(".main_modalCuota")
const closeModalButtons = document.querySelectorAll(".closeModal")
const queryString = window.location.search;
let currentPage = 1;
const inputsOnlyEgreso = document.querySelectorAll(".onlyEgreso")



async function movsGet(page) {
    const response = await fetch(`/requestmovs/?page=${page}&` + queryString.slice(1), {
        method: 'get',
        headers: {'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'},
        cache: 'no-store',
    });
    const data = await response.json();
    return data;
}

async function updateMovs(page) {
    let dataMovs = await movsGet(page);
    movsPages.textContent = page + " / " + dataMovs["numbers_pages"]
    textFilters(dataMovs["filtros"])
    // Verifica si el numero de paginas solicitado es el maximo para blockear el boton de "siguiente"
    page == dataMovs["numbers_pages"] ? buttonNext.classList.add("blocked") : buttonNext.classList.remove("blocked");
    
    // Verifica si el numero de paginas solicitado es el minimo para blockear el boton de "atras"
    page == 1 ? buttonBack.classList.add("blocked") : buttonBack.classList.remove("blocked");

    
    // Limpiar el contenedor de movimientos antes de agregar los nuevos
    containerMovimientos.innerHTML = "";
    // console.log(dataMovs["data"])
    dataMovs["data"].forEach(element => {
        // Crea un nuevo elemento <li>
        const nuevoElementoLi = document.createElement("li");
        nuevoElementoLi.classList.add("mov");
        nuevoElementoLi.id = `${element.idMov}`;
        // Establece el contenido HTML del <li> con un string
        nuevoElementoLi.innerHTML = createItemSegunMovimiento(element)
        // Agrega el nuevo <li> al elemento padre (la lista)
        containerMovimientos.appendChild(nuevoElementoLi);
    });
    cuotasButtons =  document.querySelectorAll(".mov")
    
    cuotasButtons.forEach(cuota => {
        cuota.addEventListener('click', ()=>{
            mainModal.classList.add("active")
            mainModal.style.opacity = "1"
            let movSelected = dataMovs["data"].filter(c=> c.idMov == cuota.id)
            let typeMov = "concepto" in movSelected[0]
            fillModalWithMovData(movSelected[0],typeMov)
        })
    });
}

updateMovs(currentPage);




// Manejar clic en botón de siguiente página
buttonNext.addEventListener('click', () => {
    currentPage += 1 ;
    updateMovs(currentPage);
});

// Manejar clic en botón de página anterior
buttonBack.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage -= 1 ;
        updateMovs(currentPage);
    }
});

closeModalButtons.forEach(element => {
    element.addEventListener('click', ()=>{
        mainModal.style.opacity = "0"
        setTimeout(()=>{
            modalForMovsExternos.style.visibility = "hidden"
            modalForCuotas.style.visibility = "hidden"
            mainModal.classList.remove("active")
    
        },300)
    
    })
});

function createItemSegunMovimiento(mov) {
    let fechaRecortada = mov.fecha_pago.slice(0,10)
    let stringForHTML = `<div><p class="fecha">${fechaRecortada}</p></div>`
    if("concepto" in mov){
        let conceptoStringRecortado = mov.concepto.slice(0,18);
        stringForHTML +=`
        <div><p class="concept">${conceptoStringRecortado}</p></div>
        <div><p class="nCuotas"> - </p></div>
        `;
        if("Ingreso" == mov["tipoMovimiento"]){
            stringForHTML +=`
            <div><p class="monto">$${mov.pagado}</p></div>
            <div><p class="monto"> - </p></div>
            `;  
        }else if("Egreso" == mov["tipoMovimiento"]){
            stringForHTML +=`
            <div><p class="monto"> - </p></div>
            <div><p class="monto">$${mov.pagado}</p></div>
            `;  
        }
    }else{
        let conceptoStringRecortado = mov.nombreCliente.slice(0,18);
        let cuotaStringRecortada = mov.cuota.slice(5)
        stringForHTML +=`
        <div><p class="concept">${conceptoStringRecortado}</p></div>
        <div><p class="nCuotas">${cuotaStringRecortada} </p></div>
        <div><p class="monto">$${mov.pagado}</p></div>
        <div><p class="monto"> - </p></div>
        `;
    }
    return stringForHTML;
}

function fillModalWithMovData(mov,movSelected) {
    if(movSelected){
        if(mov["tipoMovimiento"] == "Ingreso"){
            inputsOnlyEgreso.forEach(element => element.style.display = "none");
        }else{
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
        metodoPagoMovExterno.innerHTML = mov["metodoPago"]
        fechaMovExterno.innerHTML = mov["fecha_pago"]
        enteMovExterno.innerHTML = mov["ente"]
        conceptoMovExterno.innerHTML = mov["concepto"]

    }else{
        modalForCuotas.style.visibility = "visible"

        numeroVenta.innerHTML = mov["nro_operacion"]
        numeroCliente.innerHTML = mov["nroCliente"]
        numeroCuota.innerHTML = mov["cuota"]
        dinero.innerHTML = mov["pagado"]
        metodoPago.innerHTML = mov["metodoPago"]
        cobrador.innerHTML = mov["cobrador"]
        fechaPago.innerHTML = mov["fecha_pago"]
        horaPago.innerHTML = mov["hora"]
        sucursal.innerHTML = mov["sucursal"]
        
    }
    
}


function updateResumenDinero(page) {
    fetch(`/updatedinero/?page=${page}&` + queryString.slice(1))  
        .then(response => response.json())
        .then(data => {
            resumEfectivo.textContent = "$ " + data["efectivo"]
            resumBanco.textContent = "$ " + data["banco"]
            resumPosnet.textContent = "$ " + data["posnet"]
            resumMerPago.textContent = "$ " + data["merPago"]
            resumTrans.textContent = "$ " + data["transferencia"]
            resumTotal.textContent = "$ " + data["total"]
        })
        .catch(error => console.error('Error al realizar la solicitud:', error));
}
updateResumenDinero(currentPage);

function textFilters(dicc) {
    let stringForHTML =""
    
    if(dicc.length != 0){
        console.log(dicc)
        const wrapperFiltroTexto = document.querySelector(".wrapperFiltroTexto > ul")
        console.log(wrapperFiltroTexto)
        for (var i = 0; i < dicc.length; i++) {
            for (let clave in dicc[i]) {
                stringForHTML +=`<li class="fitroItem">${clave}: <strong>${dicc[i][clave]}</strong></li>`;   
            }
        }
        
        wrapperFiltroTexto.innerHTML = stringForHTML
    }   
} 
    





