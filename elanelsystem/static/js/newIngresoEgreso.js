


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
buttonsNewMov.forEach(element => {
    element.addEventListener("click",()=>{
        makeArqueo().then(data =>{
            console.log(data)
        })
        .catch(error => {
            console.log(error)
        })
    })
});


async function makeArqueo() {
    let postArqueo = await fetch(urlArqueo,{
        method: "POST",
        body:JSON.stringify({ 
            "responsable": "tuki",
        }),

        headers: {
            "X-CSRFToken": getCookie('csrftoken'),
            'Content-Type': 'application/json',
        }
    })
    let data = await postArqueo.json()
    return data;
}