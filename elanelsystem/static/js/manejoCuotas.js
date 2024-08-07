const cuotasWrapper = document.querySelectorAll(".cuota")
const btnDescuentoCuota = document.getElementById("btnDescuentoCuota")
const payCuotaForm = document.getElementById("payCuotaForm")
const btnPayCuota = document.getElementById("sendPayment")
const btnCloseFormCuota = document.getElementById("closeFormCuota")

//#region Funcion del formulario FETCH
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

async function formFETCH(form, url) {
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
            },
            body: JSON.stringify(form)
        })
        if (!res.ok) {
            throw new Error("Error")
        }
        const data = await res.json()
        return data;
    } catch (error) {
    }
}
//#endregion  

//#region Creacion de descuento en cuotas
function formHTMLDescuento() {
    let stringForHTML = `<div class="descuentoWrapperBackground">
        <div>
            <h3>Coloque el dinero</h3>
            <form id="descuentoCuotaForm" method="POST" class="wrapperDescuentoCuota">
                <input type="number" id="dineroDescuento" name ="dineroDescuento" class="input-read-write-default" placeholder="Ingrese el dinero">
                <div class="buttonsActionsDescuentoWrapper">
                    <button form="descuentoCuotaForm" type="button" id="submitDescuento" class="add-button-default" name="aplicarDescuento">Aplicar</button>
                    <button type="button" class="button-default-style" id="closeFormDescuento">Cancelar</button>
                </div>
            </form>
        </div>
    </div>`
    return stringForHTML
}
function descuentoCuotaManagement() {
    if (!document.querySelector('.descuentoWrapperBackground')) {
        payCuotaForm.insertAdjacentHTML('beforebegin', formHTMLDescuento());
    }

    // Selecciona el botón de cerrar dentro del formulario recién agregado
    const closeFormDescuento = document.querySelector('.descuentoWrapperBackground #closeFormDescuento');
    // Remover cualquier listener anterior del botón de cerrar
    closeFormDescuento.removeEventListener('click', closeFormDescuentoHandler);
    // Añadir el listener para el botón de cerrar
    closeFormDescuento.addEventListener('click', closeFormDescuentoHandler);


    const submitFormDescuento = document.querySelector('.descuentoWrapperBackground #submitDescuento');
    // Remover cualquier listener anterior del botón de enviar
    submitFormDescuento.removeEventListener('click', aplicarDescuentoCuota);
    // Añadir el listener para el botón de enviar
    submitFormDescuento.addEventListener('click', aplicarDescuentoCuota);
}


// Funcion para cerrar el formulario de descuento de la cuota 1 o 0
function closeFormDescuentoHandler() {
    let wrapperDescuento = document.querySelector(".wrapperDetalleEstadoVenta > .descuentoWrapperBackground");
    if (wrapperDescuento) {
        wrapperDescuento.remove();
    }
}
let resto = 0;
async function aplicarDescuentoCuota() {
    try {

        // Aplica el descuento a la cuota
        let formdescuento = { "ventaID": ventaID.value, "cuota": cuotaID.value, "descuento": dineroDescuento.value };
        let responseDescuento = await formFETCH(formdescuento, "/ventas/detalle_venta/descuento_cuota/");

        // Solicita la cuota actualizada luego del descuento y la actualiza en el HTML
        let formCuota = { "ventaID": ventaID.value, "cuota": cuotaID.value };
        let responseCuota = await formFETCH(formCuota, "/ventas/detalle_venta/get_specific_cuota/");
        resto = calcularDineroRestante(responseCuota);

        // Elimina el formulario de descuento
        let wrapperDescuento = document.querySelector(".wrapperDetalleEstadoVenta > .descuentoWrapperBackground");
        wrapperDescuento.remove();
        console.log(responseDescuento["message"])
        checkFormValid(validarInputsRellenados(), validarMontoParcial(resto))


    } catch (error) {
        console.error("Error al aplicar el descuento de cuota:", error);
    }
}
//#endregion  


// Proceso de seleccion de cuota
cuotasWrapper.forEach(cuota => {
    cuota.addEventListener('click', async () => {

        // Primero mostramos el form
        payCuotaForm.classList.add("active")

        // Luego solictamos la cuota a gestionar 
        let form = { "ventaID": ventaID.value, "cuota": cuota.id }
        let data = await formFETCH(form, "/ventas/detalle_venta/get_specific_cuota/")
        activeFormCuotas(data)
    })
});


