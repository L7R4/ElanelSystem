/*
    Esto sirve para manejar los inputs radio.
    La logica se basa en que cuando uno esta seleccionado
    y se le da click, que este mismo se deseleccione.
*/ 

let labelsRadios = document.querySelectorAll(".inputsRadiosContainer > label");
labelsRadios.forEach(label =>{
    label.addEventListener("click",(e)=>{
        if(label.previousElementSibling.checked){
            e.preventDefault()
            label.previousElementSibling.checked = false
        }
    })
})
