const inputsRadio = document.querySelectorAll(".selectEgreso_Ingreso > input");

inputsRadio.forEach(element => {
    element.addEventListener("click", ()=>{
        if(!element.nextElementSibling.classList.contains("active")){
            clearClassActive()
            element.nextElementSibling.classList.add("active")
        }else{
            clearClassActive()
            element.checked = false
        }
    })
});


function clearClassActive() {
    inputsRadio.forEach(element => {
        element.nextElementSibling.classList.remove("active")
    });
}