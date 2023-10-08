const inputSearchOperation = document.getElementById("operation")
let listData = document.querySelectorAll(".operationItem")
const containerData = document.querySelector(".operationsList")
const nCliente = document.getElementById("numberCliente")

inputSearchOperation.addEventListener("input", () => {
    const texto = inputSearchOperation.value;
    listData.forEach(element => {
        try {
            let nroOperacion = element.children[1].children[4].children[1].textContent
            if(texto == nroOperacion){
                element.style.display = "flex"
            }else if(texto ==""){
                element.style.display = "flex"
            }
            else{
                element.style.display = "none"
            }
        } catch (error) {
            let nroOperacion = element.children[1].children[3].children[1].textContent
            if(texto == nroOperacion){
                element.style.display = "flex"
            }else if(texto == ""){
                element.style.display = "flex"
            }else{
                element.style.display = "none"
            }
        }
    });
  })