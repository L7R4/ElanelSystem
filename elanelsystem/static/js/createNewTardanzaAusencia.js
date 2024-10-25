// Seleccionar los botones
const buttonsAddItem = document.querySelectorAll(".buttonsAddItem > button");
let listTardanzasAusencias = document.querySelector(".listTardanzasAusencias");


// Asignar eventos a los botones de "Guardar" y "Cancelar"
async function buttonSendItem(button) {
    let contenedor = button.offsetParent.offsetParent.children[1]
    console.log(contenedor)
    const body = {
            "colaborador":document.getElementById("colaborador").value, 
            "tipoEvento": document.getElementById("tipoEvento").value,
            "fecha": document.getElementById('fecha').value, 
            "hora": document.getElementById('hoursInput').value +':'+ document.getElementById('minutesInput').value
    }
    const responseData = await fetchFunction(body,urlNewIem);

    if (responseData) {
        document.querySelector(".new_item").nextElementSibling.remove();
        document.querySelector(".new_item").remove();
        newItemCreated(responseData, contenedor);
    }
};
function closeSendItem(){
    document.querySelector(".new_item").nextElementSibling.remove();
    document.querySelector(".new_item").remove();
    
}
    


// Función para actualizar el DOM con el nuevo item creado
function newItemCreated(data, contenedor) {
    let contenedorShortInfo = contenedor.parentElement.parentElement.parentElement.previousElementSibling
    
    const textTardanza = contenedorShortInfo.querySelector(".textCountTardanzas");
    const textFalta = contenedorShortInfo.querySelector(".textCountFaltas");
    textFalta.textContent = data.countFaltas;
    textTardanza.textContent = data.countTardanzas;

    const itemHTML = `
    <tr>
        <td>${data.tipoEvento || ""}</td>
        <td>${data.fecha || 0}</td>
        <td>${data.hora || ""}</td>
    </tr>`;
    
    contenedor.insertAdjacentHTML('afterbegin', itemHTML);
}

// Función para crear el formulario de nuevo item
function createNewItemForm(button, colaborador,fechaHoy, tipo) {
    const existingItem = document.querySelector(".new_item");
    if (existingItem){
        existingItem.nextElementSibling.remove();
        existingItem.remove();
    } 
        

    const listaItems = button.parentElement.previousElementSibling.children[1];
    const tipoEvento = tipo === 'tardanza' ? "Tardanza" : "Falta";

    const formHTML = `
    <tr class="new_item">
        <input type="hidden" name="colaborador" id="colaborador" value="${colaborador}" readonly>
        <td>
            <div><input class="input-read-write-default" type="text" name="tipoEvento" id="tipoEvento" value="${tipoEvento}" readonly></div>
        </td>
        <td>
            <div><input class="input-read-write-default" type="text" name="fecha" id="fecha" value="${fechaHoy}" readonly></div
        </td>
        <td>
            <div style="display: ${tipoEvento === 'Falta' ? 'none' : 'block'};">
            <div class="time-picker-container">
                <input type="text" class="input-read-write-default" name="hoursInput" id="hoursInput" maxlength="2" placeholder="HH" onchange="validateHours()">
                <p>:</p>
                <input type="text" class="input-read-write-default" name="minutesInput" id="minutesInput" maxlength="2" placeholder="MM" onchange="validateMinutes()">
            </div>
            
            </div>
        </td>

    </tr>
    <tr>
        <td colspan="3">
            <div class="wrapperButtonsSendItem">
                <button type="button" id="sendNewItem" class="add-button-default" onclick="buttonSendItem(this)">Guardar</button>
                <button type="button" id="closeSendNewItem" class="delete-button-default" onclick="closeSendItem()">Cancelar</button>
            </div>
        </td>
    </tr>`;
    listaItems.insertAdjacentHTML('beforeend', formHTML);

    // buttonSendItem(listaItems);
}

// Calcular el tiempo de tardanza
// function calcularTiempo(horaInput, horaSucursal) {
//     const [hhInput, mmInput] = horaInput.split(':');
//     const [hhSucursal, mmSucursal] = horaSucursal.split(':');
//     const minutos1 = parseInt(hhInput) * 60 + parseInt(mmInput);
//     const minutos2 = parseInt(hhSucursal) * 60 + parseInt(mmSucursal);

//     if (!isNaN(minutos1)) {
//         const resultadoMinutos = minutos1 - minutos2;
//         calcularMonto(resultadoMinutos);
//     }
// }

// // Calcular el monto a descontar
// function calcularMonto(minutos) {
//     const MINUTOS_DE_GRACIA = 15;
//     const descuentoInput = document.getElementById('descuento');
//     if (minutos <= MINUTOS_DE_GRACIA) {
//         descuentoInput.value = 0;
//     } else if (minutos > MINUTOS_DE_GRACIA && minutos < 60) {
//         descuentoInput.value = "{{amountTardanza}}";
//     } else if (minutos >= 60) {
//         descuentoInput.value = "{{amountFalta}}";
//     } else {
//         descuentoInput.value = 0;
//     }
// }

// Validacion para el manejo de las horas
// Validación de horas: asegúrate de que las horas estén entre 00 y 23
function validateHours() {
    const hoursInput = document.getElementById('hoursInput');
    let value = parseInt(hoursInput.value);
    
    if (isNaN(value) || value < 0) {
        hoursInput.value = '00'; // Si no es un número o es menor que 0, poner '00'
    } else if (value > 23) {
        hoursInput.value = '23'; // Si es mayor que 23, limitar a 23
    } else if (hoursInput.value.length === 1) {
        hoursInput.value = '0' + hoursInput.value; // Añadir '0' a horas de un solo dígito
    }else{
       hoursInput.value = hoursInput.value 
    }
}

// Validación de minutos: asegúrate de que los minutos estén entre 00 y 59
function validateMinutes() {
    const minutesInput = document.getElementById('minutesInput');
    let value = parseInt(minutesInput.value);

    if (isNaN(value) || value < 0) {
        minutesInput.value = '00'; // Si no es un número o es menor que 0, poner '00'
    } else if (value > 59) {
        minutesInput.value = '59'; // Si es mayor que 59, limitar a 59
    } else if (minutesInput.value.length === 1) {
        minutesInput.value = '0' + minutesInput.value; // Añadir '0' a minutos de un solo dígito
    }
    else{
        minutesInput.value = minutesInput.value 
    }

}