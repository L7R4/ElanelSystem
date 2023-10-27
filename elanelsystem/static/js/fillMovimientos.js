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

async function main() {
    let data = await cuotasGet()

    cuotasButtons.forEach(cuota => {
        cuota.addEventListener('click', ()=>{
            mainModal.classList.add("active")
            mainModal.style.opacity = "1"
            fillModalWithMovData(data,cuota)
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
    let movSelected = movimientos.filter(c=> c.idMov == mov.id)
    numeroVenta.innerHTML = movSelected[0]["nro_operacion"]
    numeroCliente.innerHTML = movSelected[0]["nroCliente"]
    numeroCuota.innerHTML = movSelected[0]["cuota"]
    dinero.innerHTML = movSelected[0]["pagado"]
    metodoPago.innerHTML = movSelected[0]["metodoPago"]
    cobrador.innerHTML = movSelected[0]["cobrador"]
    fechaPago.innerHTML = movSelected[0]["fecha_pago"]
    horaPago.innerHTML = movSelected[0]["hora"]
    
}




