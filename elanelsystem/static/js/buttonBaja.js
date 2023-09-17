let confirmBajaFormWrapper = document.querySelector(".buttonDeBaja > .formConfirmWrapper");
var confirmBajaFormWrapperAfter = window.getComputedStyle(confirmBajaFormWrapper, "::after");
let buttonBaja = document.getElementById("baja");
let cancelBaja = document.getElementById("noConfirm")
let editPorcentage = document.getElementById("editPorcentaje");
let formClave = document.querySelector(".formClave")
let notConfirm = document.getElementById("notConfirm")

buttonBaja.addEventListener("click",()=>{
    confirmBajaFormWrapper.classList.add("active")
})

cancelBaja.addEventListener("click",()=>{
    confirmBajaFormWrapper.classList.remove("active")
})

editPorcentage.addEventListener("click",()=>{
    formClave.classList.add("active")
    confirmBajaFormWrapper.classList.add("block")
})
notConfirm.addEventListener("click",()=>{
    formClave.classList.remove("active")
    confirmBajaFormWrapper.classList.remove("block")
})