// Pagar la cuota
btnPayCuota.addEventListener("click", () => {
    let typePaymentSelected = payCuotaForm.querySelector('.wrapperChoices input[type="radio"]:checked');
    let form = { "cobrador": cobrador.value, "typePayment": typePaymentSelected.value, "metodoPago": metodoPago.value, "ventaID": ventaID.value, "cuota": cuotaID.value, "valorParcial": amountParcial.value }

    formFETCH(form, "/ventas/detalle_venta/pay_cuota/").then(data => {
        // Verificamos si la operacion esta en estado suspendida para eliminar el boton "Crear plan recupero"
        if(document.querySelector(".wrapperUrlRecupero")){
            document.querySelector(".wrapperUrlRecupero").remove()
        }
        
        actualizarEstadoCuota(cuotaID.value) //Primero actualizamos la cuota operada
        desbloquearProximaCuota(cuotaID.value) // Desbloqueamos la siguiente cuota

        displayMensajePostCuotaPagada(data.status, data.message)
        hideFormCuotas()
    })


})


// Cerrar el formulario
btnCloseFormCuota.addEventListener("click", () => {
    hideFormCuotas()
})


// Funcion de cierre del formulario para cuando se paga una cuota o se cierra el form
function hideFormCuotas() {
    payCuotaForm.classList.remove("active")
    payCuotaForm.reset();

}

// Funcion que verifica que forma de pago (Pago total o parcial) esta permitida para mostrar en el formulario  
function verificarEstadoDeLaCuenta(cuota) {
    if (cuota["status"] === "Parcial") {

        return true // Retorna verdadero si el estado es parcial
    } else {
        return false // Retorna falso si el estado no es parcial
    }
}

// Funcion para ver si el monto parcial colocado es correcto al monto que se debe
function validarMontoParcial(resto) {
    let monto = payCuotaForm.querySelector("#amountParcial").value

    if (monto > resto) {
        console.log("If del monto parcial")

        btnPayCuota.disabled = true;
        btnPayCuota.classList.toggle('blocked', true);
        amountParcial.style.border = "2px solid rgba(255, 0, 0, 0.726)"
        return false
    } else {
        console.log("Else del monto parcial")
        btnPayCuota.disabled = false;
        btnPayCuota.classList.toggle('blocked', false);
        amountParcial.style.border = "2px solid var(--secundary-color)"
        return true
    }
}


// Funcion para calcular el dinero restante al pagar parcialmente
function calcularDineroRestante(cuota) {
    let dineroRestanteHTML = payCuotaForm.querySelector("#dineroRestante")
    let listPagos = cuota["pagoParcial"]["amount"]
    let sumaPagos = listPagos.reduce((acc, num) => acc + num["value"], 0);
    resto = cuota["total"] - (sumaPagos + cuota["descuento"])
    dineroRestanteHTML.innerHTML = "Dinero restante: $" + resto
    return resto;
}


// Funcion para actualizar la cuota que vamos a gestionar
function activeFormCuotas(cuotaSelected) {

    // Seteamos el valor del titulo de la cuota que se abrio el form
    let tittleCuotaSelected = payCuotaForm.querySelector(".cuotaPicked")
    tittleCuotaSelected.innerHTML = cuotaSelected["cuota"]

    // Seteamos el valor del input hidden de la cuota que se abrio el form
    let cuotaInput = payCuotaForm.querySelector("#cuotaID")
    cuotaInput.value = cuotaSelected["cuota"]

    validarSiAplicaDescuento(cuotaSelected)

    let todasFormasDePago = payCuotaForm.querySelectorAll(".wrapperChoices > .choice")

    // Verificamos que forma de pago tiene permitida
    if (verificarEstadoDeLaCuenta(cuotaSelected)) { // Retorna verdadero si es parcial
        todasFormasDePago[0].style.display = "none"
        setearInputAFormaDePago(todasFormasDePago[1]) // [1] significa que la forma de pago es la parcial
    } else {
        setearInputAFormaDePago(todasFormasDePago[0]) // [0] significa que la forma de pago es la total
        todasFormasDePago[0].style.display = "block"

        todasFormasDePago.forEach(choice => {
            choice.addEventListener("click", () => {
                setearInputAFormaDePago(choice)
            })
        });
    }

    resto = calcularDineroRestante(cuotaSelected)

    // Elimina todo listener antes de abrir otro para que no haya muchos listener si se cierra y se vuelve a abrir el form varias veces
    btnDescuentoCuota.removeEventListener('click', descuentoCuotaManagement);
    btnDescuentoCuota.addEventListener('click', descuentoCuotaManagement)

    checkFormValid(validarInputsRellenados(), validarMontoParcial(resto))
    payCuotaForm.querySelectorAll("input").forEach(field => {
        field.addEventListener('input', () => {
            checkFormValid(validarInputsRellenados(), validarMontoParcial(resto))
        });
    });




}


// Funcion para verificar si son las cuotas 0 o 1 para disponer del boton para aplicar descuentos
function validarSiAplicaDescuento(cuota) {
    cuota = cuota["cuota"]
    if (cuota == "Cuota 0" || cuota == "Cuota 1") {
        btnDescuentoCuota.style.display = "block"
    } else {
        btnDescuentoCuota.style.display = "none"
    }
}


