// PARA ENTEDER COMO FUNCIONA EL BUSCADOR:
// 1) VER LA FUNCION buscar
// 2) VER LA FUNCION actualizarResultados
// 3) Y POR ULTIMO RECIEN VER AddEventListener

//#region Fetch data
async function fetchFunction(url) {
  try {
    let response = await fetch(url, {
      method: 'GET',
      headers: { 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' }
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


const inputSearchCustomer = document.getElementById("customer_search")
let listData = document.querySelectorAll(".item")
const containerData = document.querySelector(".values")

document.addEventListener('DOMContentLoaded', async function () {
  let customers = await fetchFunction(urlGetCustomers);

  inputSearchCustomer.addEventListener("input", () => {
    const texto = inputSearchCustomer.value;
    const resultados = buscar(texto, customers["response"]);
    actualizarResultados(resultados, containerData);
  })
});


// 1) PRIMER PASO
function buscar(texto, datos) {
  return datos.filter(item => {
    // Convierte todos los valores del objeto a una sola cadena
    let valores = Object.values(item).join(",").toLowerCase();
    // Filtra los objetos que contienen el texto buscado
    return valores.includes(texto.toLowerCase());
  });
}

// Esto evita el comportamiento predeterminado del botón "Tab" y el "Enter"
document.addEventListener('keydown', function (e) {
  if (e.key === 'Tab' || e.key === 'Enter') {
    e.preventDefault();
  }
});

