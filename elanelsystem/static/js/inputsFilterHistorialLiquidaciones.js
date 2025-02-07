const informationTable = document.querySelector('.informationTable');
const inputsFilters = document.querySelectorAll(".wrapperSelectFilter input")
console.log(inputsFilters)
let url = window.location.pathname

function displayData(data) {
    informationTable.querySelector("tbody").innerHTML = "";

    data.forEach(item => {
        const { id, ...rest } = item; // Extraer 'id' y almacenar el resto de propiedades
        const itemDOM = `
            <tr id="${id}">
                ${Object.values(rest).map(value => `<td>${value}</td>`).join('')}
            </tr>`;
        informationTable.querySelector("tbody").insertAdjacentHTML('beforeend', itemDOM);
    });
}


inputsFilters.forEach(input => {
    input.addEventListener("input", async () => {
        createParams(inputsFilters)

        try {
            wrapperLoader.style.display = "flex";
            let request = await fetchFunction(url);
            wrapperLoader.style.display = "none";

            // Actualizar el DOM con los datos recibidos
            displayData(request.liquidaciones);
            const liquidacionesDOM = document.querySelectorAll(".informationTable > tbody > tr")
            listenerClickViewLiquidacion(liquidacionesDOM)
        } catch (error) {
            console.error("Error al obtener datos:", error);
        }
    })
})



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

function createParams(inputs) {
    if (url.includes("?")) {
        url = window.location.href;
    }

    inputs.forEach(input => {
        if (input.value.trim() !== "") {
            url += url.includes("?") ? "&" : "?";

            const inputName = input.name; // Obtener el atributo 'name' del input
            const inputValue = input.value; // Obtener el valor seleccionado
            let newParam = `${inputName}=${inputValue}`;
            url += newParam;
        }
    })
}

function listenerClickViewLiquidacion(liquidaciones) {
    liquidaciones.forEach(li => {
        li.addEventListener("click", () => {
            window.open(`/ventas/liquidaciones/pdf/liquidacion/${li.id}/`)
        })
    })
}

const liquidacionesDOM = document.querySelectorAll(".informationTable > tbody > tr")
listenerClickViewLiquidacion(liquidacionesDOM)


