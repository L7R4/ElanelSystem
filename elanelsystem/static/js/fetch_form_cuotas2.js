var url = window.location.pathname;

const checkboxes = document.querySelectorAll(".cuota > input")
const cuotasWrapper = document.querySelectorAll(".cuota")


const inputSubmit = document.getElementById("sendPayment")
const closeWindowSell = document.getElementById("closeTipoPago")

let metodoPagoPicked = document.getElementById("metodoPago")
let methodPayments = document.querySelectorAll(".methodPayments > ul > li")

const typePaymentWindow = document.querySelector(".tipo_pago")
let cuotaPicked = document.querySelector(".cuotaPicked")


const cuotaSuccess = document.querySelector(".cuotaSuccess")
const cuotaSuccessText = document.querySelector(".cuotaPagada")

const descuentoCuotaButton = document.getElementById("descuentoCuota")

const descuentoCuotaWrapper = document.querySelector(".descuentoCuota")
const inputDescuentoCuota = document.getElementById("submitDescuento")


const cobradorSelectedWrapper = document.querySelector(".cobradorSelectedWrapper")
const cobradores = document.querySelectorAll(".cobradoresList > li")
const cobradoresList = document.querySelector(".cobradoresList")
let inputCobrador = document.getElementById("cobrador")
let cobradorSelected = document.querySelector(".cobrador")
const amountParcialInput = document.getElementById("amountParcial")

const typesPayments = document.querySelectorAll(".typesPayments > label")
const typesPaymentsWrapper = document.querySelector(".typesPayments")
const pickedAmount = document.querySelector(".pickedAmount")

let pagoTotalInput = typesPayments[0].previousElementSibling
let pagoTotalLabel = typesPayments[0]
tipoPago.value = typesPayments[0].previousElementSibling.value

let amountParcial = document.getElementById("amountParcial")


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

