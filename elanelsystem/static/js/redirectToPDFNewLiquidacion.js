let confirmNewAuditoria = document.getElementById("liquidarButton");
let urlCreateAuditoria = window.location.pathname
// const form_create_user = document.getElementById("form_create_user")

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

async function fetchCRUD(body, url) {
    try {
        let response = await fetch(url, {
            method: "POST",
            body: JSON.stringify(body),
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
            }
        })
        if (!response.ok) {
            throw new Error("Error")
        }
        const data = await response.json();
        return data;
    } catch (error) {
    }
}


confirmNewAuditoria.addEventListener("click", async () => {
    body = {
        "campania":document.querySelector("#campaniaInput").value,
        "agencia":document.querySelector("#sucursalInput").value,
    }

    let response = await fetchCRUD(body, urlCreateAuditoria)
    console.log(response)
    // if (!response["success"]) {
    //     mostrarErrores(response["errors"], form_create_user)
    // } else {
    //     // Redireccionar a la página de PDF en una nueva pestaña y en la actual cambiar de url a la de la lista de usuarios
    //     window.open(response["urlPDF"], "_blank");
    //     window.location.href = response["urlRedirect"];
    // }

})
