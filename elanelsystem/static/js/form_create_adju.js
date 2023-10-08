const url = window.location.pathname;
const inputSelects = document.querySelectorAll(".select");
const menuProducto = document.querySelector('#wrapperProducto > ul')
// Para bloquer el input de producto
menuProducto.previousElementSibling.classList.add("desactive")


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



fetch(url,{
    method: 'get',
    headers: {'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' ,}
}).then(
    function(response){
        return response.json()
    }
).then(data =>{
    console.log(data)
    let objectsFiltered;
    inputSelects.forEach(element => {
        element.previousElementSibling.addEventListener('click', () => {
            clearActiveMenu()
            
            const height = element.scrollHeight
            element.style.height = height +'px'
            element.classList.add('active');

            let optionsMenu = element.querySelectorAll("li")
            optionsMenu.forEach(value => {
                value.addEventListener("click",()=>{
                    // Para colocar el valor en el input
                    let inputEvent = new Event('input')
                    element.previousElementSibling.innerHTML = value.innerHTML
                    element.previousElementSibling.value = value.innerHTML

                    // SI EL ELEMENTO ES EL INPUT DEL TIPO DE PRODUCTO que este filtre los productos segun el tipo
                    if(element.previousElementSibling.id =="id_tipo_producto"){
                        objectsFiltered = filterObjetsByType(data,element.previousElementSibling.value)
                        let items ="";
                        objectsFiltered.forEach(element => {
                            items += "<li>" + element["nombre"] + "</li>"
                        });
                        menuProducto.innerHTML = items
                        menuProducto.previousElementSibling.classList.remove("desactive")
                    }
                    element.previousElementSibling.dispatchEvent(inputEvent)
                    
                })
            });
        });
    })

    // PARA BUSCAR EL PRODUCTO
    menuProducto.previousElementSibling.addEventListener("input",()=>{
        objectsFiltered = filterObjetsByType(data[0],id_tipo_producto.value)
        let resultado = buscar(menuProducto.previousElementSibling.value,objectsFiltered)
        actualizarResultados(resultado,menuProducto)

        // para obtener el importe del producto y colocarlo
        let importe = objectsFiltered.filter((item) => item["nombre"] == menuProducto.previousElementSibling.value)
        

        if(importe.length > 0){
            inputImporte.value = importe[0]["importe"] +(importe[0]["importe"] * 0.1 )
            inputAnticipo.value = importe[0]["anticipo"]

            // Actuliza la primera cuota y suscripcion
            let itemForSuscripcionAndPrimerCuota = data[3].filter((item) => item["valor_nominal"] == inputImporte.value)
            inputCuotaSuscripcion.value = itemForSuscripcionAndPrimerCuota[0]["suscripcion"]
            inputPrimerCuota.value = itemForSuscripcionAndPrimerCuota[0]["cuota_1"]
        }else{
            inputImporte.value = ""
            inputAnticipo.value = ""
            // Limpia la primera cuota y suscripcion
            inputCuotaSuscripcion.value = ""
            // inputPrimerCuota.value = ""
        }
        // rellenarCamposDeVenta(data[1])
        let optionsLis = menuProducto.querySelectorAll("li")
        optionsLis.forEach(v =>{
            v.addEventListener('click',()=>{
                menuProducto.previousElementSibling.innerHTML = v.innerHTML
                menuProducto.previousElementSibling.value = v.innerHTML
                let inputEvent = new Event('input')
                menuProducto.previousElementSibling.dispatchEvent(inputEvent)
            })
        })
    })


    inputNroCuotas.addEventListener('input',()=>{
        rellenarCamposDeVenta(inputNroCuotas.value,inputTasaInteres.value)
    })
    inputTasaInteres.addEventListener('input',()=>{
        rellenarCamposDeVenta(inputNroCuotas.value,inputTasaInteres.value)
    })
    
})


function testClicks(event) {
    try {
        let menu = document.querySelector(".select.active")
        let input = menu.previousElementSibling
        let elementsLisClicked = Array.from(menu.children)
        if(event.target != menu && event.target != input && menu.classList.contains("active") && !elementsLisClicked.includes(event.target)){
            menu.classList.remove("active")
            menu.style.height = 0 +'px'
        }
    } catch (error) {
    }
    
}
function clearActiveMenu() {
    inputSelects.forEach(element => {
        element.classList.remove("active")
        element.style.height = 0 +'px'
    });
}
document.addEventListener("click",testClicks)


function filterObjetsByType(productsList,productType) {
    let objets = productsList.filter(object => object["tipo_de_producto"] == productType)
    return objets
}

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
function buscar(texto, datos){
    let listFilteredData = []
    let dataFormat = datos.filter((item) =>{
  
      // Accede a unicamente a los valores de cada elemento del JSON
        let valores = Object.values(item);
        // Los transforma al elemento en string para que sea mas facil filtrar por "include"
        let string = valores.join(",")
        // console.log(string)
        if(string.toLocaleLowerCase().includes(texto.toLocaleLowerCase())){
          listFilteredData.push(item)
        }
    })
    return listFilteredData;
}

function actualizarResultados(resultados,contenedor) {
    // Limpia el contenedor de los datos
    contenedor.innerHTML = "";
    
    // Se reccore los datos filtrados
    let lis ="";
    resultados.forEach((item) => {
        // console.log(item["nombre"])
        lis += "<li>"+item["nombre"]+"</li>";
  
    });
    contenedor.insertAdjacentHTML("beforeend",lis)
    let height = contenedor.scrollHeight
    contenedor.style.height = height +'px'
}


