let newIdNroContrato = `nroContrato_1`;
let newIdNroOrden = `nroOrden_1`;
listenerColocarUltimos3Digitos(newIdNroContrato,newIdNroOrden);

function agregarChance() {
    const allChancesItems = document.querySelectorAll('.chanceItem');
    let ultimaChanceNumber = obtenerUltimaChance();
    let newIdNroContrato = `nroContrato_${ultimaChanceNumber + 1}`;
    let newIdNroOrden = `nroOrden_${ultimaChanceNumber + 1}`;

    stringForHTML =`
    <div class="chanceItem">
        <h5>Chance ${ultimaChanceNumber + 1})</h5>
        <div class="wrapperNroSolicitud">
            <label for="">Nro contrato</label>
            <input type="text" name="nro_contrato_${ultimaChanceNumber + 1}" maxlength="10" class="input-read-write-default" oninput="this.value = this.value.replace(/[^0-9]/g, '');" required id="${newIdNroContrato}">
        </div>
        <div class="wrapperNroOrden">
            <label for="">Nro orden</label>
            <input type="text" name="nro_orden_${ultimaChanceNumber + 1}" class="input-read-write-default" readonly oninput="this.value=this.value.replace(/[^0-9]/g, '');" required id="${newIdNroOrden}">
        </div>
        <button type="button" class="quitarChanceButton delete-button-default" onclick="quitarChance(this)">Quitar chance</button>

    </div>`;
  
    allChancesItems[allChancesItems.length - 1].insertAdjacentHTML("afterend",stringForHTML);

    // Aumentar la cantidad de chances para rellenar y recalcular los campos de venta
    cantidadChances += 1;
    rellenarCamposDeVenta(cantidadChances);

    listenerColocarUltimos3Digitos(newIdNroContrato,newIdNroOrden);
}

// function removeChance(button) {
//   button.parentElement.parentElement.remove();
// }

function listenerColocarUltimos3Digitos(nro_contrato,nro_orden) {
    let input_nro_contrato = document.getElementById(nro_contrato);
    let input_nro_orden = document.getElementById(nro_orden);

    input_nro_contrato.addEventListener("input", () => {
        // Obtener los últimos 3 dígitos del número de contrato
        const ultimosTresDigitos = input_nro_contrato.value.slice(-3);
        input_nro_orden.value = ultimosTresDigitos;

    })
}

// Funcion para quitar una chance
function quitarChance(button) {
    let chanceItem = button.parentElement;
    chanceItem.remove();
    reenumerarChances();

    // Disminuir la cantidad de chances para rellenar y recalcular los campos de venta
    cantidadChances -= 1;
    rellenarCamposDeVenta(cantidadChances);
}

// Cuando se elimina una chance, se debe reenumerar las chances
function reenumerarChances() {
    let chancesText = document.querySelectorAll('.chanceItem > h5');
    let cantidadChances = chancesText.length;
    for (let i = 0; i < cantidadChances; i++) {
        // Reenumerar las chances en el texto
        chancesText[i].innerText = `Chance ${i + 1})`;

        // Obtener los inputs de nro de contrato y nro de orden
        let nroContrato = chancesText[i].parentElement.querySelector('.wrapperNroSolicitud > input');
        let nroOrden = chancesText[i].parentElement.querySelector('.wrapperNroOrden > input');

        // Reasignar los atributos name
        nroContrato.name = `nro_contrato_${i + 1}`;
        nroOrden.name = `nro_orden_${i + 1}`;
        
        // Reasignar los atributos id
        nroContrato.id = `nroContrato_${i + 1}`;
        nroOrden.id = `nroOrden_${i + 1}`;
        
    }
}

function obtenerUltimaChance() {
    let lastChance = document.querySelector('.chanceItem:last-child .wrapperNroSolicitud input');
    return parseInt(lastChance.id.split('_')[1]);
}