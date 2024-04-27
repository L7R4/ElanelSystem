// PARA ENTEDER COMO FUNCIONA EL BUSCADOR:
// 1) VER LA FUNCION buscar
// 2) VER LA FUNCION actualizarResultados
// 3) Y POR ULTIMO RECIEN VER AddEventListener

const inputSearchOperation = document.getElementById("operation")
const containerData = document.querySelector(".operationsList")

async function requestVentas(sucursal,campania) {
    try{
        let response = await fetch(`/ventas/request_ventas/?sucursal=${sucursal}&campania=${campania}`,{
            method: 'get',
            headers: {'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'},
            cache: 'no-store'  
        })
        if(!response.ok){
            throw new Error("Error")
        }
        const data = await response.json();
        return data;
    }catch(error){
    }
}

// 3) TERCER PASO  
var receibedSells;
document.addEventListener('DOMContentLoaded', async() => {
    receibedSells = await requestVentas(sucursalInput.value, inputCampania.value)
    inputSearchOperation.addEventListener("input", () => {
    const texto = inputSearchOperation.value;
    const resultados = buscar(texto, receibedSells["ventas"]);
    realodAmountAuditorias(receibedSells["resumenAuditorias"])
    actualizarResultados(resultados,containerData);
    showDetailsVentas();
    })
});

// 2) SEGUNDO PASO
function actualizarResultados(resultados, contenedor) {
  // Limpia el contenedor de los datos
  contenedor.innerHTML = "";
  // Se reccore los datos filtrados
  resultados.forEach((item) => {
    let div ="";
    // Se reccore los campos de cada elemento y se lo guarda en un div
    div += itemVentaHTML(item["id"],item["cliente"],item["dni"],item["nroOrden"],item["fec_insc"],item["tel"],item["cp"],item["loc"],item["prov"],item["direc"],item["vendedor"],item["supervisor"],item["auditoria"],item["campania"]);
    
    contenedor.insertAdjacentHTML("beforeend",div)
  });
}

// 1) PRIMER PASO
function buscar(texto, datos) {
    let listFilteredData = datos.filter((item) => {
      // Accede a unicamente a los valores de cada elemento del JSON
      let valores = Object.values(item);
  
      // Los transforma al elemento en string para que sea mas facil filtrar por "include"
      let string = valores.join(",");
  
      return string.toLocaleLowerCase().includes(texto.toLocaleLowerCase());
    });
    return listFilteredData;
}

// Esto evita el comportamiento predeterminado del botón "Tab" y el "Enter"
document.addEventListener('keydown', function (e) {
  if (e.key === 'Tab' || e.key === 'Enter') {
    e.preventDefault();
  }
});

function itemVentaHTML(id,nombre,dni,nro_orden,fecha,tel,cod_postal,loc,prov,domic,vendedor,supervisor,auditoria,campania) {
    let stringHTML = `
    <li class="operationItem">
        <div class="ventaWrapper">
                <div class="atributtes">
                    <button type="button" class="displayDetailInfoButton">
                        <img src="${imgNext}" alt="">
                    </button>

                    <div class="wrapperShortInfo">
                        <div class="wrapperInfoAtributte">
                            <h4>Cliente</h4>
                            <h1>${nombre}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>DNI</h4>
                            <h1>${dni}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>Nro Orden</h4>
                            <h1>${nro_orden}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>Fecha de inscripcion</h4>
                            <h1>${fecha}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>Telefono</h4>
                            <h1>${tel}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>CP</h4>
                            <h1>${cod_postal}</h1>
                        </div>
                    </div>
                    <div class="wrapperDetailInfo">
                        <div class="wrapperInfoAtributte">
                            <h4>Localidad</h4>
                            <h1>${loc}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>Provincia</h4>
                            <h1>${prov}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>Direccion</h4>
                            <h1>${domic}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>Vendedor</h4>
                            <h1>${vendedor}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>Supervisor</h4>
                            <h1>${supervisor}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>Campaña</h4>
                            <h1>${campania}</h1>
                        </div>`
    if (auditoria[auditoria.length - 1]["realizada"]){
        stringHTML +=`<div class="containerHistorialAuditorias">`
        auditoria.forEach((e,i,array) => {
            stringHTML += `
                <div class="infoCheckWrapper">
                    <div class="wrapperComentarios">
                        <h4>Comentarios</h4>
                        <p>${e.comentarios}</p>
                    </div>
                    <div class="wrapperFechaHora">
                        <p>${e.fecha_hora}</p>
                    </div>
                    <div class="wrapperGrade">
                        ${e["grade"] ? '<p>Aprobada</p>' : '<p>Desaprobada</p>'}
                    </div>
                    ${i == array.length - 1 ? '<div class="wrapperUltimo"><p>Último</p></div>' : ""}
                </div>`
        });
        stringHTML += `</div></div>`
    }
    stringHTML += ` 
    <div class="statusWrapper">
        <div class="buttonsWrapper">`
    if (auditoria[auditoria.length - 1]["realizada"]){
        stringHTML += `<label for="editarI" id="editar" onclick="formEditPostVenta(${id},this.offsetParent)">Editar</label>
        </div>
        <div class="statusPostVenta">` 
        if(auditoria[auditoria.length - 1]["grade"]){
            stringHTML += `<div class="dotStatus aprobada"></div>
                           <h3>Auditoria aprobada</h3></div>` 
        }else{
            stringHTML += `<div class="dotStatus desaprobada"></div>
                            <h3>Auditoria desaprobada</h3></div>` 
        }

    }else{
        stringHTML += `<input type="radio" name="grade" id="aprobarI" value="a">
        <label for="aprobarI" id="aprobar" class ="labelInputGrade" onclick="formComentario(${id},this.offsetParent.parentElement,this.id)">Aprobar</label>
        <input type="radio" name="grade" id="desaprobarI" value="d">
        <label for="desaprobarI" id="desaprobar" class ="labelInputGrade" onclick="formComentario(${id},this.offsetParent.parentElement,this.id)">Desaprobar</label>
        </div>
        <div class="statusPostVenta">
            <div class="dotStatus pendiente"></div>
            <h3>Auditoria pendiente</h3>
        </div>`
    }
    stringHTML += `</div>               
            </div>
        </div>
    </li>`

    return stringHTML;

}

function realodAmountAuditorias(amountAuditoriasDict) {
    // Itera sobre los elementos con la clase amountAuditorias
    document.querySelectorAll('.amountAuditorias').forEach(elemento => {
        // Obtiene el ID del elemento
        let id = elemento.id;
        // Si el ID existe en el diccionario, actualiza el texto
        if (amountAuditoriasDict.hasOwnProperty(id)) {
            elemento.textContent = amountAuditoriasDict[id];
        }
    });

}
