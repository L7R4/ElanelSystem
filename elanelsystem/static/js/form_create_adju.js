// const url = window.location.pathname;
const inputSelects = document.querySelectorAll(".select");
const listProducto = document.querySelector('#wrapperProducto ul')
const inputTipoDeProducto = document.querySelector('#tipoProductoInput')
const inputProducto = document.querySelector('#productoInput')
// Para bloquer el input de producto
// listProducto.previousElementSibling.classList.add("desactive")


const menuTipoProducto = document.querySelector('#wrapperTipoProducto > ul')

const inputImporte = document.getElementById('id_importe')
const inputCuotaSuscripcion = document.getElementById('id_anticipo')
const inputPrimerCuota = document.getElementById('id_primer_cuota')
const inputNroCuotas = document.getElementById('id_nro_cuotas')
const inputTasaInteres = document.getElementById('id_tasa_interes')
const inputInteresesGenerados = document.getElementById('id_intereses_generados')
const inputImportexCuota = document.getElementById('id_importe_x_cuota')
const inputTotalAPagar = document.getElementById('id_total_a_pagar')
const inputPaquete = document.getElementById('id_paquete')
const inputAnticipo = document.getElementById('id_anticipo')

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
        let response = await fetch(url,{
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

let productoHandled; // Variable para guardar el producto seleccionado
let productos; // Variable para guardar los productos

async function requestProductos(){
    
    let body = {
        // "sucursal": sucursalInput.value,
        "tipoProducto": inputTipoDeProducto ? inputTipoDeProducto.value : null
    }
    
    let data = await fetchFunction(body,urlRequestProductos);
    
    return data["productos"];
}

// Cuando se selecciona un tipo de producto se filtran los productos
inputTipoDeProducto.addEventListener("input", async ()=>{
    productos = await requestProductos();
    
    listProducto.innerHTML = "" // Limpia la lista de productos
    listProducto.previousElementSibling.value ="" // Limpia el input de producto en caso de que se haya seleccionado un producto
    if(productos.length != 0){

        inputProducto.parentElement.parentElement.classList.remove("desactive") // Desbloquea el input de producto
        console.log(inputProducto.offsetParent)
        productos.forEach(product => {
            createProductoHTMLElement(listProducto, product["nombre"]);
        });
        updateListOptions(listProducto, inputProducto); // Actualiza los listeners de la lista de productos
    }else{
        inputProducto.parentElement.parentElement.classList.add("desactive") // Bloquea el input de producto
    }
    
});


// Cuando se selecciona un producto se guarda en la variable productoHandled
inputProducto.addEventListener("input", async ()=>{
    productoHandled = productos.filter((item) => item["nombre"] == inputProducto.value)[0];
});



// fetch(url,{
//     method: 'get',
//     headers: {'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'},
//     cache: 'no-store'    
// }).then(
//     function(response){
//         return response.json()
//     }
// ).then(data =>{
//     console.log(data)
//     let objectsFiltered;
//     inputSelects.forEach(element => {
//         element.previousElementSibling.addEventListener('click', () => {
//             clearActiveMenu()
            
//             const height = element.scrollHeight
//             element.style.height = height +'px'
//             element.classList.add('active');

//             let optionsMenu = element.querySelectorAll("li")
//             optionsMenu.forEach(value => {
//                 value.addEventListener("click",()=>{
//                     // Para colocar el valor en el input
//                     let inputEvent = new Event('input')
//                     element.previousElementSibling.innerHTML = value.innerHTML
//                     element.previousElementSibling.value = value.innerHTML

//                     // SI EL ELEMENTO ES EL INPUT DEL TIPO DE PRODUCTO que este filtre los productos segun el tipo
//                     if(element.previousElementSibling.id =="id_tipo_producto"){
//                         objectsFiltered = filterObjetsByType(data,element.previousElementSibling.value)
//                         let items ="";
//                         objectsFiltered.forEach(element => {
//                             items += "<li>" + element["nombre"] + "</li>"
//                         });
//                         listProducto.innerHTML = items
//                         listProducto.previousElementSibling.classList.remove("desactive")
//                     }
//                     element.previousElementSibling.dispatchEvent(inputEvent)
                    
//                 })
//             });
//         });
//     })

//     // PARA BUSCAR EL PRODUCTO
//     listProducto.previousElementSibling.addEventListener("input",()=>{
//         objectsFiltered = filterObjetsByType(data[0],id_tipo_producto.value)
//         let resultado = buscar(listProducto.previousElementSibling.value,objectsFiltered)
//         actualizarResultados(resultado,listProducto)

//         // para obtener el importe del producto y colocarlo
//         let importe = objectsFiltered.filter((item) => item["nombre"] == listProducto.previousElementSibling.value)
        

//         if(importe.length > 0){
//             inputImporte.value = importe[0]["importe"] +(importe[0]["importe"] * 0.1 )
//             inputAnticipo.value = importe[0]["anticipo"]

//             // Actuliza la primera cuota y suscripcion
//             let itemForSuscripcionAndPrimerCuota = data[3].filter((item) => item["valor_nominal"] == inputImporte.value)
//             inputCuotaSuscripcion.value = itemForSuscripcionAndPrimerCuota[0]["suscripcion"]
//             inputPrimerCuota.value = itemForSuscripcionAndPrimerCuota[0]["cuota_1"]
//         }else{
//             inputImporte.value = ""
//             inputAnticipo.value = ""
//             // Limpia la primera cuota y suscripcion
//             inputCuotaSuscripcion.value = ""
//             // inputPrimerCuota.value = ""
//         }
//         // rellenarCamposDeVenta(data[1])
//         let optionsLis = listProducto.querySelectorAll("li")
//         optionsLis.forEach(v =>{
//             v.addEventListener('click',()=>{
//                 listProducto.previousElementSibling.innerHTML = v.innerHTML
//                 listProducto.previousElementSibling.value = v.innerHTML
//                 let inputEvent = new Event('input')
//                 listProducto.previousElementSibling.dispatchEvent(inputEvent)
//             })
//         })
//     })


//     inputNroCuotas.addEventListener('input',()=>{
//         rellenarCamposDeVenta(inputNroCuotas.value,inputTasaInteres.value)
//     })
//     inputTasaInteres.addEventListener('input',()=>{
//         rellenarCamposDeVenta(inputNroCuotas.value,inputTasaInteres.value)
//     })
    
// })




function rellenarCamposDeVenta(valueNroCuotas, valueInteres){
    if(valueNroCuotas != "" && valueInteres != ""){
        console.log(valueInteres)
            inputInteresesGenerados.value = parseInt((valueInteres * inputImporte.value)/100)
            inputImportexCuota.value = parseInt((inputImporte.value/valueNroCuotas)+(inputInteresesGenerados.value/valueNroCuotas))
            inputTotalAPagar.value = parseInt(inputImporte.value) + parseInt(inputInteresesGenerados.value) - inputAnticipo.value
    }
    else{
        inputInteresesGenerados.value = ""
        inputImportexCuota.value = ""
        inputTotalAPagar.value =""
    }
}


// PARA FILTRAR DATOS MEDIANTE INPUTS
// function buscar(texto, datos){
//     let listFilteredData = []
//     let dataFormat = datos.filter((item) =>{
  
//       // Accede a unicamente a los valores de cada elemento del JSON
//         let valores = Object.values(item);
//         // Los transforma al elemento en string para que sea mas facil filtrar por "include"
//         let string = valores.join(",")
//         // console.log(string)
//         if(string.toLocaleLowerCase().includes(texto.toLocaleLowerCase())){
//           listFilteredData.push(item)
//         }
//     })
//     return listFilteredData;
// }

// function actualizarResultados(resultados,contenedor) {
//     // Limpia el contenedor de los datos
//     contenedor.innerHTML = "";
    
//     // Se reccore los datos filtrados
//     let lis ="";
//     resultados.forEach((item) => {
//         // console.log(item["nombre"])
//         lis += "<li>"+item["nombre"]+"</li>";
  
//     });
//     contenedor.insertAdjacentHTML("beforeend",lis)
//     let height = contenedor.scrollHeight
//     contenedor.style.height = height +'px'
// }


// Esto evita el comportamiento predeterminado del boton "Enter"
document.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
      e.preventDefault();
    }
  });


// Crear un elemento li para el producto
function createProductoHTMLElement(contenedor, producto) {
    let stringForHTML = "";

    stringForHTML = `<li data-value="${producto}">${producto}</li>`;
    contenedor.insertAdjacentHTML('afterbegin', stringForHTML);
}
