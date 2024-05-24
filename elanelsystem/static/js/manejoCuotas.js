const cuotasWrapper = document.querySelectorAll(".cuota")
const btnDescuentoCuota = document.getElementById("btnDescuentoCuota")
const payCuotaForm = document.getElementById("payCuotaForm")

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

async function formPOST(form, url) {
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
            },
            body: new FormData(form)
        })
        if (!res.ok) {
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
    formPOST(form, "ventas/detalle_venta/descuento_cuota/").then(async response => {
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
        showFormCuotas(cuota.id)

        calcularDineroRestante(cuotaSelected.children[2].innerHTML, data)

        // // SELECCIONA EL TIPO DE PAGO
        // typesPayments.forEach(type => {
        //     type.addEventListener("click", () => {
        //         selectTypePayment(type, data)
        //     })

        // })
    })
});



function testCuotaSelected(cuota, cuotas) {
    let marcaStatusCuota = cuota.querySelector(".marca")
    let typesPayments = payCuotaForm.querySelector(".typesPayments > wrapperChoices")

    // PARA SOLAMENTE OBTENGA EL TIPO PARCIAL SI YA ESTA PAGADO PARCIALMENTE
    if (marcaStatusCuota.classList.contains("pagoParcial")) {
        // Escondemos el tipo de pago total
        typesPayments.querySelector("#choiceTotal").style.display = "none"

        // Marcamos como check el tipo de pago parcial para que quede como obligatorio
        typesPayments.querySelector("#choiceParcial > input").checked = true

        // Mostramos el input del dinero a colocar
        pickedAmount.classList.add("active")

        // Calculamos el dinero faltante
        calcularDineroRestante(cuota.id, cuotas)

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

function showFormCuotas(cuotaSelected) {

    let tittleCuotaSelected = document.querySelector("#payCuotaForm > .cuotaPicked")
    tittleCuotaSelected.innerHTML = cuotaSelected

    validarSiAplicaDescuento(cuotaSelected)



    payCuotaForm.classList.add("active")
}

// Funcion para verificar si son las cuotas 0 o 1 para disponer del boton para aplicar descuentos
function validarSiAplicaDescuento(cuota) {
    if (cuota == "Cuota 0" || cuota == "Cuota 1") {
        descuentoCuotaButton.style.display = "block"
    } else {
        descuentoCuotaButton.style.display = "none"
    }
}

function selectCuota(target, cuotas) {
    if (!target.children[0].classList.contains("pago") && !target.children[0].classList.contains("pagoBloqueado")) {
        clearPickedCuota() // Limpia todos los valores de los inputs
        clearPickedClass() // Limpia los metodo de pago seleccionado
        validarSubmit() // Resetear los inputs al cerrar



        typePaymentWindow.classList.add("active");
        testCuotaSelected(target, cuotas)
    }
    return target
}

function hideFormCuotas() {

}
//#endregion  