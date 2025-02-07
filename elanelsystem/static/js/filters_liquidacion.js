let contendorColaboradores = document.querySelector(".listColaboradoresWrapper > .valuesWrapper > .values ")
let contendorAdministradores = document.querySelector(".listAdmins > .valuesWrapper > .values ")
const wrapperManageLiquidacion = document.querySelector(".wrapperManageLiquidacion")
const radioFiltros = document.querySelectorAll('.inputSelectTipoColaborador');


let colaboradoresAFiltrar = "todos"
let body ={}

//Funcion para habilitar panel de comision
function habilitarPanelComision() {
    return inputCampania.value != "" && inputSucursal.value != ""
}


//#region Filtro sucursal - - - - - - - - - - - - 
let inputSucursal = document.getElementById("sucursalInput")
inputSucursal.addEventListener("input", async ()=>{
    
    if(habilitarPanelComision()){
        wrapperButtonsActions.classList.remove("blocked")
        wrapperManageLiquidacion.classList.add("active")

        body.sucursal = inputSucursal.value;
        body.campania = inputCampania.value;
        body.tipoColaborador = colaboradoresAFiltrar;
        
        let response = await fetchFunction(body,urlRequestColaboradores)
        console.log(response)   
        actualizarResultadosColaboradores(response["colaboradores_data"],contendorColaboradores)
        actualizarTotalComisionado(response["totalDeComisiones"])


    }else{
        wrapperButtonsActions.classList.add("blocked")
        wrapperManageLiquidacion.classList.remove("active")
        contendorColaboradores.innerHTML = ""
        totalComisionesTextColaboradores.textContent = "$ 0"
    }
})
//#endregion  - - - - - - - - - - - - - - - - - - - 


//#region Filtro campaña - - - - - - - - - - - - 
let inputCampania = document.getElementById("campaniaInput")
inputCampania.addEventListener("input", async ()=>{
    
    if(habilitarPanelComision()){
        wrapperButtonsActions.classList.remove("blocked")
        wrapperManageLiquidacion.classList.add("active")

        body.sucursal = inputSucursal.value;
        body.campania = inputCampania.value;
        body.tipoColaborador = colaboradoresAFiltrar;

        let response = await fetchFunction(body,urlRequestColaboradores)
        console.log(response)
        actualizarResultadosColaboradores(response["colaboradores_data"],contendorColaboradores)
        actualizarTotalComisionado(response["totalDeComisiones"])


    }
    else{
        wrapperButtonsActions.classList.add("blocked")
        wrapperManageLiquidacion.classList.remove("active")
        contendorColaboradores.innerHTML = ""
        totalComisionesTextColaboradores.textContent = "$ 0"
    }

})
//#endregion  - - - - - - - - - - - - - - - - - - - 


//#region  Filtros de radios - - - - - - - - - - - - - - - - -

radioFiltros.forEach(radio => {
    radio.addEventListener('change', async () => {
        colaboradoresAFiltrar = radio.value // Actuliza el valor de la variable global para posibles filtros
        body.sucursal = inputSucursal.value;
        body.campania = inputCampania.value;
        body.tipoColaborador = colaboradoresAFiltrar;

        let response = await fetchFunction(body, urlRequestColaboradores)
        console.log(response)
        actualizarResultadosColaboradores(response["colaboradores_data"],contendorColaboradores)
        actualizarTotalComisionado(response["totalDeComisiones"])
    });
})
//#endregion  - - - - - - - - - - - - - - - - - - - - - - - - - -


//#region Fetch data
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

async function fetchFunction(body, url) {
    try {
        let response = await fetch(url, {
            method: 'POST',
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
//#endregion - - - - - - - - - - - - - - -


//#region Funciones para actualizar panel de comisiones de colaboradores sin administradores

function actualizarResultadosColaboradores(resultados, contenedor) {
    console.log(resultados)
  // Limpia el contenedor de los datos
  contenedor.innerHTML = "";
  let itemsColaboradores = resultados.filter(item => !item.tipo_colaborador.includes("Administracion"))

  // Se reccore los datos filtrados
  itemsColaboradores.forEach((item) => {
    let divs ="";
    // Se reccore los campos de cada elemento y se lo guarda en un div
    divs += `<li>
        <div>
            <p>${item.nombre}</p>
        </div>
        <div>
            <p>$ ${item.comisionTotal}</p>
        </div>
    </li>`;
    
    contenedor.insertAdjacentHTML("beforeend",divs)
  });
}

function actualizarTotalComisionado(dinero){
    let totalComisionesTextColaboradores = document.querySelector("#totalComisionesTextColaboradores")
    totalComisionesTextColaboradores.textContent = "$ " + dinero
}


//#endregion  - - - - - - - - - - - - - - - - - - - - - - - - - -


// Funciones para actualizar lista de administradores

// function actualizarResultadosAdministradores(resultados, contenedor) {
//     // Limpia el contenedor de los datos
   
//     contenedor.innerHTML = "";
//     let itemsAdministrativos = resultados.filter(item => {
//         console.log(item)
//         // item.tipo_colaborador.includes("Admin")   
//     })
//     console.log(itemsAdministrativos)
//     // Se reccore los datos filtrados
//     itemsAdministrativos.forEach((item) => {
//       let divs ="";
//       // Se reccore los campos de cada elemento y se lo guarda en un div
//       divs += `<li>
//             <div>
//                 <p>${item.nombre}</p>
//             </div>
//             <div>
//                 <p>$</p>
//                 <input type="number" class="inputHaberesAdmin" id="input_haberesAdmin_${item.id}" name="comision_${item.id}" value=0 min=0>
//             </div>
//             <div>
//                 <p>$</p>
//                 <input type="number" class="inputHorariosAdmin" id="input_honorariosAdmin_${item.id}" name="premio_${item.pk}" value=0 min=0>
//             </div>
//         </li>`;
      
//       contenedor.insertAdjacentHTML("beforeend",divs)
//     });

//         // MANEJO DE LOS INPUTS DE ADMINISTRADORES
//     let inputsHaberesAdmin = document.querySelectorAll(".inputHaberesAdmin")
//     inputsHaberesAdmin.forEach(input => {
//         input.addEventListener("input",()=>{
//             let nextInput = input.parentElement.nextElementSibling.querySelector(".inputHorariosAdmin")
//             let sumaDeValores = parseFloat(input.value) + parseFloat(nextInput.value)
            
//             // Para actualizar el total
//             let total = parseFloat(totalAdminText.textContent)
//             total += sumaDeValores
//             totalAdminText.textContent = total

//             // if(input_comisionAdmin.value == "" || input_premioAdmin.value == ""){
//             //     totalAdminText.textContent = "$ 0"
//             // }
//         })
//     });


//     let inputsHonorariosAdmin = document.querySelectorAll(".inputHorariosAdmin")
//     inputsHonorariosAdmin.forEach(input => {
//         input.addEventListener("input",()=>{
//             let nextInput = input.parentElement.previousElementSibling.querySelector(".inputHaberesAdmin")
//             let sumaDeValores = parseFloat(input.value) + parseFloat(nextInput.value)
            
//             // Para actualizar el total
//             let total = parseFloat(totalAdminText.textContent)
//             total += sumaDeValores
//             totalAdminText.textContent = total


//         // if(input_premioAdmin.value == "" || input_comisionAdmin.value == ""){
//         //     totalAdminText.textContent = "$ 0"
//         // }
//         })
//     })
// }



