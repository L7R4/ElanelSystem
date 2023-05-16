const url = window.location.pathname;

const inputNroCliente = document.getElementById('id_nro_cliente');
const inputNombreCompleto = document.getElementById('nombre_completo');
const inputPaquete = document.getElementById('paquete')
const inputTipoProducto = document.getElementById('tipo_producto')
const inputProducto = document.getElementById('producto')
const inputImporte = document.getElementById('importe')
const inputTasaInteres = document.getElementById('tasa_interes')
const inputInteresesGenerados = document.getElementById('intereses_generados')
const inputImportexCuota = document.getElementById('importe_x_cuota')
const inputTotalAPagar = document.getElementById('total_a_pagar')
const inputNroCuotas = document.getElementById('nro_cuotas')
const inputSelects = document.querySelectorAll(".select_input");
const inputFecha = document.getElementById("fecha")

let fechaActual = new Date();

let anio = fechaActual.getFullYear();
let mes = fechaActual.getMonth() + 1;
let dia = fechaActual.getDate();

let fechaFormateada = dia + '/' + mes + '/' + anio;

inputFecha.value =fechaFormateada


fetch(url,{
    method: 'get',
    headers: {'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' ,}
}).then(
    function(response){
        return response.json()
    }
).then(data =>{
    console.log(data)
    inputSelects.forEach(input =>{
        input.addEventListener("input", () => {
            const texto = input.value;
            let datos = []
            if (input.classList.contains("select_input_products")) {
                datos = data[1];
            }else if(input.classList.contains("select_input_users")){
                datos = data[0];
            }else if(input.classList.contains("select_input_clientes")){
                datos = data[3];
            }
            const resultados = buscar(texto, datos);
            const contenedorResultados = input.parentElement.children[2]
            actualizarResultados(resultados,contenedorResultados);
            activeSelect(input.nextElementSibling)
        })
    });

    // INPUT DE NOMBRE COMPLETO
    inputNroCliente.addEventListener('input', ()=>{
        // const nroCliente = ;
        // Buscar el usuario en los datos del JSON
        const usuario = data[0].find(u => u.nro_cliente === inputNroCliente.value);
        if (usuario) {
        // Si se encuentra el usuario, actualizar los campos del formulario
          inputNombreCompleto.value = usuario.nombre;
        } else {
          // Si no se encuentra el usuario, dejar los campos vacíos
          inputNombreCompleto.value = ""
        }
    });


    // INPUT DE NOMBRE COMPLETO
    inputNombreCompleto.addEventListener('input', ()=>{
        // const nombre = ;
    
        // Buscar el usuario en los datos del JSON
        const usuario = data[0].find(u => u.nombre === inputNombreCompleto.value);
        if (usuario) {
        // Si se encuentra el usuario, actualizar los campos del formulario
            inputNroCliente.value = usuario.nro_cliente;
        } else {
          // Si no se encuentra el usuario, dejar los campos vacíos
            inputNroCliente.value =""
        }
    });


    // INPUT DE PRODUCTO
    inputProducto.addEventListener('input', ()=>{
        const producto = data[1].find(u => u.nombre === inputProducto.value);
        if (producto) {
        // Si se encuentra el usuario, actualizar los campos del formulario
            inputImporte.value = producto.importe;
            inputPaquete.value = producto.paquete;
            inputTipoProducto.value = producto.tipo_de_producto;
            
            if(inputTotalAPagar.value != 0){
                inputImportexCuota.value = parseInt(inputTotalAPagar.value) / parseInt(inputNroCuotas.value)
            }

            const interes = data[2].find(u => u.valor_nominal === parseInt(inputImporte.value) && u.cuota === parseInt(inputNroCuotas.value));
            if(interes){
                inputTasaInteres.value = interes.porcentage
            }else {
                inputTasaInteres.value = 0
            }
            if (inputTasaInteres.value != 0){
                inputInteresesGenerados.value = ((inputImporte.value * inputTasaInteres.value) /100).toFixed(2)
                inputTotalAPagar.value = (parseInt(inputInteresesGenerados.value) + parseInt(inputImporte.value)).toFixed(2)  
                inputImportexCuota.value = (parseInt(inputTotalAPagar.value) / parseInt(inputNroCuotas.value)).toFixed(2)
            }

        } else {
          // Si no se encuentra el usuario, dejar los campos vacíos
          inputImporte.value = 0;
          inputPaquete.value = "";
          inputTipoProducto.value = "";
          inputInteresesGenerados.value = 0
          inputImportexCuota.value = 0
          inputTotalAPagar.value = 0
          inputTasaInteres.value = 0
        }
    })


    inputImporte.addEventListener('input', ()=>{
        inputInteresesGenerados.value =((inputImporte.value * inputTasaInteres.value) /100).toFixed(2)
        if(inputTotalAPagar.value != 0){
            inputImportexCuota.value = (parseInt(inputTotalAPagar.value) / parseInt(inputNroCuotas.value)).toFixed(2)
        }else if(inputTotalAPagar.value == 0 || inputTotalAPagar.value == ""){
            inputImportexCuota.value = 0
        }
        if (inputImporte.value == 0 || inputImporte == ""){
            inputInteresesGenerados.value = 0
            inputTasaInteres.value = 0
        }
        if(inputNroCuotas != "" && inputImporte != 0){
            const interes = data[2].find(u => u.valor_nominal === parseInt(inputImporte.value) && u.cuota === parseInt(inputNroCuotas.value));
            if(interes){
                inputTasaInteres.value = interes.porcentage
                inputTotalAPagar.value = (parseInt(inputInteresesGenerados.value) + parseInt(inputImporte.value))   
                inputImportexCuota.value = (parseInt(inputTotalAPagar.value) / parseInt(inputNroCuotas.value)).toFixed(2) 
            }else {
                inputTasaInteres.value = 0
            }
        }
    })
    
    
    // INPUT DE TASA DE INTERES
    inputTasaInteres.addEventListener('input', ()=>{
        inputInteresesGenerados.value = ((inputImporte.value * inputTasaInteres.value) /100).toFixed(2)
        if (inputInteresesGenerados.value != 0){
            inputTotalAPagar.value = (parseInt(inputInteresesGenerados.value) + parseInt(inputImporte.value)).toFixed(2) 
            inputImportexCuota.value = (parseInt(inputTotalAPagar.value) / parseInt(inputNroCuotas.value)).toFixed(2)
        }else if(inputInteresesGenerados.value == 0 || inputInteresesGenerados.value == ""){
            inputTotalAPagar.value = 0
            inputImportexCuota.value = 0
        }
        

    })


    // INPUT DE IMPORTE
    inputImporte.addEventListener('input', ()=>{
        inputInteresesGenerados.value =((inputImporte.value * inputTasaInteres.value) /100).toFixed(2)
        if(inputTotalAPagar.value != 0){
            inputImportexCuota.value = (parseInt(inputTotalAPagar.value) / parseInt(inputNroCuotas.value)).toFixed(2)
        }else if(inputTotalAPagar.value == 0 || inputTotalAPagar.value == ""){
            inputImportexCuota.value = 0
        }
        if (inputImporte.value == 0 || inputImporte == ""){
            inputInteresesGenerados.value = 0
        }
        if(inputTasaInteres.value == 0 || inputTasaInteres == ""){
            inputTotalAPagar.value = 0
            inputImportexCuota.value = 0
        }
    })


    // INPUT DE NUMERO DE CUOTAS
    inputNroCuotas.addEventListener('input', () =>{
        inputImportexCuota.value = (parseInt(inputTotalAPagar.value) / parseInt(inputNroCuotas.value)).toFixed(2)
        if(inputNroCuotas.value == 0 || inputNroCuotas.value == ""){
            inputImportexCuota.value = 0
            inputTasaInteres.value = 0
        }
        if(inputNroCuotas != "" && inputImporte != 0){
            const interes = data[2].find(u => u.valor_nominal === parseInt(inputImporte.value) && u.cuota === parseInt(inputNroCuotas.value));
            if(interes){
                inputTasaInteres.value = interes.porcentage
                inputInteresesGenerados.value = ((inputImporte.value * inputTasaInteres.value) /100).toFixed(2)
                inputTotalAPagar.value = (parseInt(inputInteresesGenerados.value) + parseInt(inputImporte.value)).toFixed(2) 
                inputImportexCuota.value = (parseInt(inputTotalAPagar.value) / parseInt(inputNroCuotas.value)).toFixed(2)
            }else {
                inputTasaInteres.value = 0
                inputInteresesGenerados.value = 0
                inputTotalAPagar.value = 0
                inputImportexCuota.value = 0
            }
        }
    })

    // INPUT DE TIPO DE PRODUCTO
    inputTipoProducto.addEventListener('input', () => {
        // Aquí irá el código para actualizar la lista de opciones de "Nombre del producto"
        actProducts(data[1],inputTipoProducto.value)
        if(inputTipoProducto.value != ""){
            inputPaquete.value = ""
            inputImporte.value = 0
            inputProducto.value = ""
            inputTotalAPagar.value = 0
            inputInteresesGenerados.value = 0
            inputImportexCuota.value = 0
            inputTasaInteres.value = 0


            inputProducto.removeAttribute("readonly")
            inputProducto.parentElement.style.pointerEvents = "all"
        }
    });

});
function actProducts(products,type_value) {
    // Guarda el valor del select
    const valor = type_value

    // Limpia la lista de productos
    const containerProducts = inputProducto.parentElement.children[2]
    containerProducts.innerHTML = ""

    // Busca los elementos segun el tipo
    let products_list = products.filter(p => {
        return p.tipo_de_producto === valor
    })

    products_list.forEach(i =>{
        const option = document.createElement('li');
        option.textContent = i.nombre
        containerProducts.appendChild(option)
    })

}


function buscar(texto, datos) {
    return datos.filter((item) => {
      const valores = Object.values(item);
      return valores.some((valor) => {
        if (typeof valor === "string") {
          return valor.toLowerCase().includes(texto.toLowerCase());
        }
        return false;
      });
    });
}

function actualizarResultados(resultados, contenedor) {
  contenedor.innerHTML = "";
  resultados.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item.nombre;
    contenedor.appendChild(li);
  });
  let contenedorChildrens = contenedor.children
  selectDataInSelectInput(contenedorChildrens)
}

function selectDataInSelectInput(lista){
      Array.from(lista).forEach(item =>{
          item.addEventListener("click", ()=>{
              console.log("entra")
              let text_value = item.textContent
              let inputRefered = item.parentElement.parentElement.children[0]
              inputRefered.value = text_value
          })
      })
}




