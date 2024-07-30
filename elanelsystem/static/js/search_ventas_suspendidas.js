let inputNroVenta = document.querySelector("#nro_ordenInput")
let wrapperOperaciones = document.querySelector(".operationsList")

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

async function fetchVenta(url, body) {
    try {
        let response = await fetch(url, {
            method: 'POST',
            body: JSON.stringify(body),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }

        })
        if (!response.ok) {
            throw new Error('Ocurrio un error al buscar la venta')
        }
        let data = await response.json()
        return data;
    } catch (error) { }
}



inputNroVenta.addEventListener('input', async () => {
    wrapperOperaciones.innerHTML = ''
    if (inputNroVenta.value != '') {
        let venta = await fetchVenta(window.location.pathname, { 'nro_operacion': inputNroVenta.value })
        console.log(venta)
        if (venta["venta"] != null) {
            wrapperOperaciones.insertAdjacentHTML('beforeend', createVentaHTML(venta["venta"]))
        } else {
            let message = "No se encontro ninguna venta con ese número"
            wrapperOperaciones.insertAdjacentHTML('beforeend', createMessageHTML(message))
        }
    } else {
        let message = "Coloque el numero de venta para filtrar la venta"
        wrapperOperaciones.insertAdjacentHTML('beforeend', createMessageHTML(message))
    }
})

function createVentaHTML(venta) {
    // Para elegir imagen segun el tipo de producto
    let tipo_producto_image = `<img class="iconProducto" src="/static/images/icons/moto_icon.svg" alt="">`
    if (venta.tipo_producto === 'Prestamo') {
        tipo_producto_image = `<img class="iconProducto" src="/static/images/icons/soluciones_dinerarias_icon.svg" alt="">`
    } else if (venta.tipo_producto === 'Electrodomestico') {
        tipo_producto_image = `<img class="iconProducto" src="/static/images/icons/combos_icon.svg" alt="">`
    }


    // Para verificar si la venta tiene plan de recupero
    let buttonPlanRecupero = ''
    let operationStatusImage = `<img class="iconStatus" src="/static/images/icons/operationSuspendido.svg" alt=""></img>`
    let operationStatusText = `<h3>Suspendida</h3>`
    if (venta.cuotas_atrasadas >= 4) {
        operationStatusImage = `<img class="iconStatus" src="/static/images/icons/operationBaja.svg" alt=""></img>`
        operationStatusText = `<h3>De baja</h3>`
        buttonPlanRecupero = `<a href="${venta.urlSimularPlanRecupero}" class="buttonSimulacro add-button-default" target="_blank"><h3>Simular plan recupero</h3></a>`
    }

    let string = `<li class="operationItem">
                    <div class="nameStatus">
                        ${tipo_producto_image}
                        <h1>${venta.producto}</h1>
                        ${operationStatusImage}
                        ${operationStatusText}
                    </div>
                    <div class="attributes">
                        <div class="information" id="cliente_information">
                            <h2>Cliente</h2>
                            <h3>${venta.cliente}</h3>
                        </div>

                        <div class="information">
                            <h2>Importe</h2>
                            <h3>$${venta.importe}</h3>
                        </div>
                        
                        <div class="information">
                            <h2>N° Orden</h2>
                            <h3>${venta.nro_orden}</h3>
                        </div>
                        <div class="information">
                            <h2>Fecha Inscripcion</h2>
                            <h3>${venta.fecha_inscripcion}</h3>
                        </div>
                        <div class="information">
                            <h2>N° Operacion</h2>
                            <h3>${venta.nro_operacion}</h3>
                        </div>
                        <div class="information">
                            <h2>Cuotas atrasadas</h2>
                            <h3>${venta.cuotas_atrasadas}</h3>
                        </div>
                        <div class="information">
                            <h2>Saldo a favor</h2>
                            <h3>$${venta.saldo_Afavor}</h3>
                        </div>
                        <div class="information">
                            <h2>Cuotas pagadas</h2>
                            <h3>${venta.cuotas_pagadas}</h3>
                        </div>
                    </div>
                    ${buttonPlanRecupero}
                    
                </li>`
    return string;
}

function createMessageHTML(message) {
    let string = `<div class="wrapperMessage">
                        <h2 class="messageInfoVacio">${message}</h2>
                    </div>`
    return string;
}