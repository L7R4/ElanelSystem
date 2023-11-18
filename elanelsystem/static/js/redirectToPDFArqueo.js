let confirmArqueoCaja = document.getElementById("confirmArqueoCaja");
let urlArqueo = window.location.pathname
let p050 = document.getElementById("p0.5")
let p025 = document.getElementById("p0.25")
let p010 = document.getElementById("p0.5")
let p005 = document.getElementById("p0.5")

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
        body:JSON.stringify({ 
            "responsable": responsable.value,
            "totalEfectivo": totalEfectivo.value,
            "totalPlanilla": totalPlanilla.value,
            "totalSegunDiarioCaja": totalSegunDiarioCaja.value,
            "diferencia": diferencia.value,
            "observaciones": observaciones.value,
            "p1000": p1000.value,
            "p500": p500.value,
            "p200": p200.value,
            "p100": p100.value,
            "p50": p50.value,
            "p20": p20.value,
            "p10": p10.value,
            "p5": p5.value,
            "p2": p2.value,
            "p1": p1.value,
            "p0.5": p050.value,
            "p0.25": p025.value,
            "p0.1": p010.value,
            "p0.05": p005.value,
        }),

        headers: {
            "X-CSRFToken": getCookie('csrftoken'),
            'Content-Type': 'application/json',
        }
    })
    let data = await postArqueo.json()
    return data;
}