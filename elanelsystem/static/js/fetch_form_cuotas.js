const checkboxes = document.querySelectorAll(".cuota > input")
const inputSubmit = document.getElementById("sendPayment")
const closeTipoPago = document.getElementById("closeTipoPago")

let metodoPagoPicked = document.getElementById("metodoPago")
let methodPayments = document.querySelectorAll(".methodPayments > ul > li")

const typePaymentWindow = document.querySelector(".tipo_pago")
let cuotaPicked = document.querySelector(".cuotaPicked")

var url = window.location.pathname;

const cuotaSuccess = document.querySelector(".cuotaSuccess")
const cuotaSuccessText = document.querySelector(".cuotaPagada")

const descuentoCuotaButton = document.getElementById("descuentoCuota")
const descuentoCuotaWrapper = document.querySelector(".descuentoCuota")
const inputDescuentoCuota = document.getElementById("submitDescuento")

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
async function refreshData() {
    const response = await fetch(url, {
        method: 'get',
        headers: {'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'},
    });
    const data = await response.json();
    return data;
}

fetch(url,{
    method: 'get',
    headers: {'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' ,}
})
.then(response => response.json())
.then(data =>{
    console.log(data)
    changeCheckboxes(checkboxsFilterPagados(data))
    changeCheckboxesAtrasados(checkboxsFilterAtrasados(data))
    changeCheckboxesPagadosParcialmente(checkboxsFilterPagadosParcialmente(data))

    // CUANDO SE ABONA UNA CUOTA
    let resto;
    checkboxes.forEach(element => {
        element.parentElement.addEventListener("click",async ()=>{
            
            if(!element.previousElementSibling.classList.contains("pago")){
                validarSubmit()

                // REFRESCAR LOS DATOS PARA OBTENER EL DINERO RESTANTE
                let data = await refreshData()
                let cuotaSeleccionada = data.filter(c=> c.cuota === element.value)
                calcularDineroRestante(cuotaSeleccionada[0])
                resto = parseInt(dineroRestante.innerHTML.match(/\d+/)[0])
                console.log(resto)
                // VALIDAR INPUT DE DINERO PARCIAL
                amountParcialInput.addEventListener("input",()=>{
                    if(amountParcialInput.value > resto){
                        amountParcialInput.classList.add("invalido")
                    }else{
                        amountParcialInput.classList.remove("invalido")
                    }
                    validarSubmit()
                })

                cuotaPagada = element.value;
                cuotaPicked.innerHTML = element.value
                cuotaParaDescuento.value = element.value
                typePaymentWindow.classList.add("active");
                inputSubmit.addEventListener("click", async () =>{
                    let data = await refreshData()
                    let amount = 0;

                    if (tipoPago.value == "total") {
                        isChecked = "Pagado";
                        element.checked = true
                        let cuota = data.filter(c=> c.cuota === element.value)
                        amount = cuota[0]["total"] - cuota[0]["descuento"]
                        console.log("EL monto a pagar es: "+ amount)
                    }else if(tipoPago.value == "parcial"){
                        isChecked = "Parcial";
                        amount =amountParcial.value
                        console.log("EL monto a pagar es: "+ amount)

                    }
                    
                    if(resto - parseInt(amountParcialInput.value) == 0){
                        resto = 0
                        console.log("weps")
                    }

                    testSale(element,isChecked,resto)
                    let post = fetch(url,{
                        method: "POST",
                        body: JSON.stringify({ 
                            cuota: cuotaPagada, 
                            status: isChecked,
                            metodoPago: metodoPago.value,
                            amountParcial: amountParcial.value,
                        }),
                        headers: {
                            "X-CSRFToken": getCookie('csrftoken')
                        }
                    })
                    .then(async response2 => {
                        response2.json()


                        cuotaSuccessText.innerHTML = "<strong>" + cuotaPagada +"</strong> ha sido abonada correctamente"
                        setTimeout(()=>{
                            cuotaSuccess.classList.add("active")
                        },"500")
                        typePaymentWindow.classList.remove("active");

                        clearPickedClass()
                        clearPickedCuota()
                        setTimeout(()=>{
                            cuotaSuccess.classList.remove("active")
                        },"3000")
                    })
                })
            }
        })
    })

    // PARA APLICAR DESCUENTO A UNA CUOTA
    inputDescuentoCuota.addEventListener('click', ()=>{
        let post = fetch(url,{
            method: "POST",
            body: JSON.stringify({ 
                cuota: cuotaParaDescuento.value,
                descuento: dineroDescuento.value
                
            }),
            headers: {
                "X-CSRFToken": getCookie('csrftoken')
            }
        })
        .then(async response2 =>{
            response2.json()

            let data = await refreshData()
            let cuotaSeleccionada = data.filter(c=> c.cuota === cuotaParaDescuento.value)
            calcularDineroRestante(cuotaSeleccionada[0])
            resto = parseInt(dineroRestante.innerHTML.match(/\d+/)[0])
            console.log(resto)
            console.log(data)
            
            descuentoCuotaWrapper.classList.remove("active")
            dineroDescuento.value = ""
            cuotaParaDescuento.value =""
        })
    })
    
})

// BOTON PARA ACTIVAR PARA APLICAR DESCUENTO
descuentoCuotaButton.addEventListener('click',()=>{
    descuentoCuotaWrapper.classList.toggle("active")
})



