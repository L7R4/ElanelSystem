// const cobradores = document.querySelectorAll(".cobradoresList > li")
let cobradorSelected = document.querySelector(".cobrador")


const typesPayments = document.querySelectorAll(".typesPayments > label")


const amountParcialInput = document.getElementById("amountParcial") 

// SELECCIONAR EL TIPO DE PAGO
let pagoTotalInput = typesPayments[0].previousElementSibling
let pagoTotalLabel = typesPayments[0]
tipoPago.value = typesPayments[0].previousElementSibling.value

checkboxes.forEach(element =>{
    element.parentElement.addEventListener("click",()=>{
        if (element.previousElementSibling.classList.contains("pagoParcial")) {
            typesPayments[0].previousElementSibling.remove()
            typesPayments[0].remove()
            typesPayments[1].classList.add("active")
            typesPayments[1].style.width = "100%"
            typesPayments[1].previousElementSibling.checked = true
            tipoPago.value = typesPayments[1].previousElementSibling.value
            pickedAmount.classList.add("active")

        }
    })
})

typesPayments.forEach(element => {
    element.addEventListener("click", ()=>{
        element.previousElementSibling.checked = true
        tipoPago.value = element.previousElementSibling.value
        validarSubmit()
        clearPickedType()
        element.classList.add("active")
        if(parcial.checked == true){
            pickedAmount.classList.add("active")
        }else{
            pickedAmount.classList.remove("active")
        }
    })
});

function clearPickedType() {
    typesPayments.forEach(element => {
        element.classList.remove("active")
    });
}

// ------------------------------------------------------------


// ELEGIR COBRADOR
// cobradorSelectedWrapper.addEventListener("click",()=>{
//     cobradoresList.classList.toggle("active")
// })

// cobradores.forEach(element => {
//     element.addEventListener("click",()=>{
//         cobradorSelected.innerHTML = element.innerHTML
//         inputCobrador.value = element.innerHTML
//         validarSubmit()
//     })
// });
// ------------------------------------------------------------
