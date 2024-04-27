let fromDate = document.querySelector(".fromDate")
let toDate = document.querySelector(".toDate")
let wrapperSelectTypePayments = document.querySelector(".wrapperSelectTypePayments")
let wrapperselectCobrador = document.querySelector(".selectCobrador")
document.addEventListener("click",(event)=>{
    if(!fromDate.contains(event.target)){
        fromDate.children[2].classList.remove("active")
    }
    if(!toDate.contains(event.target)){
        toDate.children[2].classList.remove("active")
    }
    // if(!wrapperSelectTypePayments.contains(event.target)){
    //     wrapperSelectTypePayments.children[2].classList.remove("active")
    // }
    if(!wrapperselectCobrador.contains(event.target)){
        wrapperselectCobrador.children[2].classList.remove("active")
    }

})