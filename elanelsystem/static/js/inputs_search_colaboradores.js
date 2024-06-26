// PARA ENTEDER COMO FUNCIONA EL BUSCADOR:
// 1) VER LA FUNCION buscar
// 2) VER LA FUNCION actualizarResultados
// 3) Y POR ULTIMO RECIEN VER AddEventListener

const inputSearchCustomer = document.getElementById("customer")
let listData = document.querySelectorAll(".item")
const containerData = document.querySelector(".values")
const url = window.location.pathname;

fetch(url,{
  method: 'get',
  headers: {'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'},
  cache: 'no-store'  
}).then(
  function(response){
      return response.json()
})
  .then(data =>{
    console.log(data)
  // 3) TERCER PASO
  inputSearchCustomer.addEventListener("input", () => {
    const texto = inputSearchCustomer.value;
    const resultados = buscar(texto, data);
    actualizarResultados(resultados,containerData);
  })

})

// 2) SEGUNDO PASO
function actualizarResultados(resultados, contenedor) {
  // Limpia el contenedor de los datos
  contenedor.innerHTML = "";

  // Se reccore los datos filtrados
  resultados.forEach((item) => {
    let divs ="";

    // Se reccore los campos de cada elemento y se lo guarda en un div
    // Ademas de eso empieza en 1 porque el campo 0 es la pk para luego poder colocar el URL
    for (let i = 1; i < item.length; i++) {
      divs += "<div><p>"+item[i]+"</p></div>";
    }

    // Se crea la etiqueta a con el enlace de la pk (item[0]) 
    let enlace = "<a class ='item' href='/cliente/"+item[0]+"/operaciones/'>"+ divs +"</a>";
    contenedor.insertAdjacentHTML("beforeend",enlace)
  });
}

// 1) PRIMER PASO
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

// Esto evita el comportamiento predeterminado del botón "Tab" y el "Enter"
document.addEventListener('keydown', function (e) {
  if (e.key === 'Tab' || e.key === 'Enter') {
    e.preventDefault();
  }
});

