let itemsCobradoresWrapper = document.querySelector(".selectCobrador > .options")
let selectCobradorInput = document.getElementById("cobradorInput")
var url = window.location.pathname;


fetch(url,{
    method: "get",
    headers: {'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'},
})
.then(response => response.json())
.then(data =>{
    console.log(data)
    selectCobradorInput.addEventListener("input",()=>{
        let resultado = buscar(selectCobradorInput.value,data)
        itemsCobradoresWrapper = actualizarResultados(resultado,itemsCobradoresWrapper)
    })
    
    itemsCobradoresWrapper.addEventListener("click",(event)=>{
        if(itemsCobradoresWrapper.contains(event.target)){
            selectCobradorInput.value = event.target.innerHTML
            let inputEventCobrador = new Event('input')
            selectCobradorInput.dispatchEvent(inputEventCobrador) 
        }
    })

})

selectCobradorInput.addEventListener("click",()=>{
    itemsCobradoresWrapper.classList.add("active")
})





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
        lis += "<li>"+item["name"]+"</li>";
  
    });
    contenedor.insertAdjacentHTML("beforeend",lis)
    return contenedor
}


