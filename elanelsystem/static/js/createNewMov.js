const formEgresoIngreso = document.getElementById('formNewIngresoEgreso');
const confirmForm = document.getElementById('confirmMovimiento')

// CONTROLA EL MODAL ---------------------------------------------------------------------------------------
const main_modalNewEgresoIngreso = document.querySelector(".main_modalNewEgresoIngreso")
const buttonsNewMov = document.querySelectorAll(".buttonNewMov");
const closeModalEgresoIngreso = document.getElementById("closeModalEgresoIngreso")

const inputTypeComprobante = document.getElementById("tipoComprobanteMov").parentElement
const inputNroComprobante = document.getElementById("nroComprobanteMov").parentElement
const inputTypeID = document.getElementById("tipoIdentificacionMov").parentElement
const inputNroID = document.getElementById("nroIdentificacionMov").parentElement
const inputDenominacion = document.getElementById("denominacionMov").parentElement
const inputTypeMoneda = document.getElementById("tipoMonedaMov").parentElement
const inputSelectAdelanto_Premio = document.querySelector(".wrapperSelectAdelanto_Premio").parentElement
const inputsEgresoIngreso = document.querySelectorAll(".inputEgresoIngreso")

buttonsNewMov.forEach(element => {
    element.addEventListener('click', ()=>{
        fechaMov.value = dateToday()
        if(element.id == "buttonEgreso"){
            tittleModalEgresoIngreso.textContent = "Nuevo egreso"
            formNewIngresoEgreso.insertBefore(inputDenominacion,formNewIngresoEgreso.children[2])
            formNewIngresoEgreso.insertBefore(inputNroID,formNewIngresoEgreso.children[2])
            formNewIngresoEgreso.insertBefore(inputTypeID,formNewIngresoEgreso.children[2])
            formNewIngresoEgreso.insertBefore(inputNroComprobante,formNewIngresoEgreso.children[2])
            formNewIngresoEgreso.insertBefore(inputTypeComprobante,formNewIngresoEgreso.children[2])
            formNewIngresoEgreso.insertAdjacentElement('beforeend',inputSelectAdelanto_Premio)
            inputTypeMoneda.remove()
            typeMov.value = "Egreso"

        }else if(element.id == "buttonIngreso"){
            tittleModalEgresoIngreso.textContent = "Nuevo ingreso"
            inputTypeComprobante.remove()
            inputTypeID.remove()
            inputDenominacion.remove()
            inputNroComprobante.remove()
            inputNroID.remove()
            inputSelectAdelanto_Premio.remove()
            formNewIngresoEgreso.insertBefore(inputTypeMoneda,formNewIngresoEgreso.children[2])
            typeMov.value = "Ingreso"
        }
        main_modalNewEgresoIngreso.classList.add("active")
        main_modalNewEgresoIngreso.style.opacity = "1"
    })
});

// Cierra el modal
closeModalEgresoIngreso.addEventListener("click",()=>{
    main_modalNewEgresoIngreso.style.opacity = "0"
    setTimeout(()=>{
        main_modalNewEgresoIngreso.classList.remove("active")
        clearInputs()
    },300)
})

// ----------------------------------------------------------------------------------------------------------



// ENVIA EL FORMULARIO DEL MOVIMIENTO ----------------------------------------------------------------------------

confirmForm.addEventListener("click",()=>{
    makeMov().then(data => {
        updateMovs(currentPage);
        updateResumenDinero(currentPage);
        main_modalNewEgresoIngreso.style.opacity = "0"
        setTimeout(()=>{
            main_modalNewEgresoIngreso.classList.remove("active")
        },300)
        clearInputs()
    })
    .catch(error => console.error('Error:', error));
})


// FUNCION PARA TOMAR EL FORMULARIO
async function makeMov() {
    let newMov = await fetch("/create_new_mov/", {
        method: 'POST',
        body: new FormData(formEgresoIngreso),
        headers: {
            "X-CSRFToken": getCookie('csrftoken')
        }
    })
    let data = await newMov.json()
    return data;
}

// -----------------------------------------------------------------------------------------------------------------

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

function clearInputs() {
    inputsEgresoIngreso.forEach(element => element.value = "")
    if(document.querySelector(".wrapperSelectAdelanto_Premio")){
        let inputsSelectPremio_Adelanto = document.querySelectorAll(".inputSelectPremio_Adelanto")
        inputsSelectPremio_Adelanto.forEach(element => element.checked = false)   
    }
}

// Colocar la fecha automatica de hoy en el input de "Fecha de emicion"
function dateToday() {
    // Obtener la fecha actual
    var fechaActual = new Date();

    // Obtener el año, mes y día
    var año = fechaActual.getFullYear();
    var mes = fechaActual.getMonth() + 1; // Los meses van de 0 a 11, por lo que sumamos 1
    var dia = fechaActual.getDate();

    // Formatear la fecha como una cadena (en formato DD/MM/YYYY)
    var fechaFormateada = (dia < 10 ? '0' : '') + dia + '/' + (mes < 10 ? '0' : '') + mes + '/' + año;

    return fechaFormateada
}
