const listProducto = document.querySelector('#wrapperProducto ul#contenedorProducto')
const inputTipoDeProducto = document.querySelector('#tipoProductoInput')
const inputProducto = document.querySelector('#productoInput')
const submitAdjudicacionButton = document.querySelector('#enviar')

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
    }
});


// Cuando se selecciona un producto se guarda en la variable productoHandled
inputProducto.addEventListener("input", async () => {
    if (productos != null) {
        productoHandled = productos.filter((item) => item["nombre"] == inputProducto.value)[0];
    }
    if (window.location.href.includes("sorteo")) {
        id_importe.value = productoHandled ? productoHandled["importe"] * cantidadChances : "";
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
    try {
        let dineroDeCuotas = parseInt(document.querySelector("#wrapperSumaCuotasPagadas .textInputP").textContent)
        if (window.location.href.includes("negociacion")) {
            let subTotalSinIntereses = parseInt(id_importe.value) - (dineroDeCuotas * (parseInt(id_porcentaje_a_reconocer.value) / 100) + parseInt(id_anticipo.value))
            id_intereses_generados.value = parseInt((subTotalSinIntereses * id_tasa_interes.value) / 100)

            id_total_a_pagar.value = subTotalSinIntereses + parseInt(id_intereses_generados.value)
            id_importe_x_cuota.value = parseInt(parseInt(id_total_a_pagar.value) / parseInt(id_nro_cuotas.value))
        } else {
            // let importeAFinanciar = parseInt(document.querySelector("#wrapperImporte .textInputP").textContent)

            id_intereses_generados.value = parseInt((parseInt(id_importe.value) * id_tasa_interes.value) / 100)

            id_total_a_pagar.value = (parseInt(id_importe.value) + parseInt(id_intereses_generados.value)) - parseInt(dineroDeCuotas)
            id_importe_x_cuota.value = parseInt((parseInt(id_importe.value) / parseInt(id_nro_cuotas.value)) + (parseInt(id_intereses_generados.value) / parseInt(id_nro_cuotas.value)))

        }

    } catch (error) {
        console.log(error)

    }
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


submitAdjudicacionButton.addEventListener("click", async () => {
    body = {}
    let inputs = form_create_sale.querySelectorAll("input")
    let textareas = form_create_sale.querySelectorAll("textarea")
    let inputsAsP_tag = form_create_sale.querySelectorAll(".textInputP")

    inputs = [...inputs, ...textareas, ...inputsAsP_tag]

    inputs.forEach(element => {
        body[element.name] = element.value
    });

    // document.getElementById('loader').style.display = 'block';
    let response = await fetchFunction(body, window.location.pathname)

    if (!response["success"]) {
        mostrarErrores(response["errors"], form_create_sale)
    } else {
        window.location.href = response["urlRedirect"];
    }

    // document.getElementById('loader').style.display = 'none';

})


function checkInputs() {
    const requiredInputs = form_create_sale.querySelectorAll('input[required]');
    let allInputsCompleted = true;

    requiredInputs.forEach(input => {
        if (input.value.trim() === '') {
            allInputsCompleted = false;
        }
    });

    if (allInputsCompleted) {
        submitAdjudicacionButton.disabled = false;
    } else {
        submitAdjudicacionButton.disabled = true;
    }
}

// Agregar evento de input a los inputs requeridos
const requiredInputs = form_create_sale.querySelectorAll('input[required]');
requiredInputs.forEach(input => {
    input.addEventListener('input', checkInputs);
});
