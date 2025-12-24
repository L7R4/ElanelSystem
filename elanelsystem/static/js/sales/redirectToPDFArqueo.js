let confirmArqueoCaja = document.getElementById("confirmArqueoCaja");
let urlArqueo = window.location.pathname
const formArqueoCaja = document.getElementById("formArqueoCaja")

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

confirmArqueoCaja.addEventListener("click",()=>{
    makeArqueo().then(data =>{
        if(data.success){
            window.open(data.urlPDF, '_blank');
            window.location.href = data.urlCaja 
        }
    })
    .catch(error => {
        console.log(error)
    })
})

async function makeArqueo() {
    let postArqueo = await fetch(urlArqueo,{
        method: "POST",
        body: new FormData(formArqueoCaja),

        headers: {
            "X-CSRFToken": getCookie('csrftoken'),
        }
    })
    let data = await postArqueo.json()
    return data;
}