const inputRol = document.getElementById("rangoInput")
const vendedoresWrapper = document.getElementById("vendedoresWrapper")
const wrapperInputsObligatorios = document.querySelector(".inputsObligatorios")
let url = "/usuario/administracion/requestusuarios/";
let pkUser = document.querySelector("#pkUser") || null

// Para mostrar el input de vendedores
inputRol.addEventListener("input", async () => {
    let contenedor = document.querySelector("#itemsVendedores > ul")
    if (inputRol.value === "Supervisor") {

        wrapperInputsObligatorios.classList.add("supervisorPicked")
        vendedoresWrapper.classList.add("active")

        let body = {
            "sucursal": sucursalInput.value,
            "pkUser": pkUser.value
        }

        let vendedores = await fetchVendedores(body, url);
        contenedor.innerHTML = ""
        vendedores["data"].forEach(v => {
            createVendedorHTMLElement(contenedor, v);
        });



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



async function fetchVendedores(body, url) {
    try {
        let response = await fetch(url, {
            method: "POST",
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



// Funcion para cuando se esta creando un usuario nuevo
function createVendedorHTMLElement(contenedor, vendedor) {
    let stringForHTML = ""

    stringForHTML = `<li>
        <input type="checkbox" name="idv_${vendedor.email}" id="idv_${vendedor.email}" value="${vendedor.email}">
        <label for="idv_${vendedor.email}">${vendedor.nombre}</label>
    </li> `;
    contenedor.insertAdjacentHTML('afterbegin', stringForHTML);
}
