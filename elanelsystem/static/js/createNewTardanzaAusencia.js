let url = window.location.pathname
const buttonsAddItem = document.querySelectorAll(".buttonsAddItem > button")
let listTardanzasAusencias = document.querySelector(".listTardanzasAusencias")

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


async function createAusenciaTardanza(){
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                colaborador: colaborador.value,
                r: "WEpss",
                fecha: fecha.value,
                hora: hora.value,
                descuento: descuento.value,
            }),
        })
        if (!res.ok){
            throw new Error("Error")
        }
        const data = await res.json()
        return data;
    } catch (error) {
        console.log(error)
    }
}



function buttonSendItem(contenedor) {
    let buttonSendItem = document.getElementById("sendNewItem")
        buttonSendItem.addEventListener("click",async()=>{
            let data = await createAusenciaTardanza()
            let new_item = document.querySelector(".new_item")
            new_item.remove()
            newItemCreated(data,contenedor)
        })
}

function buttonCloseItem() {
    let buttonCloseSendItem = document.getElementById("closeSendNewItem")
        buttonCloseSendItem.addEventListener("click",()=>{
            let new_item = document.querySelector(".new_item")
            new_item.remove()
        })
}



function newItemCreated(data,contenedor) {
    let textTardanza = contenedor.offsetParent.previousElementSibling.querySelector(".textCountTardanzas")
    let textFalta = contenedor.offsetParent.previousElementSibling.querySelector(".textCountFaltas")
    textFalta.textContent = data.countFaltas
    textTardanza.textContent = data.countTardanzas

    let stringForHTML = `<li>
    <div><p>${data.fecha}</p></div>
    <div><p>${data.hora}</p></div>
    <div><p>$${data.descuento}</p></div>
    </li> `
    contenedor.insertAdjacentHTML('afterbegin', stringForHTML);
}