// Funcion para desbloquear la proxima cuota
function desbloquearProximaCuota(cuota) {
    const numeroCuota = parseInt(cuota.split(" ")[1]);
    // Incrementar el número de cuota en 1
    const nuevoNumeroCuota = numeroCuota + 1;

    // Volver a unir la cadena con el nuevo número de cuota
    const cuotaADesbloquear = "Cuota " + nuevoNumeroCuota;

    actualizarEstadoCuota(cuotaADesbloquear) // Actualizamos la proxima cuota
}


// Funcion para mostrar un mensaje al pagar una cuota
function displayMensajePostCuotaPagada(status, message) {
    let messageStatusPostPago = document.querySelector(".payCuotaStatus")
    if (status) {
        messageStatusPostPago.classList.add('active', 'ok')
        messageStatusPostPago.querySelector("#okPostPagoImg").style.display = "unset"
        messageStatusPostPago.querySelector("#failedPostPagoImg").style.display = "none"

        setTimeout(() => {
            messageStatusPostPago.classList.remove('active', 'ok');
        }, 3000);
    } else {
        messageStatusPostPago.classList.add('active', 'failed')
        messageStatusPostPago.querySelector("#okPostPagoImg").style.display = "none"
        messageStatusPostPago.querySelector("#failedPostPagoImg").style.display = "unset"

        setTimeout(() => {
            messageStatusPostPago.classList.remove('active', 'failed');
        }, 3000);
    }
    messageStatusPostPago.querySelector(".infoCuotaStatus").textContent = message

}


// Funcion para que cuando este una forma de pago (parcial o total) elegida se aplique un estilo diferente y haga el checked del input
function setearInputAFormaDePago(choice) {
    let inputsFormaDePago = payCuotaForm.querySelectorAll(".wrapperChoices > .choice")
    let montoDeFormaParcial = payCuotaForm.querySelector(".pickedAmount")

    // Limpiamos todos los demas inputs
    inputsFormaDePago.forEach(c => c.classList.remove("active"));
    payCuotaForm.reset(); // Se resetean los campos


    choice.classList.add("active")
    choice.children[0].checked = true

    if (choice.id == "choiceParcial") {
        montoDeFormaParcial.style.display = "block"
    } else {
        // typesPayments.querySelector("#choiceTotal").style.display = "block"
        montoDeFormaParcial.style.display = "none"
        montoDeFormaParcial.children[1].value = ""
    }
}


// Funcion para habilitar el boton de submit del formulario
function checkFormValid(inputsRellanados, inputMontoParcialValido) {
    if (inputsRellanados && inputMontoParcialValido) {
        btnPayCuota.disabled = false;
        btnPayCuota.classList.toggle('blocked', false);
    } else {
        btnPayCuota.disabled = true;
        btnPayCuota.classList.toggle('blocked', true);
    }
}


function validarInputsRellenados() {
    let requiredFields = payCuotaForm.querySelectorAll("input:not([type='hidden']):not([type='radio'])");
    let formaPagoSeleccionada = payCuotaForm.querySelector(".typesPayments > .wrapperChoices > .choice.active")
    let contInputs = 0
    requiredFields.forEach(field => { if (field.value !== "") { contInputs++ } });

    if (formaPagoSeleccionada.id == "choiceParcial" && contInputs == 3) {
        return true;

    } else if (formaPagoSeleccionada.id == "choiceTotal" && contInputs == 2) {
        return true;

    } else {
        return false;
    }
}


// Funcion para actualizar el estado de una cuota
async function actualizarEstadoCuota(cuota) {
    // Luego solictamos la nueva cuota a desbloquear para colocarle su estado actual
    let form = { "ventaID": ventaID.value, "cuota": cuota }
    let data = await formFETCH(form, "/ventas/detalle_venta/get_specific_cuota/")

    cuotasWrapper.forEach((c, i) => {
        if (c.id === data["cuota"]) {

            
            if (!data["bloqueada"]) {
                // Elimnamos el estado anterior
                removeSpecificClasses(c)
                removeSpecificClasses(c.children[0])
                
                // Colocamos el estado actual
                c.classList.add(data["status"])
                c.children[0].classList.add(data["status"]);
                c.children[0].removeAttribute("style");
            }

        }
    });
}


// Funcion helper para remover las clases de bloqueado, pendiente, atrasado, etc para visualizar en el HTML
function removeSpecificClasses(elementHTML) {
    // Clases específicas que deseas eliminar
    const classesToRemove = ["Pendiente", "Pagado", "Bloqueado", "Atrasado", "Parcial"];

    // Iterar sobre las clases específicas y eliminarlas del elemento
    classesToRemove.forEach(className => {
        if (elementHTML.classList.contains(className)) {
            elementHTML.classList.remove(className);
        }
    });
}


