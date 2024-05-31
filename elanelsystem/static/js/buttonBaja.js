// Variables para form de baja
let formConfirmBajaWrapper = document.querySelector(".formConfirmBajaWrapper");
let buttonBaja = document.getElementById("bajaBtn");
let yesConfirmFormBaja = document.getElementById("yesConfirm")
let notConfirmFormBaja = document.getElementById("noConfirm")
let inputDescuento = document.getElementById("porcentage")

// Variables para form del descuento
let editPorcentajeBtn = document.getElementById("porcentajeBtn");
let formPassword = document.querySelector("#formPassword")
let cancelFormPass = document.getElementById("notConfirmPass")
let confirmFormPass = document.getElementById("confirmPass")


// #region Funcion del formulario FETCH
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


async function formFETCH(form, url) {
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
            },
            body: JSON.stringify(form)
        })
        if (!res.ok) {
            throw new Error("Error")
        }
        const data = await res.json()
        return data;
    } catch (error) {
    }
}
// #endregion

// #region Management form baja
// Activa el formulario de baja
buttonBaja.addEventListener("click", () => {
    formConfirmBajaWrapper.classList.add("active")
})

// Cierra el formulario de baja
notConfirmFormBaja.addEventListener("click", () => {
    formConfirmBajaWrapper.classList.remove("active")
})

yesConfirmFormBaja.addEventListener('click', async () => {
    let form = { 'porcentage': porcentage.value, 'motivo': motivo.value, 'motivoDescripcion': bajaObservacion.value }
    let response = await formFETCH(form, `/ventas/detalle_venta/${venta_id}/dar_baja/`)
    inputDescuento.classList.remove("enable")

    window.open(response.urlPDF)
    window.location.href = response.urlUser;

})

// #endregion

// #region Management descuento form baja

// Muestra el formulario para colocar el password para el descuento personalizado
let backgroundBlockForm = `<div class="backgroundBlockForm"></div>`
editPorcentajeBtn.addEventListener("click", () => {
    formPassword.classList.add("active")
    let formBaja = formConfirmBajaWrapper.querySelector("#formBaja")
    formBaja.insertAdjacentHTML('afterbegin', backgroundBlockForm);

})

// Envia el password para el descuento personalizado

confirmFormPass.addEventListener("click", async () => {
    let form = { 'pass': clave.value, 'motivo': 'baja' }
    let response = await formFETCH(form, `/usuario/administracion/requestkey/`)
    console.log(`message: ${response.message}`)

    if (response.status) {
        formPassword.classList.remove("active")
        formConfirmBajaWrapper.querySelector(".backgroundBlockForm").remove()
        inputDescuento.classList.add("enable")
        if (formPassword.querySelector('messageErrorPass')) {
            formPassword.querySelector('messageErrorPass').remove()
        }
    } else {
        let p_HTML = `<p class="messageErrorPass">${response.message}</p>`
        formPassword.insertAdjacentHTML('beforeend', p_HTML)
    }
})


// Cancela el formulario de password para descuento personalizado
cancelFormPass.addEventListener("click", () => {
    formPassword.classList.remove("active")
    formConfirmBajaWrapper.querySelector(".backgroundBlockForm").remove()
})

// #endregion

// confirmPassword.addEventListener("click", () => {
//     let post = fetch(url, {
//         method: "POST",
//         body: JSON.stringify({
//             clave: clave.value,
//         }),
//         headers: {
//             "X-CSRFToken": getCookie('csrftoken'),
//             'Content-Type': 'application/json',

//         }
//     })
//         .then(response => response.json())
//         .then(data => {
//             if (data["ok"]) {
//                 formClave.classList.remove("active")
//                 confirmBajaFormWrapper.classList.remove("block")
//                 inputEditPorcentage.removeAttribute("readonly")
//                 inputEditPorcentage.style.backgroundColor = "transparent"
//                 inputEditPorcentage.style.cursor = "text"
//                 if (document.querySelector(".errorMessage")) {
//                     document.querySelector(".errorMessage").remove()
//                 }
//                 inputEditPorcentage.name = "porcentage" + data.c
//             }
//         })
//         .catch(error => {
//             if (!document.querySelector(".errorMessage")) {
//                 let errorMessage = document.createElement('p');
//                 errorMessage.textContent = "Contraseña incorrecta"
//                 errorMessage.className = 'errorMessage';
//                 inputClave.appendChild(errorMessage)
//             }
//         })
// })

// motivoSelectedWrapper.addEventListener("click", () => {
//     motivosList.classList.toggle("active");
// });
// motivos.forEach(motivo => {
//     motivo.addEventListener("click", () => {
//         selectMotivo(motivo)
//     })
// });

// function selectMotivo(target) {
//     textMotivo.innerHTML = target.innerHTML;
//     motivo.value = target.innerHTML;
//     validarSubmit()
// }

// Esto evita el comportamiento predeterminado del  "Enter"
document.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
        e.preventDefault();
    }
});