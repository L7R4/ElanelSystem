const cuotasWrapper = document.querySelectorAll(".cuota")
const btnDescuentoCuota = document.getElementById("btnDescuentoCuota")


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

async function formPOST(form,url){
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
            },
            body: new FormData(form)
        })
        if (!res.ok){
            throw new Error("Error")
        }
        const data = await res.json()
        return data;
    } catch (error) {
    }
}

async function fetchGETCuotas() {
    const response = await fetch(url, {
        method: 'get',
        headers: { 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' },
        cache: 'no-store',
    });
    const data = await response.json();
    return data;
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
    formPOST(form,"ventas/detalle_venta/descuento_cuota/").then(async response => {
        let data = await fetchCuotas()
        calcularDineroRestante(cuotaPicked.innerHTML, data)
        descuentoCuotaWrapper.classList.remove("active")
        dineroDescuento.value = ""
        cuotaParaDescuento.value = ""
    })
})

//#endregion  

//#region Seccion para seleccionar cuota
cuotasWrapper.forEach(cuota => {
    cuota.addEventListener('click', async () => {
        let data = await fetchGETCuotas()

        // ABRE LA VENTANA DE ABONAR CUOTA Y VALIDA SI ESTA PAGADO PARCIALMENTE
        cuotaSelected = selectCuota(cuota, data)
        calcularDineroRestante(cuotaSelected.children[2].innerHTML, data)

        // // SELECCIONA EL TIPO DE PAGO
        // typesPayments.forEach(type => {
        //     type.addEventListener("click", () => {
        //         selectTypePayment(type, data)
        //     })

        // })
    })
});

function selectCuota(target, cuotas) {
    if (!target.children[0].classList.contains("pago") && !target.children[0].classList.contains("pagoBloqueado")) {
        clearPickedCuota() // Limpia todos los valores de los inputs
        clearPickedClass() // Limpia los metodo de pago seleccionado
        validarSubmit() // Resetear los inputs al cerrar


        let inputCuota = target.children[2].innerHTML
        cuotaPicked.innerHTML = inputCuota
        if (inputCuota == "Cuota 0" || inputCuota == "Cuota 1") {
            descuentoCuotaButton.style.display = "block"
        } else {
            descuentoCuotaButton.style.display = "none"
        }
        typePaymentWindow.classList.add("active");
        testCuotaSelected(target, cuotas)
    }
    return target
}

function testCuotaSelected(target, cuotas) {

    // PARA SOLAMENTE OBTENGA EL TIPO PARCIAL SI YA ESTA PAGADO PARCIALMENTE
    if (target.children[0].classList.contains("pagoParcial")) {
        try {
            let inputCuota = target.children[1]
            cuotaPicked.innerHTML = inputCuota.value

            typesPayments[0].previousElementSibling.remove()
            typesPayments[0].remove()
            typesPayments[1].classList.add("active")
            typesPayments[1].style.width = "100%"
            typesPayments[1].previousElementSibling.checked = true
            tipoPago.value = typesPayments[1].previousElementSibling.value
            pickedAmount.classList.add("active")
            calcularDineroRestante(target.children[2].innerHTML, cuotas)
        } catch (error) {

        }
    }
    else if (!target.children[0].classList.contains("pagoParcial") && !typesPaymentsWrapper.contains(pagoTotalLabel)) {
        typesPaymentsWrapper.insertAdjacentElement("afterbegin", pagoTotalLabel)
        typesPaymentsWrapper.insertAdjacentElement("afterbegin", pagoTotalInput)

        typesPayments[1].style.width = "50%"
        typesPayments[1].previousElementSibling.checked = false
        typesPayments[0].previousElementSibling.checked = true
        typesPayments[0].classList.add("active")


        typesPayments[1].classList.remove("active")
        pickedAmount.classList.remove("active")
        inputSubmit.classList.add("blocked")

        tipoPago.value = typesPayments[0].previousElementSibling.value
    }
}
//#endregion  


//#region Funciones helpers
function clearPickedType() {
    typesPayments.forEach(element => {
        element.classList.remove("active")
    });
}

function closeWindowSellCuota() {
    typePaymentWindow.classList.remove("active");
    cuotaPicked.innerHTML = ""
}

function clearPickedCuota() {
    // Limpiar metodo de pago
    metodoPagoPicked.value = ""

    // Limpiar cobrador
    cobradorSelected.innerHTML = "-----"
    cobrador.value = ""

    //Limpiar pago parcial
    amountParcialInput.innerHTML = ""
    amountParcialInput.value = ""

    cuotaPicked.innerHTML = ""
}
//#endregion  