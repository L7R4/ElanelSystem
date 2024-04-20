const inputRol = document.getElementById("rangoInput")
const vendedoresWrapper = document.getElementById("vendedoresWrapper")
const wrapperInputsObligatorios = document.querySelector(".inputsObligatorios")


// Para mostrar el input de vendedores
inputRol.addEventListener("input",async ()=>{
    let contenedor = document.querySelector("#itemsVendedores > ul")
    if (inputRol.value === "Supervisor"){

        wrapperInputsObligatorios.classList.add("supervisorPicked")
        vendedoresWrapper.classList.add("active")
        vendedoresWrapper.previousElementSibling.classList.add("active")

        let vendedores = await vendedoresGet(sucursalInput.value, pkUser.value)
        vendedores["data"].forEach(v => {
            createVendedorHTMLElement(contenedor,v,vendedores.vendedores_a_cargo);
        });
        
    }else{
        vendedoresWrapper.classList.remove("active")
        vendedoresWrapper.previousElementSibling.classList.remove("active")
        wrapperInputsObligatorios.classList.remove("supervisorPicked")
    }
})

sucursalInput.addEventListener("input",()=>{
    // Crea un nuevo evento Change
    const inputEvent = new Event('input');

    // Forzar el evento Change en el elemento input
    inputRol.dispatchEvent(inputEvent);
})


async function vendedoresGet(sucursal,usuario) {
    const response = await fetch(`/usuario/administracion/requestusuarios/?sucursal=${sucursal}&usuario=${usuario}`, {
        method: 'get',
        headers: {'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'},
        cache: 'no-store',
    });
    const data = await response.json();
    return data;
}

function createVendedorHTMLElement(contenedor,vendedor,list_vendedores_a_cargo){
    let stringForHTML =""

    if(isVendedorInCargoList(vendedor,list_vendedores_a_cargo)){
        stringForHTML = `<li>
        <input type="checkbox" checked name="idv_${vendedor.email}" id="idv_${vendedor.email}" value="${vendedor.email}">
        <label for="idv_${vendedor.email}">${vendedor.nombre}</label>
        </li> `;
    }else{
        stringForHTML = `<li>
            <input type="checkbox" name="idv_${vendedor.email}" id="idv_${vendedor.email}" value="${vendedor.email}">
            <label for="idv_${vendedor.email}">${vendedor.nombre}</label>
        </li> `;
    }
    contenedor.insertAdjacentHTML('afterbegin', stringForHTML);
}

function isVendedorInCargoList(vendedor, list_vendedores_a_cargo) {
    return list_vendedores_a_cargo.some(item => item.email === vendedor.email);
}