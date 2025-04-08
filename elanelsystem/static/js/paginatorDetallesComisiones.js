
const dataContainer = document.getElementById('data-container');
const buttonsPagesManage = document.querySelectorAll('.buttonsPagesManage');
const informationTable = document.querySelector('.informationTable');

const selectFilters = document.querySelectorAll(".wrapperTypeFilter .filterInput") 
let url = window.location.pathname

let page = 1;
buttonsPagesManage.forEach(button => {
    button.addEventListener('click', async () => {
        page = button.value;
        wrapperLoader.style.display = "flex";
        let request = await movsGetFilter(selectFilters,url);
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

selectFilters.forEach(select=>{
    select.addEventListener('input', async () => {
        wrapperLoader.style.display = "flex";
        let request = await movsGetFilter(selectFilters,url);
        wrapperLoader.style.display = "none";
    
    
        updateValuePages(request);
        displayData(request);
    })
})


// Funcion para obtener todos los movimientos por pagina 
async function movsGetFilter(inputs, url) {
    let urlParams = createParamsUrl(inputs)
    urlForFilter = urlParams
    console.log("a")
    const response = await fetch(`${url}?page=${page}${urlForFilter}`, {
        method: 'get',
        headers: { 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' },
        // cache: 'no-store',
    });
    if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
    }
    const data = await response.json();
    return data;
}



function createParamsUrl(inputs) {
    let urlParams = ""

    inputs.forEach(input => {
        if (input.value.trim() !== "") {
            urlParams += "&";

            const inputName = input.name; // Obtener el atributo 'name' del input
            const inputValue = input.value; // Obtener el valor seleccionado
            let newParam = `${inputName}=${inputValue}`;
            urlParams += newParam;
        }
    })
    return urlParams
}