async function fetchCuotas() {
    const response = await fetch(url, {
        method: 'get',
        headers: { 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' },
        cache: 'no-store',
    });
    const data = await response.json();
    return data;
}

let cuotaSelected;
async function main() {
    const cuotas = await fetchCuotas();
    // COLOCA LOS ESTADOS DE LAS CUOTAS SEGUN EL FETCH
    changeCheckboxes(cuotas, "Pagado")
    changeCheckboxes(cuotas, "Atrasado")
    changeCheckboxes(cuotas, "Parcial")
    changeCheckboxes(cuotas, "Bloqueado")



    // VENTANA DE ABONAR CUOTA
    cuotasWrapper.forEach(cuota => {
        cuota.addEventListener('click', async () => {
            let data = await fetchCuotas()

            // ABRE LA VENTANA DE ABONAR CUOTA Y VALIDA SI ESTA PAGADO PARCIALMENTE
            cuotaSelected = selectCuota(cuota, data)
            calcularDineroRestante(cuotaSelected.children[2].innerHTML, data)


            // SELECCIONA EL TIPO DE PAGO
            typesPayments.forEach(type => {
                type.addEventListener("click", () => {
                    selectTypePayment(type, data)
                })

            })
        })
    });
    closeWindowSell.addEventListener("click", closeWindowSellCuota)


    // SELECCIONA COBRADOR
    cobradorSelectedWrapper.addEventListener("click", () => {
        cobradoresList.classList.toggle("active");
    });
    cobradores.forEach(cobrador => {
        cobrador.addEventListener("click", () => {
            selectCobrador(cobrador)
        })
    });



    // SELECCIONA EL METODO DE PAGO
    methodPayments.forEach(method => {
        method.addEventListener("click", () => {
            selectMethodPayment(method)
        })

    })

    // VALIDA INPUT DINERO PARCIAL
    amountParcialInput.addEventListener('click', async () => {
        const cuotas = await fetchCuotas();
        amountParcialInput.addEventListener("input", () => {
            validarInputPagoParcial(calcularDineroRestante(cuotaPicked.innerHTML, cuotas))
        })
    })

    // BOTON PARA ACTIVAR PARA APLICAR DESCUENTO
    descuentoCuotaButton.addEventListener('click', () => {
        descuentoCuotaWrapper.classList.toggle("active")
    })
}
main();

inputSubmit.addEventListener("click", async () => {
    let data = await fetchCuotas()
    let amount = 0;
    let isChecked;
    let cuotaPorAbonar = cuotaPicked
    if (tipoPago.value == "total") {
        isChecked = "Pagado";
        cuotaPorAbonar.previousElementSibling.checked = true
        let cuota = data.filter(c => c.cuota === cuotaPorAbonar.innerHTML)
        amount = cuota[0]["total"] - cuota[0]["descuento"]
    } else if (tipoPago.value == "parcial") {
        isChecked = "Parcial";
        amount = amountParcial.value
    }

    let post = fetch(url, {
        method: "POST",
        body: JSON.stringify({
            cuota: cuotaPorAbonar.innerHTML,
            status: isChecked,
            metodoPago: metodoPago.value,
            amountParcial: amount,
            cobrador: cobrador.value

        }),
        headers: {
            "X-CSRFToken": getCookie('csrftoken')
        }
    })
        .then(async response2 => {
            response2.json()
            let data = await fetchCuotas();
            // PARA VALIDAR SI LA CUOTA YA SE PAGO TOTALMENTE O NO
            let resto = calcularDineroRestante(cuotaPorAbonar.innerHTML, data)
            testSale(cuotaSelected, isChecked, resto)
            //---------------------------

            changeCheckboxes(data, "Atrasado")

            amount = 0
            isChecked = ""

            cuotaSuccessText.innerHTML = "<strong>" + cuotaPorAbonar.innerHTML + "</strong> ha sido abonada correctamente"
            setTimeout(() => {
                cuotaSuccess.classList.add("active")
            }, "500")
            typePaymentWindow.classList.remove("active");
            clearPickedCuota()

            clearPickedClass()
            setTimeout(() => {
                cuotaSuccess.classList.remove("active")
            }, "3000")
        })
})

// PARA APLICAR DESCUENTO A UNA CUOTA
inputDescuentoCuota.addEventListener('click', () => {
    let post = fetch(url, {
        method: "POST",
        body: JSON.stringify({
            cuota: cuotaPicked.innerHTML,
            descuento: dineroDescuento.value

        }),
        headers: {
            "X-CSRFToken": getCookie('csrftoken')
        }
    })
        .then(async response2 => {
            response2.json()

            let data = await fetchCuotas()
            calcularDineroRestante(cuotaPicked.innerHTML, data)
            descuentoCuotaWrapper.classList.remove("active")
            dineroDescuento.value = ""
            cuotaParaDescuento.value = ""
        })
})

function testSale(cuotaTest, typePayment, resto) {

    if (typePayment == "Pagado") {
        if (cuotaTest.children[0].classList.contains("atrasado")) {
            cuotaTest.children[0].classList.remove("atrasado")
            cuotaTest.removeChild(cuotaTest.children[3])
        }
        cuotaTest.children[0].classList.add("pago")
        cuotaTest.nextElementSibling.classList.remove("pagoBloqueado")
        cuotaTest.nextElementSibling.children[0].classList.remove("pagoBloqueado")
    } else if (typePayment == "Parcial") {
        if (cuotaTest.children[0].classList.contains("atrasado")) {
            cuotaTest.children[0].classList.remove("atrasado")
            cuotaTest.removeChild(cuotaTest.children[3])
            cuotaTest.children[0].classList.add("pagoParcial")
        }
        else if (resto == 0) {
            cuotaTest.children[0].classList.remove("pagoParcial")
            cuotaTest.children[1].checked = true
            cuotaTest.children[0].classList.add("pago")
            cuotaTest.nextElementSibling.classList.remove("pagoBloqueado")
            cuotaTest.nextElementSibling.children[0].classList.remove("pagoBloqueado")
        }
        else {
            cuotaTest.children[0].classList.add("pagoParcial")
        }
    }
}


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

// SELECCIONA COBRADOR
function selectCobrador(target) {
    cobradorSelected.innerHTML = target.innerHTML;
    inputCobrador.value = target.innerHTML;
    validarSubmit()
}

// SELECCIONA EL TIPO DE PAGO
function selectTypePayment(target, cuotas) {
    target.previousElementSibling.checked = true
    tipoPago.value = target.previousElementSibling.value
    clearPickedType()
    validarSubmit()
    target.classList.add("active")
    if (parcial.checked == true) {
        pickedAmount.classList.add("active")
        // calcularDineroRestante(cuotaPicked.innerHTML,cuotas)

    } else {
        pickedAmount.classList.remove("active")
    }
}
function clearPickedType() {
    typesPayments.forEach(element => {
        element.classList.remove("active")
    });
}


// SELECCIONA EL METODO DE PAGO
function selectMethodPayment(target) {
    metodoPagoPicked.value = target.innerHTML
    clearPickedClass()
    target.classList.add("picked")
    validarSubmit()
}
function clearPickedClass() {
    methodPayments.forEach(element => {
        element.classList.remove("picked")
    });
}

// VALIDA EL INPUT DE DINERO DE PAGO PARCIAL
function validarInputPagoParcial(resto) {
    if (amountParcialInput.value > resto) {
        amountParcialInput.classList.add("invalido")
    } else {
        amountParcialInput.classList.remove("invalido")
    }
    validarSubmit()
}

// CALCULA EL DINERO RESTANTE DE LA CUOTA
function calcularDineroRestante(objetivo, datos) {
    let cuotaSeleccionada = datos.filter(c => c.cuota === objetivo)
    let listPagos = cuotaSeleccionada[0]["pagoParcial"]["amount"]
    let sumaPagos = listPagos.reduce((acc, num) => acc + num["value"], 0);
    let resto = cuotaSeleccionada[0]["total"] - (sumaPagos + cuotaSeleccionada[0]["descuento"])
    dineroRestante.innerHTML = "Dinero restante: $" + resto
    return resto
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

function validarSubmit() {
    if (tipoPago.value == "total") {
        if (cobrador.value != "" && metodoPago.value != "") {
            inputSubmit.classList.remove("blocked")
        } else {
            inputSubmit.classList.add("blocked")
        }
    } else if (tipoPago.value == "parcial") {
        if (cobrador.value != "" && metodoPago.value != "" && !amountParcialInput.classList.contains("invalido") && amountParcialInput.value != "") {
            inputSubmit.classList.remove("blocked")
        } else {
            inputSubmit.classList.add("blocked")
        }
    }

}





// PARA FILTRAR LAS CUOTAS SEGUN SU ESTADO
function checkboxsFilter(checkboxes, estado) {
    let cuotasFiltered = checkboxes.filter(c => c.status === estado)
    // if(estado == "Atrasado"){
    //     cuotasFiltered = checkboxes.filter(c => c.status === estado || c.status === "Pagado")
    // }
    return cuotasFiltered
}

function changeCheckboxes(lista, estado) {
    let lista_cuotas = checkboxsFilter(lista, estado)
    let numberCuota = lista_cuotas.map(item => item.cuota)

    checkboxes.forEach(element => {
        if (numberCuota.includes(element.value) && estado == "Pagado") {
            element.checked = true;
            element.previousElementSibling.classList.add("pago");
        }

        else if (numberCuota.includes(element.value) && estado == "Atrasado") {
            let previousCuota;
            let diasAtrasadostext;

            for (let i = 0; i < lista.length; i++) {
                if (lista[i]["cuota"] === element.value && lista[i]["status"] === "Atrasado") {
                    previousCuota = lista[i - 1];
                    diasAtrasadostext = "<h4 class='textAtrasado'>" + lista[i]["diasRetraso"] + " dias</h4>"
                    break;
                }
            }
            if (previousCuota["status"] == "Pagado") {
                element.previousElementSibling.classList.add("atrasado");
                element.parentElement.insertAdjacentHTML("beforeend", diasAtrasadostext)
            }
            else {
                element.previousElementSibling.classList.add("pagoBloqueado");
                element.parentElement.classList.add("pagoBloqueado");
            }


        }
        else if (numberCuota.includes(element.value) && estado == "Parcial") {
            element.previousElementSibling.classList.add("pagoParcial");

        }
        else if (numberCuota.includes(element.value) && estado == "Bloqueado") {
            element.previousElementSibling.classList.add("pagoBloqueado");
            element.parentElement.classList.add("pagoBloqueado");

        }
        else if (numberCuota.includes(element.value) && estado == "Pendiente") {
            element.previousElementSibling.classList.remove("pagoBloqueado");
            element.parentElement.classList.remove("pagoBloqueado");
        }
    });
}

// LISTENER PARA CERRAR LA LISTA DE COBRADOR (POR AHORA)
document.addEventListener("click", function (event) {
    if (!cobradoresList.contains(event.target) && event.target !== cobradorSelectedWrapper) {
        cobradoresList.classList.remove("active");
    }
    if (!descuentoCuotaButton.contains(event.target) &&
        !descuentoCuotaWrapper.contains(event.target) &&
        ![...descuentoCuotaWrapper.childNodes].includes(event.target) &&
        ![...descuentoCuotaWrapper.childNodes[3].childNodes].includes(event.target)) {
        descuentoCuotaWrapper.classList.remove("active")
    }
});

// Esto evita el comportamiento predeterminado del botón "Tab" y el "Enter"
document.addEventListener('keydown', function (e) {
    if (e.key === 'Tab' || e.key === 'Enter') {
        e.preventDefault();
    }
});

