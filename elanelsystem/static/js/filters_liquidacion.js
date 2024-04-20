let query = ""
let contendorColaboradores = document.querySelector(".listColaboradoresWrapper > .valuesWrapper > .values ")
let contendorAdministradores = document.querySelector(".listAdmins > .valuesWrapper > .values ")
// Funcion para cleanear el query segun su estado
function cleanQuery(queryString, tipoFiltro, valor) {
    const params = new URLSearchParams(queryString);

    if (params.has(tipoFiltro)) {
        // Si el parámetro ya existe, lo eliminamos antes de agregar el nuevo valor
        params.delete(tipoFiltro);
    }

    // Agregamos el nuevo valor al parámetro
    params.append(tipoFiltro, valor);

    // Devolvemos la cadena de consulta
    return params.toString();
}


// Filtro sucursal - - - - - - - - - - - - 
let inputSucursal = document.getElementById("sucursalInput")
inputSucursal.addEventListener("input", async ()=>{
    // Para habilitar la liquidacion
    backgroundLiquidacion.style.display = "none"
    wrapperButtonsActions.classList.remove("blocked")
    // ----------------
    query = cleanQuery(query, "sucursal", inputSucursal.value);
    let data = await fetchColaboradores(query);

    actualizarResultadosColaboradores(data["colaboradores"],contendorColaboradores);
    totalComisionesTextColaboradores.textContent = "$ "+ data["totalDeComisiones"]

    actualizarResultadosAdministradores(data["colaboradores"],contendorAdministradores)
})
//  - - - - - - - - - - - - - - - - - - - 


// Filtro campaña - - - - - - - - - - - - 
// let inputCampania = document.getElementById("inputCampania")
// inputCampania.addEventListener("input", async ()=>{
//     query = cleanQuery(query, "campania", inputCampania.value);
//     console.log(query);
//     await fetchColaboradores(query);
// })
//  - - - - - - - - - - - - - - - - - - - 


// Filtros de radios - - - - - - - - - - - - - - - - -
const radioFiltros = document.querySelectorAll('.inputSelectTipoColaborador');

radioFiltros.forEach(radio => {
    radio.addEventListener('change', async () => {
        const tipoFiltro = radio.name;
        const valor = radio.value;
        query = cleanQuery(query, tipoFiltro, valor);
        let data = await fetchColaboradores(query);
        
        actualizarResultadosColaboradores(data["colaboradores"],contendorColaboradores);
        totalComisionesTextColaboradores.textContent = "$ "+ data["totalDeComisiones"]
    });
});
//  - - - - - - - - - - - - - - - - - - - - - - - - - -




// PETICION FETCH PARA FILTRAR COLABORADORES
async function fetchColaboradores(query){
    try {
        const res = await fetch(urlRequestColaboradores+query, {
            method: 'GET',
            headers: {'X-Requested-With': 'XMLHttpRequest', 
                      'Content-Type': 'application/json'},
            cache: 'no-store',
        })
        if (!res.ok){
            throw new Error("Error")
        }
        const data = await res.json()
        console.log(data)
        return data;
    } catch (error) {}
}

// Funciones para actualizar lista de colaboradores

function actualizarResultadosColaboradores(resultados, contenedor) {
  // Limpia el contenedor de los datos
  contenedor.innerHTML = "";
  let itemsColaboradores = resultados.filter(item => !item.tipo_colaborador.includes("Administracion"))

  // Se reccore los datos filtrados
  itemsColaboradores.forEach((item) => {
    let divs ="";
    // Se reccore los campos de cada elemento y se lo guarda en un div
    divs += `<li><div><p>${item.nombre}</p></div><div><p>$ ${item.comisionTotal}</p></div></li>`;
    
    contenedor.insertAdjacentHTML("beforeend",divs)
  });
}

function buscar(texto, datos){
  let listFilteredData = []
  let dataFormat = datos.filter((item) =>{

    // Accede a unicamente a los valores de cada elemento del JSON
      let valores = Object.values(item);

      // Los transforma al elemento en string para que sea mas facil filtrar por "include"
      let string = valores.join(",")
      
      if(string.toLocaleLowerCase().includes(texto.toLocaleLowerCase())){
        listFilteredData.push(valores)
      }
  })
  return listFilteredData;
}
//  - - - - - - - - - - - - - - - - - - - - - - - - - -


// Funciones para actualizar lista de colaboradores

function actualizarResultadosAdministradores(resultados, contenedor) {
    // Limpia el contenedor de los datos
   
    contenedor.innerHTML = "";
    let itemsAdministrativos = resultados.filter(item => {
        console.log(item)
        // item.tipo_colaborador.includes("Admin")   
    })
    console.log(itemsAdministrativos)
    // Se reccore los datos filtrados
    itemsAdministrativos.forEach((item) => {
      let divs ="";
      // Se reccore los campos de cada elemento y se lo guarda en un div
      divs += `<li><div><p>${item.nombre}</p></div><div><p>$</p><input type="number" class="inputHaberesAdmin" id="input_haberesAdmin_${item.id}" name="comision_${item.id}" value=0 min=0></div><div><p>$</p><input type="number" class="inputHorariosAdmin" id="input_honorariosAdmin_${item.id}" name="premio_${item.pk}" value=0 min=0></div></li>`;
      
      contenedor.insertAdjacentHTML("beforeend",divs)
    });

        // MANEJO DE LOS INPUTS DE ADMINISTRADORES
    let inputsHaberesAdmin = document.querySelectorAll(".inputHaberesAdmin")
    inputsHaberesAdmin.forEach(input => {
        input.addEventListener("input",()=>{
            let nextInput = input.parentElement.nextElementSibling.querySelector(".inputHorariosAdmin")
            let sumaDeValores = parseFloat(input.value) + parseFloat(nextInput.value)
            
            // Para actualizar el total
            let total = parseFloat(totalAdminText.textContent)
            total += sumaDeValores
            totalAdminText.textContent = total

            // if(input_comisionAdmin.value == "" || input_premioAdmin.value == ""){
            //     totalAdminText.textContent = "$ 0"
            // }
        })
    });


    let inputsHonorariosAdmin = document.querySelectorAll(".inputHorariosAdmin")
    inputsHonorariosAdmin.forEach(input => {
        input.addEventListener("input",()=>{
            let nextInput = input.parentElement.previousElementSibling.querySelector(".inputHaberesAdmin")
            let sumaDeValores = parseFloat(input.value) + parseFloat(nextInput.value)
            
            // Para actualizar el total
            let total = parseFloat(totalAdminText.textContent)
            total += sumaDeValores
            totalAdminText.textContent = total


        // if(input_premioAdmin.value == "" || input_comisionAdmin.value == ""){
        //     totalAdminText.textContent = "$ 0"
        // }
        })
    })
}



