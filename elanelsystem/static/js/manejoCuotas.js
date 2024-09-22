const cuotasWrapper = document.querySelectorAll(".cuota")
const btnDescuentoCuota = document.getElementById("btnDescuentoCuota")
const payCuotaForm = document.getElementById("payCuotaForm")
const wrapperVerDetallesPago = document.getElementById("wrapperVerDetallesPago")

const btnPayCuota = document.getElementById("sendPayment")
const btnCloseFormCuota = document.getElementById("closeFormCuota")
const btnCloseViewCuota = document.getElementById("closeViewCuota")


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
        <h2>Acreditacion de cuota</h2>        
        <form id="descuentoCuotaForm" method="POST" class="wrapperDescuentoCuota">
                <h3>Monto:</h3>
                <input type="number" oninput="checkButtonSubmitDescuento()" id="dineroDescuento" name ="dineroDescuento" class="input-read-write-default" placeholder="Monto">
                <h3>Autorizado por:</h3>
                <input type="text" oninput="checkButtonSubmitDescuento()" id="autorizacionDescuento" name ="autorizacionDescuento" class="input-read-write-default" placeholder="Ingrese el nombre">
                <div class="buttonsActionsDescuentoWrapper">
                    <button form="descuentoCuotaForm" disabled type="button" id="submitDescuento" class="add-button-default" name="aplicarDescuento">Aplicar</button>
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

// Funcion para verificar si los campos del formulario de descuento estan rellenados
function checkButtonSubmitDescuento() {
    let inputsFormDescuento = descuentoCuotaForm.querySelectorAll("input")
    // Si todos los inputs son diferentes a "" entonces habilitar el button de submit
    
    inputsFormDescuento.forEach(element => {
        if(element.value == ""){
            submitDescuento.disabled = true;
            return;
        }
        else{
            submitDescuento.disabled = false;
        }
    });
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
        let formdescuento = { "cuota": cuotaID.value, "descuento": dineroDescuento.value, "autorizado": autorizacionDescuento.value };
        let responseDescuento = await formFETCH(formdescuento, "/ventas/detalle_venta/descuento_cuota/");

        // Solicita la cuota actualizada luego del descuento y la actualiza en el HTML
        let formCuota = { "ventaID": ventaID.value, "cuota": cuotaID.value };
        let responseCuota = await formFETCH(formCuota, "/ventas/detalle_venta/get_specific_cuota/");
        resto = calcularDineroRestante(responseCuota);

        // Elimina el formulario de descuento
        let wrapperDescuento = document.querySelector(".wrapperDetalleEstadoVenta > .descuentoWrapperBackground");
        wrapperDescuento.remove();

        checkFormValid(validarInputsRellenados(), validarMontoParcial(resto))


    } catch (error) {
    }
}
//#endregion  

// Proceso de seleccion de cuota
cuotasWrapper.forEach(cuota => {
    cuota.addEventListener('click', async () => {

        // Primero mostramos el form
        
        // Luego solictamos la cuota a gestionar 
        let form = { "ventaID": ventaID.value, "cuota": cuota.id }
        let data = await formFETCH(form, "/ventas/detalle_venta/get_specific_cuota/")
        console.log(data)
        if(data["status"] == "Pagado"){
            wrapperVerDetallesPago.classList.add("active")
            verDetalleCuota(data)
        }else{
            payCuotaForm.classList.add("active")
            activeFormCuotas(data)
        }
    })
});

//Funcion confirmar la anulacion de una cuota
async function anularCuota() {
    let url = "/ventas/detalle_venta/anular_cuota/"
    let form = {"cuota": cuotaID.value, "password": passwordAnularCuota.value}
    let response = await formFETCH(form, url)

    if(response["status"]){
        if(response["password"]){
            actualizarEstadoCuota(cuotaID.value) //Primero actualizamos la cuota operada
            actualizarEstadoProximaCuota(cuotaID.value) // Desbloqueamos la siguiente cuota
            displayMensajePostCuotaPagada(response.status, response.message)
            cerrarAnularCuotaForm()
            wrapperVerDetallesPago.classList.remove("active")
            document.querySelector("#anularButton").remove()
            document.querySelector(".wrapperInfo_cuota").remove()

        }
        else{
            showMessageFormAnularCuota()
        }
    }else{
        displayMensajePostCuotaPagada(response.status, response.message)
        cerrarAnularCuotaForm()
        wrapperVerDetallesPago.classList.remove("active")

    }
}

