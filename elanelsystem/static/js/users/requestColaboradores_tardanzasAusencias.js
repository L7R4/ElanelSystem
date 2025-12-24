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
        let response = await fetch(url, {
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

const sucursalInput = document.getElementById("sucursalInput");
const rangoInput = document.getElementById("rangoInput");
const itemsColaboradoresContainer = document.querySelector('.colaboradoresDataWrapper');

function habilitarTardanzaAusencia() {
    return sucursalInput.value != "" && rangoInput.value != ""
}

// Realizar la petición fetch al cargar la página con el valor default del input sucursal
let body = {"sucursal":sucursalInput.value, "rango":rangoInput.value}
renderColaboradores(body)

// Escuchar cambios en el input de sucursal
sucursalInput.addEventListener("input", function () {
    body = {"sucursal":sucursalInput.value, "rango":rangoInput.value}
    if(habilitarTardanzaAusencia()){
        renderColaboradores(body)
    }else{
        itemsColaboradoresContainer.innerHTML =""
    }
});
// Escuchar cambios en el input de rango
rangoInput.addEventListener("input", function () {
    body = {"sucursal":sucursalInput.value, "rango":rangoInput.value}
    if(habilitarTardanzaAusencia()){
        renderColaboradores(body)

    }else{
        itemsColaboradoresContainer.innerHTML =""
    }
});
    

async function renderColaboradores(body) {
    itemsColaboradoresContainer.innerHTML = ""
    let response = await fetchFunction(body,urlFilterUsuario);
    console.log(response)
    let colaboradores = response["colaboradores_data"]

    colaboradores.forEach(colaborador => {
        // Crear las filas para la tabla
        const trShortInfo = document.createElement("tr");
        trShortInfo.classList.add("wrapperShortInfo");

        trShortInfo.innerHTML = `
            <td>${colaborador.nombre}</td>
            <td class="textCountFaltas">${colaborador.countFaltas || 0}</td>
            <td class="textCountTardanzas">${colaborador.countTardanzas || 0}</td>
        `;

        const trDetailInfo = document.createElement("tr");
        trDetailInfo.classList.add("wrapperDetailInfo");
        trDetailInfo.style.display = "none"; // Oculto por defecto

        trDetailInfo.innerHTML = `
            <td colspan="3">
                <table class="detailTable">
                    <thead>
                        <tr>
                            <th>Tipo</th>
                            <th>Fecha</th>
                            <th>Hora</th>
                        </tr>
                    </thead>
                    <tbody class="itemsWrapper">
                        ${colaborador.tardanzasAusencias.map(item => `
                            <tr>
                                <td>${item.tipoEvento || ""}</td>
                                <td>${item.fecha || 0}</td>
                                <td>${item.hora || ""}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
                <div class="buttonsAddItem">
                    <button type="button" onclick="createNewItemForm(this,'${colaborador.email}','${colaborador.fechaHoy}','tardanza')">Agregar tardanza</button>
                    <button type="button" onclick="createNewItemForm(this,'${colaborador.email}','${colaborador.fechaHoy}','falta')">Agregar falta</button>
                </div>
            </td>
        `;

        // Agregar event listener al trShortInfo para mostrar/ocultar trDetailInfo
        trShortInfo.addEventListener('click', function () {
            trDetailInfo.style.display = trDetailInfo.style.display === 'none' ? 'table-row' : 'none';
        });

        // Agregar las filas al contenedor de la tabla
        itemsColaboradoresContainer.appendChild(trShortInfo);
        itemsColaboradoresContainer.appendChild(trDetailInfo);
    });
}