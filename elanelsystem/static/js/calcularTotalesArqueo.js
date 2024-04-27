const inputsCantidad = document.querySelectorAll(".item > .itemCantidad > input")
let valoresTotalesXBillete = document.querySelectorAll(".item > .itemImporte > .importeValue")

let totalPlanillaText = document.getElementById("totalPlanillaEfectivo")
let diferenciaText = document.getElementById("diferenciaText")
let totalDiarioCaja = document.getElementById("saldoSegunCaja")

calcularDiferencia(totalPlanillaText.textContent,totalDiarioCaja.textContent)

saldoSegunCajaInput.value = totalDiarioCaja.textContent
inputsCantidad.forEach(input => {
    input.addEventListener("input",()=>{
        let billete = input.offsetParent.querySelector(".monedaValue").textContent
        let importe = input.offsetParent.querySelector(".importeValue")
        if(input.value == ""){
            importe.textContent = 0;
        }else{
            importe.textContent = (parseFloat(input.value) * billete).toFixed(0);
        }
        let sumaTotal = 0;
        valoresTotalesXBillete.forEach(element => {
            sumaTotal += parseFloat(element.textContent)
        });
        totalPlanillaText.textContent = sumaTotal.toFixed(0)
        totalPlanillaEfectivoInput.value = totalPlanillaText.textContent
        calcularDiferencia(totalPlanillaText.textContent,totalDiarioCaja.textContent)
    })
});

function calcularDiferencia(montoPlanilla,montoDiarioCaja) {
    diferenciaText.textContent = (parseFloat(montoPlanilla)) - (parseFloat(montoDiarioCaja)).toFixed(0)

    if(diferenciaText.textContent < 0){
        diferenciaText.style.color = "#ed1717" //Falta dinero
    }else if(diferenciaText.textContent > 0){
        diferenciaText.style.color = "#61e124" //Falta sobrante
    }else{
        diferenciaText.style.color = "#fff" // Dinero justo
    }
}

totalPlanillaText.addEventListener("input",()=>{
    let inputEvent = new Event('input')
    inputsCantidad[0].dispatchEvent(inputEvent)
})

