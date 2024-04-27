let confirmBaja = document.getElementById("yesConfirm");
let urlBaja = window.location.pathname
let inputPorcentage = document.getElementById("porcentage")
let bajaMotivo = document.getElementById("motivo")
let observacion = document.getElementById("bajaObservacion")
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

confirmBaja.addEventListener("click",()=>{
    darBaja().then(data =>{
        if(data.success){
            window.open(data.urlPDF, '_blank');
            window.location.href = data.urlUser 
        }
    })
    .catch(error => {
        console.log(error)
        if(!document.querySelector(".errorMessageSendBaja")){
            let errorMessage = document.createElement('p');
            errorMessage.className = 'errorMessageSendBaja';
            errorMessage.textContent = "Hubo un error inesperado con la confirmacion de la baja"
            formBaja.appendChild(errorMessage)
        }
    })
})

async function darBaja() {
    let postBaja = await fetch(urlBaja,{
        method: "POST",
        body:JSON.stringify({ 
            porcentage: inputPorcentage.value,
            c: inputEditPorcentage.name,
            motivo: bajaMotivo.value,
            observacion: observacion.value
        }),
        headers: {
            "X-CSRFToken": getCookie('csrftoken'),
            'Content-Type': 'application/json',
        }
    })
    let data = await postBaja.json()
    return data;
}