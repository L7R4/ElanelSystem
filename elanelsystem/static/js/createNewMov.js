const formEgresoIngreso = document.getElementById('formNewIngresoEgreso');
const confirmForm = document.getElementById('confirmMovimiento')

//#region CONTROLA EL MODAL ---------------------------------------------------------------------------------------
const main_modalNewEgresoIngreso = document.querySelector(".main_modalNewEgresoIngreso")
const buttonsNewMov = document.querySelectorAll(".buttonNewMov");
const closeModalEgresoIngreso = document.getElementById("closeModalEgresoIngreso")

const inputsID_egresos = [
    "denominacionMov",
    "nroIdentificacionMov",
    "tipoID",
    "tipoComprobante",
    "nroComprobanteMov",
    "adelanto",
    "premio",
]

const inputsID_ingresos = [
    "tipoMoneda",
]

function newEgreso() {

    tittleModalEgresoIngreso.textContent = "Nuevo egreso"
    typeMov.value = "Egreso"
    document.getElementById("fechaMov").value = dateToday()

    // Esconde todos los inputs que son solamente para crear un INGRESO
    inputsID_ingresos.forEach(element => {
        let inputObject = document.getElementById(element)
        let wrapper = inputObject.closest('.wrapperInput')
        wrapper.style.display = "None"
    });

    // Muestra todos los inputs que son solamente para crear un EGRESO
    inputsID_egresos.forEach(element => {
        let inputObject = document.getElementById(element)
        let wrapper = inputObject.closest('.wrapperInput')
        wrapper.style.display = "flex"
    });

    main_modalNewEgresoIngreso.classList.add("active")
    main_modalNewEgresoIngreso.style.opacity = "1"
}

function newIngreso() {
    tittleModalEgresoIngreso.textContent = "Nuevo Ingreso"
    typeMov.value = "Ingreso"
    document.getElementById("fechaMov").value = dateToday()

    // Esconde todos los inputs que son solamente para crear un EGRESO
    inputsID_egresos.forEach(element => {
        let inputObject = document.getElementById(element)
        let wrapper = inputObject.closest('.wrapperInput')
        wrapper.style.display = "None"
    });
    // Muestra todos los inputs que son solamente para crear un INGRESO
    inputsID_ingresos.forEach(element => {
        let inputObject = document.getElementById(element)
        let wrapper = inputObject.closest('.wrapperInput')
        wrapper.style.display = "flex"
    });

    main_modalNewEgresoIngreso.classList.add("active")
    main_modalNewEgresoIngreso.style.opacity = "1"

}


// Cierra el modal
closeModalEgresoIngreso.addEventListener("click", () => {
    main_modalNewEgresoIngreso.style.opacity = "0"
    setTimeout(() => {
        main_modalNewEgresoIngreso.classList.remove("active")
        clearInputs()
    }, 300)
})

//#endregion ----------------------------------------------------------------------------------------------------------


//#region ENVIA EL FORMULARIO DEL MOVIMIENTO ----------------------------------------------------------------------------
confirmForm.addEventListener("click", () => {
    makeMov().then(data => {
        updateMovs(currentPage);
        updateResumenDinero(currentPage);
        main_modalNewEgresoIngreso.style.opacity = "0"
        setTimeout(() => {
            main_modalNewEgresoIngreso.classList.remove("active")
        }, 300)
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
//#endregion -----------------------------------------------------------------------------------------------------------------

function clearInputs() {
    let inputs = document.querySelectorAll(".wrapperInput input")
    inputs.forEach(element => element.value = "")
    let inputsSelectPremio_Adelanto = document.querySelectorAll(".inputSelectPremio_Adelanto")
    inputsSelectPremio_Adelanto.forEach(element => element.checked = false)
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
