const listProducto = document.querySelector('#wrapperProducto ul')
const inputTipoDeProducto = document.querySelector('#tipoProductoInput')
const inputProducto = document.querySelector('#productoInput')
const submitChangePackButton = document.querySelector('#enviar')

const inputsWithEventInput = document.querySelectorAll(".eventInput")

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

let productoHandled; // Variable para guardar el producto seleccionado
let productos; // Variable para guardar los productos

async function requestProductos() {

    let body = {
        // "sucursal": sucursalInput.value,
        "tipoProducto": inputTipoDeProducto ? inputTipoDeProducto.value : null
    }

    let data = await fetchFunction(body, urlRequestProductos);

    return data["productos"];
}

// Cuando se selecciona un tipo de producto se filtran los productos
inputTipoDeProducto.addEventListener("input", async () => {
    productos = await requestProductos();

    listProducto.innerHTML = "" // Limpia la lista de productos
    listProducto.previousElementSibling.value = "" // Limpia el input de producto en caso de que se haya seleccionado un producto
    if (productos.length != 0) {

        inputProducto.parentElement.parentElement.classList.remove("desactive") // Desbloquea el input de producto

        productos.forEach(product => {
            createProductoHTMLElement(listProducto, product["nombre"]);
        });
        updateListOptions(listProducto, inputProducto); // Actualiza los listeners de la lista de productos
    } else {
        inputProducto.parentElement.parentElement.classList.add("desactive") // Bloquea el input de producto

        productoHandled = null // Resetea la variable productoHandled
        productos = null // Resetea la lista de productos

        // Forzar un evento input del inputProducto para que se reseteen los valores de los inputs
        let event = new Event('input');
        inputProducto.dispatchEvent(event);

    }

});


// Cuando se selecciona un producto se guarda en la variable productoHandled
inputProducto.addEventListener("input", async () => {
    if (productos != null) {
        productoHandled = productos.filter((item) => item["nombre"] == inputProducto.value)[0];
    }


    if (productoHandled) {
        id_importe.value = productoHandled["importe"];
        id_paquete.value = productoHandled["paquete"];
        id_primer_cuota.value = productoHandled["primer_cuota"]
        id_anticipo.value = productoHandled["suscripcion"]

    } else {
        id_importe.value = "";
        id_paquete.value = "";
        id_primer_cuota.value = "";
        id_anticipo.value = "";
    }
    rellenarCamposDeVenta();

});


// Agrega listener de tipo input a los inputs que son necesarios para calcular los valores de venta
inputsWithEventInput.forEach(input => {
    input.addEventListener("input", () => {
        rellenarCamposDeVenta();
    });
});


function rellenarCamposDeVenta() {
    let nroCuotas = parseInt(id_nro_cuotas.value)
    let importe = parseInt(id_importe.value)
    let dineroDeCuotas = parseInt(document.querySelector("#wrapperSumaCuotasPagadas .textInputP").textContent)

    try {
        // Valores de los inputs
        id_tasa_interes.value = porcentaje_segun_nroCuotas(nroCuotas)
        id_intereses_generados.value = (importe * parseFloat(id_tasa_interes.value)) / 100
        let total = (parseInt(id_intereses_generados.value) + importe) - dineroDeCuotas
        id_importe_x_cuota.value = parseInt((parseInt(total) / nroCuotas) + (parseInt(id_intereses_generados.value) / nroCuotas))
        id_total_a_pagar.value = total
    }

    catch (error) {
        id_tasa_interes.value = "";
        id_intereses_generados.value = "";
        id_importe_x_cuota.value = "";
        id_primer_cuota.value = "";
        id_anticipo.value = "";
        id_total_a_pagar.value = "";
    }
}

function porcentaje_segun_nroCuotas(nroCuotas) {
    let cuotasList = {
        '24': productoHandled["c24_porcentage"],
        '30': productoHandled["c30_porcentage"],
        '48': productoHandled["c48_porcentage"],
        '60': productoHandled["c60_porcentage"],
    }
    return cuotasList[nroCuotas] ? cuotasList[nroCuotas] : null
}

// Esto evita el comportamiento predeterminado del boton "Enter"
document.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
        e.preventDefault();
    }
});


// Crear un elemento li para el producto
function createProductoHTMLElement(contenedor, producto) {
    let stringForHTML = "";

    stringForHTML = `<li data-value="${producto}">${producto}</li>`;
    contenedor.insertAdjacentHTML('afterbegin', stringForHTML);
}


submitChangePackButton.addEventListener("click", async () => {
    body = {}
    let inputs = form_create_sale.querySelectorAll("input")
    let textareas = form_create_sale.querySelectorAll("textarea")

    inputs = [...inputs, ...textareas]

    inputs.forEach(element => {
        body[element.name] = element.value
    });

    let response = await fetchFunction(body, window.location.pathname)

    if (!response["success"]) {
        mostrarErrores(response["errors"], form_create_sale)
    } else {
        window.location.href = response["urlRedirect"];
    }


})

// Función para verificar si todos los inputs requeridos están completos
function checkInputs() {
    const requiredInputs = form_create_sale.querySelectorAll('input[required]');
    let allInputsCompleted = true;

    requiredInputs.forEach(input => {
        if (input.value.trim() === '') {
            allInputsCompleted = false;
        }
    });

    if (allInputsCompleted) {
        submitChangePackButton.disabled = false;
    } else {
        submitChangePackButton.disabled = true;
    }
}

// Agregar evento de input a los inputs requeridos
const requiredInputs = form_create_sale.querySelectorAll('input[required]');
requiredInputs.forEach(input => {
    input.addEventListener('input', checkInputs);
});
