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
    }
}


confirmNewUser.addEventListener("click",async()=>{
    body = {}
    let inputs = form_create_user.querySelectorAll("input")
    let textareas = form_create_user.querySelectorAll("textarea")
    
    inputs = [...inputs,...textareas]

    inputs.forEach(element => {
        body[element.name] = element.value
    });
    
    let response = await fetchCRUD(body,urlCreateUser)
    if(!response["success"]){
        console.log(response["errors"])
        mostrarErrores(response["errors"],form_create_user)
    }

})