function htmlPassAnularCuota(){
    if(!document.querySelector("#formAnularCuota")){
        let wrapperVerDetallesPago = document.querySelector("#wrapperVerDetallesPago")
        let stringHTML = `
            <form id="formAnularCuota" method="POST">
                ${crsf_token}
                <h3>Para anular la cuota, ingrese su contraseña</h3>
                <input type="text" placeholder="Contraseña" id="passwordAnularCuota" name="passwordAnularCuota" class="input-read-write-default">
                <div class="buttonsWrapperAnularCuota">
                    <button type="button" onclick="anularCuota()" id="anularButton" class="delete-button-default">Anular cuota</button>
                    <button type="button" onclick="cerrarAnularCuotaForm()" id="cancelarAnularButton" class="button-default-style">Cancelar</button>
                </div>
            </form>`
        wrapperVerDetallesPago.insertAdjacentHTML('beforeend', stringHTML)
    }
    
}

function showMessageFormAnularCuota() {
    let inputFormAnularCuota = document.querySelector("#formAnularCuota > input")
    let stringHTML = `<h3 class="messageAnularCuota">Contraseña incorrecta</h3>`
    inputFormAnularCuota.insertAdjacentHTML('afterend', stringHTML)
}

function cerrarAnularCuotaForm() {
    let formAnularCuota = document.querySelector("#formAnularCuota")
    formAnularCuota.remove()
}

// Funcion para ver el detalle de la cuota
function verDetalleCuota(cuotaSelected) {
    let wrapperVerDetallesPago = document.querySelector("#wrapperVerDetallesPago")
    
    wrapperVerDetallesPago.insertAdjacentHTML('beforeend', htmlDetalleCuota(cuotaSelected))
    
    // Seteamos el valor del titulo de la cuota que se abrio el form
    let tittleCuotaSelected = wrapperVerDetallesPago.querySelector(".cuotaPicked")
    tittleCuotaSelected.innerHTML = cuotaSelected["cuota"]

    // Seteamos el valor del input hidden de la cuota que se abrio el form
    let cuotaInput = payCuotaForm.querySelector("#cuotaID")
    cuotaInput.value = cuotaSelected["cuota"]
    
    // Verifico si es la ultima cuota pagada para agregar el boton de "Anular cuota"
    if(cuotaSelected["buttonAnularCuota"]){
        let anularButton = cuotaSelected["buttonAnularCuota"]
        if(!document.querySelector("#anularButton")){
            wrapperVerDetallesPago.insertAdjacentHTML('beforeend', anularButton)
        }
    }else{
        let anularButton = wrapperVerDetallesPago.querySelector("#anularButton")
        if(anularButton){
            anularButton.remove()
        }
    }

    
 
}

// Funcion para desplegar mas detalles del detalle de la cuota
function viewMoreFunction(elemento) {
    let iconDisplayViewMore = elemento.querySelector(".iconDisplayViewMore")
    let viewMoreContent = elemento.querySelector(".wrapperDetail_view_more")
    iconDisplayViewMore.classList.toggle("active")
    viewMoreContent.classList.toggle("active")
}

