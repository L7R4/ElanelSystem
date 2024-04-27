const inputRol = document.getElementById("rangoInput")
const vendedoresWrapper = document.getElementById("vendedoresWrapper")
const wrapperInputsObligatorios = document.querySelector(".inputsObligatorios")
var url = window.location.pathname;

// Para mostrar el input de vendedores
inputRol.addEventListener("input", async () => {
    let contenedor = document.querySelector("#itemsVendedores > ul")
    if (inputRol.value === "Supervisor") {

        wrapperInputsObligatorios.classList.add("supervisorPicked")
        vendedoresWrapper.classList.add("active")
        vendedoresWrapper.previousElementSibling.classList.add("active")
        if (url.includes("detalleusuario")) {
            let vendedores = await vendedoresACargoGet(sucursalInput.value, pkUser.value)
            vendedores["data"].forEach(v => {
                createVendedorHTMLElement(contenedor, v, vendedores["vendedores_a_cargo"]);
            });
        } else {
            let vendedores = await vendedoresGet(sucursalInput.value)
            vendedores["data"].forEach(v => {
                createVendedorHTMLElement(contenedor, v);
            });
        }



    } else {
        vendedoresWrapper.classList.remove("active")
        vendedoresWrapper.previousElementSibling.classList.remove("active")
        wrapperInputsObligatorios.classList.remove("supervisorPicked")
    }
})

sucursalInput.addEventListener("input", () => {
    // Crea un nuevo evento Change
    const inputEvent = new Event('input');

    // Forzar el evento Change en el elemento input
    inputRol.dispatchEvent(inputEvent);
})


// Funcion para cuando se esta editan un usuario
async function vendedoresACargoGet(sucursal, usuario) {
    const response = await fetch(`/usuario/administracion/requestusuarios_acargo/?sucursal=${sucursal}&usuario=${usuario}`, {
        method: 'get',
        headers: { 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' },
        cache: 'no-store',
    });
    const data = await response.json();
    return data;
}

// Funcion para cuando se esta creando un usuario nuevo
async function vendedoresGet(sucursal) {
    const response = await fetch(`/usuario/administracion/requestusuarios/?sucursal=${sucursal}`, {
        method: 'get',
        headers: { 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' },
        cache: 'no-store',
    });
    const data = await response.json();
    return data;
}

// Funcion para cuando se esta editan un usuario
function createVendedorACargoHTMLElement(contenedor, vendedor, list_vendedores_a_cargo) {
    let stringForHTML = ""
    contenedor.innerHTML = ''

    if (isVendedorInCargoList(vendedor, list_vendedores_a_cargo)) {
        stringForHTML = `<li>
        <input type="checkbox" checked name="idv_${vendedor.email}" id="idv_${vendedor.email}" value="${vendedor.email}">
        <label for="idv_${vendedor.email}">${vendedor.nombre}</label>
        </li> `;
    } else {
        stringForHTML = `<li>
            <input type="checkbox" name="idv_${vendedor.email}" id="idv_${vendedor.email}" value="${vendedor.email}">
            <label for="idv_${vendedor.email}">${vendedor.nombre}</label>
        </li> `;
    }
    contenedor.insertAdjacentHTML('afterbegin', stringForHTML);
}
// Funcion para cuando se esta creando un usuario nuevo
function createVendedorHTMLElement(contenedor, vendedor) {
    let stringForHTML = ""
    contenedor.innerHTML = ''

    stringForHTML = `<li>
        <input type="checkbox" name="idv_${vendedor.email}" id="idv_${vendedor.email}" value="${vendedor.email}">
        <label for="idv_${vendedor.email}">${vendedor.nombre}</label>
    </li> `;
    contenedor.insertAdjacentHTML('afterbegin', stringForHTML);
}

function isVendedorInCargoList(vendedor, list_vendedores_a_cargo) {
    return list_vendedores_a_cargo.some(item => item.email === vendedor.email);
}