let confirmNewUser = document.getElementById("saveButton");
let urlCreateUser = window.location.pathname
const form_create_user = document.getElementById("form_create_user")

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
        console.error("Error en fetchCRUD:", error); // Agregar este log
    }
}


confirmNewUser.addEventListener("click",async()=>{
    let body = {
        nombre: form_create_user.nombre.value,
        dni: form_create_user.dni.value,
        tel: form_create_user.tel.value,
        fec_nacimiento: form_create_user.fec_nacimiento.value,
        domic: form_create_user.domic.value,
        prov: form_create_user.prov.value,
        loc: form_create_user.loc.value,
        cp: form_create_user.cp.value,
        lugar_nacimiento: form_create_user.lugar_nacimiento.value,
        estado_civil: form_create_user.estado_civil.value,
        xp_laboral: form_create_user.xp_laboral.value,
        sucursal: form_create_user.sucursal.value,
        rango: form_create_user.rango.value,
        fec_ingreso: form_create_user.fec_ingreso.value,
        email: form_create_user.email.value,
        password: form_create_user.password.value
    }

    let response = await fetchCRUD(body,urlCreateUser)
    if(!response["success"]){
        mostrarErrores(response["errors"],form_create_user)
    }

})



