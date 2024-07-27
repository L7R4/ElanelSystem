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

async function fetchVenta(url,body) {
    try {
        let response = await fetch(url,{
            method:'POST',
            body:JSON.stringify(body),
            headers:{
                'Content-Type':'application/json',
                'X-CSRFToken':getCookie('csrftoken')
            }
            
        }) 
        if (!response.ok) {
            throw new Error('Ocurrio un error al buscar la venta')
        }
        let data = await response.json()
        return data;
    } catch (error) {}
}
if (!response.ok) {
    throw new Error('Ocurrio un error al buscar la venta')
}


inputNroVenta.addEventListener('input', async()=>{
    let venta = await fetchVenta(window.location.pathname,{'nro_orden':inputNroVenta.value})
    wrapperOperaciones.innerHTML = ''
    wrapperOperaciones.insertAdjacentHTML('beforeend',createVentaHTML(venta["venta"]))
})

function createVentaHTML(venta) {
    let string = `<li class="operationItem">
                    <div class="iconWrapper">
                        <img src="/static/images/icons/iconMoto.png" alt="">
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
                            <h3>${venta.saldo_Afavor}</h3>
                        </div>
                        <div class="information">
                            <h2>Cuotas pagadas</h2>
                            <h3>${venta.cuotas_pagadas}</h3>
                        </div>
                    </div>
                </li>`
    return string;
}