function htmlDetalleCuota(cuota){
    let stringHTML = `
        <div class="wrapperInfo_cuota">
            <div onclick="viewMoreFunction(this)" class="info_cuota view_more">
                <h3>Pagos</h3>
                <img class="iconDisplayViewMore" src="/static/images/icons/arrowDown.png" alt="">
                <div class="wrapperDetail_view_more">
                    ${htmlPagos(cuota["pagos"])}
                </div>
            </div>
            <div class="info_cuota">
                <h3>Descuento</h3>
                <h3>${cuota["descuento"]["monto"]}</h3>
            </div>`
        if(cuota["cuota"] != "Cuota 0"){
            stringHTML += `
                <div class="info_cuota">
                    <h3>Dias de atraso</h3>
                    <h3>${cuota["diasRetraso"]}</h3>
                </div>  
                
                <div class="info_cuota">
                    <h3>Interes por mora</h3>
                    <h3>${cuota["interesPorMora"]}</h3>
                </div>
                <div class="info_cuota">
                    <h3>Total</h3>
                    <h3>$${(cuota["total"] + cuota["interesPorMora"]) - cuota["descuento"]["monto"]}</h3>
                </div>
                <div class="info_cuota">
                    <h3>Fecha de venc.</h3>
                    <h3>${cuota["fechaDeVencimiento"].substring(0, 10)}</h3>
                </div>`
        }
        stringHTML += `</div>`
    return stringHTML;

}
    

function htmlPagos(pagos){
    let stringHTML = ""
    pagos.forEach((element,index) => {
        stringHTML += `
                    <h3>${index+1}:</h3>
                    <div class="info_cuota detail_view_more">
                        <h3>Fecha de pago</h3>
                        <h3>${element["fecha"]}</h3>
                    </div>
                    <div class="info_cuota detail_view_more">
                        <h3>Metodo de pago</h3>
                        <h3>${element["metodoPago"]}</h3>
                    </div>
                    <div class="info_cuota detail_view_more">
                        <h3>Cobrador</h3>
                        <h3>${element["cobrador"]}</h3>
                    </div>
                    <div class="info_cuota detail_view_more">
                        <h3>Monto</h3>
                        <h3>$${element["monto"]}</h3>
                    </div>`
    });
    return stringHTML;
}



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
        actualizarEstadoProximaCuota(cuotaID.value) // Desbloqueamos la siguiente cuota

        displayMensajePostCuotaPagada(data.status, data.message)
        hideFormCuotas()
    })


})


// Cerrar el formulario
btnCloseFormCuota.addEventListener("click", () => {
    hideFormCuotas()
})
// Cerrar el formulario de ver detalles
btnCloseViewCuota.addEventListener("click", () => {
    wrapperVerDetallesPago.classList.remove("active")
    document.querySelector(".wrapperInfo_cuota").remove()
    document.querySelector("#anularButton").remove()
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
        btnPayCuota.disabled = false;
        btnPayCuota.classList.toggle('blocked', false);
        amountParcial.style.border = "2px solid var(--secundary-color)"
        return true
    }
}


// Funcion para calcular el dinero restante al pagar parcialmente
function calcularDineroRestante(cuota) {
    let dineroRestanteHTML = payCuotaForm.querySelector("#dineroRestante")
    console.log(cuota)
    console.log(cuota["pagos"])
    
    let listPagos = cuota["pagos"].map(({monto}) => monto)
    let sumaPagos = listPagos.reduce((acc, num) => acc + num, 0);
    resto = cuota["total"] - (sumaPagos + cuota["descuento"]["monto"])
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
function actualizarEstadoProximaCuota(cuota) {
    const numeroCuota = parseInt(cuota.split(" ")[1]);
    // Incrementar el número de cuota en 1
    const nuevoNumeroCuota = numeroCuota + 1;

    // Volver a unir la cadena con el nuevo número de cuota
    const cuotaADesbloquear = "Cuota " + nuevoNumeroCuota;
    console.log("Cuota siguiente: ", cuotaADesbloquear);
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
            // Elimnamos el estado anterior
            removeSpecificClasses(c)
            removeSpecificClasses(c.children[0])
            if (!data["bloqueada"]) {
                // Colocamos el estado actual
                c.classList.add(data["status"])
                c.children[0].classList.add(data["status"]);
                c.children[0].removeAttribute("style");
            }else{
                c.classList.add("Bloqueado")
                c.children[0].classList.add("Bloqueado");
                c.children[0].setAttribute("style", data["styleBloqueado"]);

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


