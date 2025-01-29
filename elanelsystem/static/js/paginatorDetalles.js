
const dataContainer = document.getElementById('data-container');
const buttonsPagesManage = document.querySelectorAll('.buttonsPagesManage');
const informationTable = document.querySelector('.informationTable');
const selectAgencia = document.getElementById('inputSucursal');

let page = 1;
let agencia = selectAgencia.value;
buttonsPagesManage.forEach(button => {
    button.addEventListener('click', async () => {
        page = button.value;
        wrapperLoader.style.display = "flex";
        let request = await fetchFunction(`/detalles/${tipoSlug}?agencia=${agencia}&page=${page}`);
        wrapperLoader.style.display = "none";

        updateValuePages(request);
        displayData(request);
    });
})

function displayData(data) {
    informationTable.querySelector("tbody").innerHTML = ""; // Limpiar la tabla

    if (informationTable.querySelector("thead > tr").children.length == 0) {
        displayHeaders(data);
    }

    data.data.forEach(item => {
        const itemDOM = `<tr>
            ${Object.values(item).map(value => `<td>${value.data}</td>`).join('')}
        
        </tr>`;
        informationTable.querySelector("tbody").insertAdjacentHTML('beforeend', itemDOM);
    });
}

function displayHeaders(data) {
    const headers = data.data[0];
    const headersDOM = Object.values(headers).map(header => `<th>${header.verbose_name}</th>`).join('');
    informationTable.querySelector("thead").innerHTML = headersDOM;
}

function updateValuePages(data) {
    previouPageButton.value = data.previous_page;
    nextPageButton.value = data.next_page;

    if (data.previous_page == null) {
        previouPageButton.disabled = true;
    } else {
        previouPageButton.disabled = false;
    }

    if (data.next_page == null) {
        nextPageButton.disabled = true;
    }
    else {
        nextPageButton.disabled = false;
    }

    textPaginator.textContent = `Página ${data.page} de ${data.total_pages}`;
}

// Filtro por sucursal


selectAgencia.addEventListener('input', async () => {
    agencia = selectAgencia.value;
    wrapperLoader.style.display = "flex";
    let request = await fetchFunction(`/detalles/${tipoSlug}/?agencia=${agencia}&page=${page}`);
    wrapperLoader.style.display = "none";


    updateValuePages(request);
    displayData(request);
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


