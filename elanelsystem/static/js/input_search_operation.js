const inputSearchOperation = document.getElementById("operation")
const inputSearchProducto = document.getElementById("productoInput")
let listData = document.querySelectorAll(".operationItem");
const containerData = document.querySelector(".operationsList")
let buttonSubmitSearch = document.getElementById("submitSearchVenta")
let operationsList = document.querySelector(".operationsList")

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

// Para habilitar el boton de buscar
inputSearchOperation.addEventListener("input", () => {
    buttonSubmitSearch.disabled = inputSearchOperation.value === '' && inputSearchProducto.value === '';
})

// Para habilitar el boton de buscar
inputSearchProducto.addEventListener("input", () => {
    buttonSubmitSearch.disabled = inputSearchProducto.value === '' && inputSearchOperation.value === '';
})

buttonSubmitSearch.addEventListener('click', async () => {
    operationsList.innerHTML = ''
    let inputs = document.querySelectorAll("input:not([type='submit']):not([type='button'])");
    let formData = {};
    inputs.forEach(input => {
        if (input.value !== '') {
            formData[input.name] = input.value;
        }
    });
    let response = await fetchVenta(window.location.pathname, formData)

    if (response["status"]){
        console.log(response["ventas"])
        for (const venta of response["ventas"]) {
            operationsList.insertAdjacentHTML('beforeend', htmlVenta(venta))
        }
        buttonSubmitSearch.insertAdjacentHTML('afterend', htmlLimpiarFiltros())
    }else{
        console.log(response["detalleError"])
    }
     
})

// Crear el html de la venta 
function htmlVenta(venta){
    let ordenesHtml = '';
    for (const nro_orden of venta['nro_ordenes']) {
        ordenesHtml += `<h3>${nro_orden}</h3>`;
    }

    let iconStatusClass = "";
    if (venta['estado'].toLowerCase().includes('activo')) {
        iconStatusClass = "activo";
    } else if (venta['estado'].toLowerCase().includes('baja')) {
        iconStatusClass = "baja";
    } else if (venta['estado'].toLowerCase().includes('adjudicada')) {
        iconStatusClass = "adjudicada";
    } else if (venta['estado'].toLowerCase().includes('suspendida')) {
        iconStatusClass = "suspendida";
    }

    let stringHtml = `
    <li class="operationItem">
        <div class="nameStatus">
            <img class="iconProducto" src="/static/images/icons/moto_icon.svg" alt="">
            <h1>${venta['producto']}</h1>    
            <div class="iconStatus ${iconStatusClass}"></div>
            <h3>${venta['estado']}</h3>    
        </div>
        <div class="attributes">
            <div class="information">
                <h2>Importe</h2>
                <h3>$${venta['importe']}</h3>
            </div>
            
            <div class="information">
                <h2>Fecha Inscripcion</h2>
                <h3>${venta['fecha_inscripcion'].substring(0,10)}</h3>
            </div>
            <div class="information">
                <h2>N° Operacion</h2>
                <h3>${venta['nro_operacion']}</h3>
            </div>
            
            <div class="information">
                <h2>Cuotas pagadas</h2>
                <h3>${venta['cuotas_pagadas']}</h3>
            </div>
            <div class="information">
                <h2>N° Orden/es</h2>
                <div class="ordenesWrapper">
                    ${ordenesHtml}
                </div>
            </div> 
        </div>
        <div class="iconsAttributes">
            <a href="/ventas/detalle_venta/8/" class="buttonMore">
                <div>
                    <h3>Ver mas</h3>
                    <img src="/static/images/icons/nextSinBackground.png" alt="">
                </div>
            </a>
        </div>
        
    </li>`
    return stringHtml
}

function htmlLimpiarFiltros(){
    return `<a href="${window.location.pathname}" onclick="deleteHTMLLimpiarFiltros(this)" id="resetFiltros">Limpiar filtros</a>`
}

function deleteHTMLLimpiarFiltros(button){
    button.remove()
}



