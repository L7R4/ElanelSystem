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
    let stringForHTML = `<div>
        <h3>Coloque el dinero</h3>
        <form id="descuentoCuotaForm" method="POST" class="wrapperDescuentoCuota">
            <input type="hidden" name="cuotaParaDescuento" id="cuotaParaDescuento" value="">
            <input type="number" id="dineroDescuento" name ="dineroDescuento" value="0">
            <button form="descuentoCuotaForm" type="button" id="submitDescuento" name="aplicarDescuento">Aplicar</button>
        </form>
    </div>`

    return stringForHTML
}

btnDescuentoCuota.addEventListener('click', () => {
    let form = document.getElementById(btnDescuentoCuota.form)
    formPOST(form, "ventas/detalle_venta/descuento_cuota/").then(async response => {
        let data = await fetchCuotas()
        calcularDineroRestante(cuotaPicked.innerHTML, data)
        descuentoCuotaWrapper.classList.remove("active")
        dineroDescuento.value = ""
        cuotaParaDescuento.value = ""
    })
})

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
        console.log(data)
    })
});


// Pagar la cuota
btnPayCuota.addEventListener("click", () => {
    let typePaymentSelected = payCuotaForm.querySelector('.wrapperChoices input[type="radio"]:checked');
    let form = { "cobrador": cobrador.value, "typePayment": typePaymentSelected.value, "metodoPago": metodoPago.value, "ventaID": ventaID.value, "cuota": cuotaID.value, "valorParcial": amountParcial.value }

    formFETCH(form, "/ventas/detalle_venta/pay_cuota/").then(data => {
        console.log(data.message, data.detalleError)
        desbloquearProximaCuota(cuotaID.value)
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

// Funcion para ver si la cuota esta parcialmente pagada
function vericarSiEsParcial(cuota) {
    let cuotaHTML = ""
    cuotasWrapper.forEach(c => {
        if (c.querySelector("h4").textContent === cuota["cuota"]) {
            cuotaHTML = c
        }
    });

    let marcaStatusCuota = cuotaHTML.querySelector(".marca")
    let typesPayments = payCuotaForm.querySelector(".typesPayments > .wrapperChoices")

    if (marcaStatusCuota.classList.contains("Parcial")) {
        // Escondemos el tipo de pago total
        typesPayments.querySelector("#choiceTotal").style.display = "none"

        // Marcamos como check el tipo de pago parcial para que quede como obligatorio
        setearInputAFormaDePago(typesPayments.querySelector("#choiceParcial"))

        // // Mostramos el input del dinero a colocar
        // let amountWrapper = payCuotaForm.querySelector(".pickedAmount")
        // amountWrapper.classList.add("active")

        // Calculamos el dinero faltante
        calcularDineroRestante(cuota)
    }
}

// Funcion para ver si el monto parcial colocado es correcto al monto que se debe
function validarMontoParcial(resto, monto) {

    if (monto > resto) {
        btnPayCuota.disabled = true;
        btnPayCuota.classList.toggle('blocked', true);
        amountParcial.style.border = "2px solid rgba(255, 0, 0, 0.726)"
    } else {
        btnPayCuota.disabled = false;
        btnPayCuota.classList.toggle('blocked', false);
        amountParcial.style.border = "2px solid var(--secundary-color);"

    }
}


// Funcion para calcular el dinero restante al pagar parcialmente
function calcularDineroRestante(cuota) {
    let dineroRestanteHTML = payCuotaForm.querySelector("#dineroRestante")
    let listPagos = cuota["pagoParcial"]["amount"]
    let sumaPagos = listPagos.reduce((acc, num) => acc + num["value"], 0);
    let resto = cuota["total"] - (sumaPagos + cuota["descuento"])
    dineroRestanteHTML.innerHTML = "Dinero restante: $" + resto
    return resto;
}


// Funcion para actualizar la cuota que vamos a gestionar
function activeFormCuotas(cuotaSelected) {


    let tittleCuotaSelected = payCuotaForm.querySelector(".cuotaPicked")
    tittleCuotaSelected.innerHTML = cuotaSelected["cuota"]

    let cuotaInput = payCuotaForm.querySelector("#cuotaID")
    cuotaInput.value = cuotaSelected["cuota"]

    // validarSiAplicaDescuento(cuotaSelected)
    let resto = calcularDineroRestante(cuotaSelected)





    let inputsFormaDePago = payCuotaForm.querySelectorAll(".choice")
    if (!vericarSiEsParcial(cuotaSelected)) {
        let formaDePago = setearInputAFormaDePago(inputsFormaDePago[0])
        inputsFormaDePago.forEach(choice => {
            choice.addEventListener("click", () => {
                formaDePago = setearInputAFormaDePago(choice)
            })
        });
    }
    vericarSiEsParcial(cuotaSelected)



    checkFormCompletion(formaDePago);
    payCuotaForm.querySelectorAll("input").forEach(field => {
        field.addEventListener('input', () => {
            console.log("Evento input")
            checkFormCompletion(formaDePago)
            if (field.id == "amountParcial") {
                validarMontoParcial(resto, field.value)
            }
        });
    });
}


// Funcion para verificar si son las cuotas 0 o 1 para disponer del boton para aplicar descuentos
function validarSiAplicaDescuento(cuota) {
    cuota = cuota["cuota"]
    if (cuota == "Cuota 0" || cuota == "Cuota 1") {
        descuentoCuotaButton.style.display = "block"
    } else {
        descuentoCuotaButton.style.display = "none"
    }
}


// Funcion para desbloquear la proxima cuota
function desbloquearProximaCuota(cuota) {
    const numeroCuota = parseInt(cuota.split(" ")[1]);
    // Incrementar el número de cuota en 1
    const nuevoNumeroCuota = numeroCuota + 1;

    // Volver a unir la cadena con el nuevo número de cuota
    const cuotaADesbloquear = "Cuota " + nuevoNumeroCuota;
    console.log('Cuota a desbloquear')
    console.log(cuotaADesbloquear)

    actualizarEstadoCuota(cuota) //Primero actualizamos la cuota operada
    actualizarEstadoCuota(cuotaADesbloquear) // Luego actualizamos la proxima cuota
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
    console.log(choice)
    let inputsFormaDePago = payCuotaForm.querySelectorAll(".wrapperChoices > .choice")
    let montoDeFormaParcial = payCuotaForm.querySelector(".pickedAmount")

    // Limpiamos todos los demas inputs
    inputsFormaDePago.forEach(c => c.classList.remove("active"));

    choice.children[0].checked = true
    choice.classList.add("active")

    if (choice.id == "choiceParcial") {
        montoDeFormaParcial.style.display = "block"
    } else {
        montoDeFormaParcial.style.display = "none"
        montoDeFormaParcial.children[1].value = ""
    }
    checkFormCompletion(choice.id)
    return choice.id
}


// Funcion para habilitar el boton de submit del formulario
function checkFormCompletion(formaPago) {
    let requiredFields = payCuotaForm.querySelectorAll("input:not([type='hidden']):not([type='radio'])");

    let contInputs = 0
    requiredFields.forEach(field => { if (field.value !== "") { contInputs++ } });
    if (formaPago == "choiceParcial" && contInputs == 3) {
        btnPayCuota.disabled = false;
        btnPayCuota.classList.toggle('blocked', false);
    } else if (formaPago == "choiceTotal" && contInputs == 2) {
        btnPayCuota.disabled = false;
        btnPayCuota.classList.toggle('blocked', false);
    } else {
        btnPayCuota.disabled = true;
        btnPayCuota.classList.toggle('blocked', true);
    }
}

// Funcion para actualizar el estado de una cuota
async function actualizarEstadoCuota(cuota) {
    // Luego solictamos la nueva cuota a desbloquear para colocarle su estado actual
    let form = { "ventaID": ventaID.value, "cuota": cuota }
    let data = await formFETCH(form, "/ventas/detalle_venta/get_specific_cuota/")

    cuotasWrapper.forEach(async (c, i) => {
        if (c.querySelector("h4").textContent === data["cuota"]) {

            // Elimnamos el estado anterior
            removeSpecificClasses(c)
            removeSpecificClasses(c.children[0])

            // Colocamos el estado actual
            c.classList.add(data["status"])
            c.children[0].classList.add(data["status"]);

            if (c.querySelector("h4").textContent != "Cuota 0" && cuotasWrapper[i - 1].classList.contains("Pagado")) {
                c.children[0].removeAttribute("style"); // Por si se encuentra bloqueado
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


