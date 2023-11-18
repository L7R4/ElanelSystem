const inputsCantidad = document.querySelectorAll(".item > .itemCantidad > input")
let valoresTotalesXBillete = document.querySelectorAll(".item > .itemImporte > .importeValue")

let totalEfectivoText = document.getElementById("totalEfectivoText")
let totalPlanillaText = document.getElementById("totalPlanillaText")
let diferenciaText = document.getElementById("diferenciaText")
let totalSegunDiarioCaja = document.getElementById("totalSegunDiarioCaja")

inputsCantidad.forEach(input => {
    input.addEventListener("input",()=>{
        let billete = input.offsetParent.querySelector(".monedaValue").textContent
        let importe = input.offsetParent.querySelector(".importeValue")
        if(input.value == ""){
            importe.textContent = 0;
        }else{
            importe.textContent = (parseFloat(input.value) * billete).toFixed(1);
        }
        let sumaTotal = 0;
        valoresTotalesXBillete.forEach(element => {
            sumaTotal += parseFloat(element.textContent)
        });
        totalEfectivoText.textContent = sumaTotal.toFixed(1)
        totalPlanillaText.textContent = totalEfectivoText.textContent
        if(totalSegunDiarioCaja.value == ""){
            diferenciaText.textContent = 0    
        }else{
            diferenciaText.textContent = (parseFloat(totalPlanillaText.textContent) - parseFloat(totalSegunDiarioCaja.value)).toFixed(1)
            if(parseFloat(diferenciaText.textContent) < 0){
                diferenciaText.style.color = "#ed1717"
            }else{
                diferenciaText.style.color = "#fff"
            }
        }
    })
});

totalSegunDiarioCaja.addEventListener("input",()=>{
    let inputEvent = new Event('input')
    inputsCantidad[0].dispatchEvent(inputEvent)
})

