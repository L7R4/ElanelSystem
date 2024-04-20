let confirmNewUser = document.getElementById("saveButton");
let urlCreateUser = window.location.pathname
const formCreateUser = document.getElementById("form_create_user")

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

confirmNewUser.addEventListener("click",()=>{
    newUser().then(data =>{
        if(data.success){
            window.open(data.urlPDF, '_blank');
            window.location.href = data.urlRedirect 
        }
    })
    .catch(error => {})
})

async function newUser() {
    let postNewUser = await fetch(urlCreateUser,{
        method: "POST",
        body: new FormData(formCreateUser),

        headers: {
            "X-CSRFToken": getCookie('csrftoken'),
        }
    })
    let data = await postNewUser.json()
    return data;
}