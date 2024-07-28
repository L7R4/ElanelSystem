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
    let tipo_producto_image = `<img src="/static/images/icons/moto_icon.svg" alt="">`
    if (venta.tipo_producto === 'Prestamo') {
        tipo_producto_image = `<img src="/static/images/icons/soluciones_dinerarias_icon.svg" alt="">`
    } else if (venta.tipo_producto === 'Electrodomestico') {
        tipo_producto_image = `<img src="/static/images/icons/combos_icon.svg" alt="">`
    }


    // Para verificar si la venta tiene plan de recupero
    let buttonPlanRecupero = ''
    if (venta.cuotas_atrasadas >= 4) {
        buttonPlanRecupero = `<div class="urlsWrapper"><a href="${venta.urlSimularPlanRecupero}" class="add-button-default">Simular plan recupero</a></div>`
    }

    let string = `<li class="operationItem">
                    <div class="iconWrapper">
                        ${tipo_producto_image}
                    </div>
                    <div class="attributes">
                        <div class="nameStatus">
                            <h1>${venta.producto}</h1>
                            <img src="/static/images/icons/operationSuspendido.svg" alt="">
                            <h3>Suspendida</h3>
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
                    <a href="/ventas/detalle_venta/1/" class="buttonMore">
                            <div>
                                <h3>Ver mas</h3>
                                <img src="/static/images/icons/nextSinBackground.png" alt="">
                            </div>
                        </a>
                    
                </li>`
    return string;
}

function createMessageHTML(message) {
    let string = `<div class="wrapperMessage">
                        <h2 class="messageInfoVacio">${message}</h2>
                    </div>`
    return string;
}