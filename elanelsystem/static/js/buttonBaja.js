let confirmBajaFormWrapper = document.querySelector(".buttonDeBaja > .formConfirmWrapper");
var confirmBajaFormWrapperAfter = window.getComputedStyle(confirmBajaFormWrapper, "::after");
let buttonBaja = document.getElementById("baja");
let cancelBaja = document.getElementById("noConfirm")
let editPorcentage = document.getElementById("editPorcentaje");
let yesConfirm = document.getElementById("yesConfirm")
let inputEditPorcentage = document.querySelector("#inputPorcentaje > div>input")
let formClave = document.querySelector(".formClave")
let notConfirm = document.getElementById("notConfirm")
let confirmPassword = document.getElementById("confirm")

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
    document.querySelector(".errorMessage") ? inputClave.removeChild(document.querySelector(".errorMessage")) : null
    clave.value != "" ? clave.value = "" : null

})
confirmPassword.addEventListener("click",()=>{
    let post = fetch(url,{
        method: "POST",
        body:JSON.stringify({ 
            clave: clave.value,
        }),
        headers: {
            "X-CSRFToken": getCookie('csrftoken'),
            'Content-Type': 'application/json',

        }
    })
    .then(response => response.json())
    .then(data =>{
       if (data["ok"]) {
            formClave.classList.remove("active")
            confirmBajaFormWrapper.classList.remove("block")
            inputEditPorcentage.removeAttribute("readonly")
            inputEditPorcentage.style.backgroundColor = "transparent"
            inputEditPorcentage.style.cursor = "text"
            if(document.querySelector(".errorMessage")){
                document.querySelector(".errorMessage").remove()
            }
            inputEditPorcentage.name = "porcentage"+data.c
       }
    })
    .catch(error => {
        if(!document.querySelector(".errorMessage")){
            let errorMessage = document.createElement('p');
            errorMessage.textContent = "Contraseña incorrecta"
            errorMessage.className = 'errorMessage';
            inputClave.appendChild(errorMessage)
        }
    })
})
