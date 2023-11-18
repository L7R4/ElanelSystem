const main_modalNewEgresoIngreso = document.querySelector(".main_modalNewEgresoIngreso")
const buttonsNewMov = document.querySelectorAll(".buttonNewMov");
const closeModalEgresoIngreso = document.getElementById("closeModalEgresoIngreso")
const buttonConfirmMovimiento = document.getElementById("confirmMovimiento")

let urlMov = "/requestEgresoIngreso/"

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

// CONTROLA EL MODAL
buttonsNewMov.forEach(element => {
    element.addEventListener('click', ()=>{
        if(element.id == "buttonEgreso"){
            tittleModalEgresoIngreso.textContent = "Nuevo egreso"
            enteMov.previousElementSibling.textContent = "Egresa de:"
            typeMov.value = "Egreso"
        }else if(element.id == "buttonIngreso"){
            tittleModalEgresoIngreso.textContent = "Nuevo ingreso"
            enteMov.previousElementSibling.textContent = "Ingresa a:"
            typeMov.value = "Ingreso"
        }
        main_modalNewEgresoIngreso.classList.add("active")
        main_modalNewEgresoIngreso.style.opacity = "1"
    })
});


// ENVIA EL FORMULARIO DEL MOVIMIENTO

buttonConfirmMovimiento.addEventListener("click",()=>{
    makeMov().then(data =>{
        console.log(data)
    })
    .catch(error => {
        console.log(error)
    })
})



// CIERRA EL MODAL
closeModalEgresoIngreso.addEventListener("click",()=>{
    main_modalNewEgresoIngreso.style.opacity = "0"
    setTimeout(()=>{
        main_modalNewEgresoIngreso.classList.remove("active")
    },300)
})

// FUNCION PARA TOMAR EL FORMULARIO
async function makeMov() {
    console.log(typeMov.value, dineroMov.value, metodoPagoMov.value, fechaMov.value, enteMov.value, conceptoMov.value);
    let postMovimiento = await fetch(urlMov,{
        method: "POST",
        body:JSON.stringify({ 
            movimiento:typeMov.value,
            dineroMov: dineroMov.value,
            metodoPagoMov:metodoPagoMov.value,
            fechaMov: fechaMov.value,
            ente: enteMov.value,
            conceptoMov: conceptoMov.value,
        }),

        headers: {
            "X-CSRFToken": getCookie('csrftoken'),
            'Content-Type': 'application/json',
        }
    })
    
    let data = await postMovimiento.json()
    return data;
}