function testSale(checkboxToTest,typePayment,resto) {
    console.log("Resto en la funcion: "+resto)
    if(typePayment == "Pagado"){
        if (checkboxToTest.previousElementSibling.classList.contains("atrasado")) {
            checkboxToTest.previousElementSibling.classList.remove("atrasado")
            checkboxToTest.parentElement.removeChild(checkboxToTest.parentElement.children[3])
          }
        checkboxToTest.previousElementSibling.classList.add("pago")
    }else if(typePayment == "Parcial"){
        if (checkboxToTest.previousElementSibling.classList.contains("atrasado")) {
            checkboxToTest.previousElementSibling.classList.remove("atrasado")
            checkboxToTest.parentElement.removeChild(checkboxToTest.parentElement.children[3])
        }else if(resto == 0)
        {
            console.log("Entro a pago")
            
            checkboxToTest.previousElementSibling.classList.remove("pagoParcial")
            checkboxToTest.checked = true
            checkboxToTest.previousElementSibling.classList.add("pago")
        }else{
            console.log("Entro a pago parcial")
            checkboxToTest.previousElementSibling.classList.add("pagoParcial")
        }
    }
}




let cuotaPagada;
let isChecked;

function calcularDineroRestante(cuotaSeleccionada){
    let listPagos = cuotaSeleccionada["pagoParcial"]["amount"]
    let sumaPagos = listPagos.reduce((acc,num) => acc + num["value"], 0);
    let resto = cuotaSeleccionada["total"] - (sumaPagos + cuotaSeleccionada["descuento"])
    dineroRestante.innerHTML = "Dinero restante: $" + resto
    return resto
}

methodPayments.forEach(element =>{
    element.addEventListener("click", ()=>{
        metodoPagoPicked.value = element.innerHTML
        clearPickedClass()
        element.classList.add("picked")
        validarSubmit()
    })
})

function clearPickedClass(){
    methodPayments.forEach(element => {
        element.classList.remove("picked")
    });
}


function clearPickedCuota() {
    // Limpiar metodo de pago
    metodoPagoPicked.value = ""

    // Limpiar cobrador
    cobradorSelected.innerHTML ="-----"
    cobrador.value = ""

    //Limpiar pago parcial
    amountParcialInput.innerHTML=""
    amountParcialInput.value=""
}

closeTipoPago.addEventListener("click", ()=>{
    typePaymentWindow.classList.remove("active");

    typePaymentWindow.children[1].insertAdjacentElement("afterbegin",pagoTotalLabel)
    typePaymentWindow.children[1].insertAdjacentElement("afterbegin",pagoTotalInput)
    typesPayments[1].classList.remove("active")
    pickedAmount.classList.remove("active")
    typesPayments[1].style.width = "50%"
    typesPayments[0].previousElementSibling.checked = true
    tipoPago.value = typesPayments[0].previousElementSibling.value
    typesPayments[0].classList.add("active")

    // Limpiar ventana de tipo de pago
    clearPickedCuota()
    clearPickedClass()

    // Resetear los inputs al cerrar
    validarSubmit()


})


function checkboxsFilterPagados(checkboxes) {
    let cuotas_pagas = checkboxes.filter(c => c.status === "Pagado")
    return cuotas_pagas
}
function changeCheckboxes(lista) {
    let lista_cuotas = lista.map(item => item.cuota)
    console.log(lista_cuotas)
    checkboxes.forEach(element => {
        if(lista_cuotas.includes(element.value)){
            element.checked = true;
            element.previousElementSibling.classList.add("pago");
        }
    });
}


function checkboxsFilterAtrasados(checkboxes) {
    let cuotas_atrasadas = checkboxes.filter(c => c.status === "Atrasado")
    return cuotas_atrasadas
}
function changeCheckboxesAtrasados(lista) {
    let lista_cuotasAtrasadas = lista.map(item => item.cuota)
    checkboxes.forEach(element => {
        if(lista_cuotasAtrasadas.includes(element.value)){
            element.previousElementSibling.classList.add("atrasado");
            let diaAtrasado = lista.filter(cuota => cuota["cuota"] == element.value)
            let diasAtrasadostext = "<h4 class='textAtrasado'>" + diaAtrasado[0]["diasRetraso"] + " dias</h4>"
            element.parentElement.insertAdjacentHTML("beforeend",diasAtrasadostext)
        }
    });
}


function checkboxsFilterPagadosParcialmente(checkboxes) {
    let cuotas_pagas = checkboxes.filter(c => c.status === "Parcial")
    return cuotas_pagas
}
function changeCheckboxesPagadosParcialmente(lista) {
    let lista_cuotas = lista.map(item => item.cuota)
    checkboxes.forEach(element => {
        if(lista_cuotas.includes(element.value)){
            element.previousElementSibling.classList.add("pagoParcial");
        }
    });
}

function validarSubmit(){
    if(tipoPago.value =="total"){
        if(cobrador.value != "" && metodoPago.value != ""){
            inputSubmit.classList.remove("blocked")
        }else{
            inputSubmit.classList.add("blocked")
        }
    }else if(tipoPago.value =="parcial"){
        if(cobrador.value != "" && metodoPago.value != "" && !amountParcialInput.classList.contains("invalido") && amountParcialInput.value !=""){
            inputSubmit.classList.remove("blocked")
        }else{
            inputSubmit.classList.add("blocked")
        }
    }
    
}




