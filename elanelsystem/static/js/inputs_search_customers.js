const inputSearchCustomer = document.getElementById("customer")
const listContainersData = document.querySelectorAll(".container_data")
const attr_list =["nro_cliente","nombre", "dni","domic","loc","prov","cod_postal","tel","fec_nacimiento","estado_civil","ocupacion"]
const url = window.location.pathname;

fetch(url,{
  method: 'get',
  headers: {'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' ,}
}).then(
  function(response){
      return response.json()
  }
).then(data =>{
  inputSearchCustomer.addEventListener("input", () => {
    const texto = inputSearchCustomer.value;
    const resultados = buscar(texto, data);
    let contador = 0

    // aca comienza lo chido
    listContainersData.forEach(element => {
      const contenedorResultados = element.children[1]
      actualizarResultados(resultados,contenedorResultados,contador);
      contador++
    });
  })

})
function actualizarResultados(resultados, contenedor,cont) {
  contenedor.innerHTML = "";
  let atributo = attr_list[cont]
  resultados.forEach((item) => {
    const li = document.createElement("li");
    console.log(item[atributo])
    li.textContent = item[atributo];
    contenedor.appendChild(li);
  });
}


function buscar(texto, datos) {
    return datos.filter((item) => {
      const valores = Object.values(item);
      const string = valores.join(",")
      return valores.some((valor) => {
        if (typeof valor === "string") {
          return valor.toLowerCase().includes(texto.toLowerCase());
        }
        return false;
      });
    });
}


