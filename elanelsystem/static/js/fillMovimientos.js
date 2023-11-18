const buttonNext = document.getElementById("buttonNextMov")
const buttonBack = document.getElementById("buttonPreviousMov")
const cuotasPages = document.querySelector(".cuotasPages")
const containerMovimientos = document.querySelector(".values")
let cuotasButtons =  document.querySelectorAll(".mov")

const mainModal = document.querySelector(".main_modalCuota")
const closeModal = document.getElementById("closeModal")
url = window.location.pathname;

async function cuotasGet() {
    const response = await fetch("/request-cuotas/", {
        method: 'get',
        headers: {'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'},
        cache: 'no-store',
    });
    const data = await response.json();
    return data;
}
async function movsExternosGet() {
    const response = await fetch("/requestEgresoIngreso/", {
        method: 'get',
        headers: {'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'},
        cache: 'no-store',
    });
    const data = await response.json();
    return data;
}

async function main() {
    let data_cuotas = await cuotasGet()
    let data_movsExternos = await movsExternosGet()
    let dataTotal = data_cuotas.concat(data_movsExternos); // Combinar los arrays

    console.log(dataTotal)
    cuotasButtons.forEach(cuota => {
        cuota.addEventListener('click', ()=>{
            mainModal.classList.add("active")
            mainModal.style.opacity = "1"
            fillModalWithMovData(dataTotal,cuota)
        })
    });
}
main()

closeModal.addEventListener('click', ()=>{
    mainModal.style.opacity = "0"
    setTimeout(()=>{
        mainModal.classList.remove("active")

    },300)

})

function fillModalWithMovData(movimientos,mov) {
    console.log(movimientos)
    let movSelected = movimientos.filter(c=> c.idMov == mov.id)
    if("concepto" in movSelected[0]){
        console.log(movSelected)
        numeroVenta.innerHTML = ""
        numeroCliente.innerHTML = ""
        numeroCuota.innerHTML = ""
        dinero.innerHTML = ""
        metodoPago.innerHTML = ""
        cobrador.innerHTML = ""
        fechaPago.innerHTML = ""
        horaPago.innerHTML = ""
        sucursal.innerHTML = ""
    }else{
        numeroVenta.innerHTML = movSelected[0]["nro_operacion"]
        numeroCliente.innerHTML = movSelected[0]["nroCliente"]
        numeroCuota.innerHTML = movSelected[0]["cuota"]
        dinero.innerHTML = movSelected[0]["pagado"]
        metodoPago.innerHTML = movSelected[0]["metodoPago"]
        cobrador.innerHTML = movSelected[0]["cobrador"]
        fechaPago.innerHTML = movSelected[0]["fecha_pago"]
        horaPago.innerHTML = movSelected[0]["hora"]
        sucursal.innerHTML = movSelected[0]["sucursal"]
        
    }
    
}




