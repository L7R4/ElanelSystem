const buttonSelectOption = document.querySelector(".selectedOption");
const optionWrapper = document.querySelector(".options");
const options = document.querySelectorAll(".wrapperSelectTypePayments >.options > li");
const tipoDePago = document.getElementById("tipoDePago")
let textOptionPicked = document.querySelector(".selectedOption > h2")

buttonSelectOption.addEventListener("click" ,() =>{
    optionWrapper.classList.toggle("active")
})

options.forEach(element => {
    element.addEventListener("click", ()=>{
        textOptionPicked.innerHTML = element.innerHTML
        tipoDePago.value = element.innerHTML
    })
});

