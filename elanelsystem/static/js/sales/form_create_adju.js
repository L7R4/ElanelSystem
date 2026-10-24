const listProducto = document.querySelector(
  "#wrapperProducto ul#contenedorProducto"
);
const inputTipoDeProducto = document.querySelector("#tipoProductoInput");
const inputProducto = document.querySelector("#productoInput");
const submitAdjudicacionButton = document.querySelector("#enviar");

const inputsWithEventInput = document.querySelectorAll(".eventInput");

//#region Fetch data
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
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
      method: "POST",
      body: JSON.stringify(body),
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
    });

    if (!response.ok) {
      throw new Error("Error");
    }

    const data = await response.json();
    return data;
  } catch (error) {}
}
//#endregion - - - - - - - - - - - - - - -

let productoHandled; // Variable para guardar el producto seleccionado
let productos; // Variable para guardar los productos

async function requestProductos() {
  let body = {
    // "sucursal": sucursalInput.value,
    tipoProducto: inputTipoDeProducto ? inputTipoDeProducto.value : null,
  };

  let data = await fetchFunction(body, urlRequestProductos);

  return data["productos"];
}

// Cuando se selecciona un tipo de producto se filtran los productos
inputTipoDeProducto.addEventListener("input", async () => {
  productos = await requestProductos();

  listProducto.innerHTML = ""; // Limpia la lista de productos
  listProducto.previousElementSibling.value = ""; // Limpia el input de producto en caso de que se haya seleccionado un producto
  if (productos.length != 0) {
    inputProducto.parentElement.parentElement.classList.remove("desactive"); // Desbloquea el input de producto

    // El servidor los manda de la A a la Z y createLiHTMLElement inserta al principio, por eso se recorren al revés.
    [...productos].reverse().forEach((product) => {
      createLiHTMLElement(listProducto, product.id, product.nombre);
    });
  } else {
    inputProducto.parentElement.parentElement.classList.add("desactive"); // Bloquea el input de producto
  }
});

// Cuando se selecciona un producto se guarda en la variable productoHandled
inputProducto.addEventListener("input", async () => {
  if (productos != null) {
    productoHandled = productos.filter(
      (item) => item["id"] == inputProducto.value
    )[0];
  }
  console.log("WEpsss");
  console.log(productoHandled);
  id_importe.value = productoHandled
    ? productoHandled["importe"] * cantidadChances
    : "";

  rellenarCamposDeVenta();
});

// Agrega listener de tipo input a los inputs que son necesarios para calcular los valores de venta
inputsWithEventInput.forEach((input) => {
  input.addEventListener("input", () => {
    rellenarCamposDeVenta();
  });
});

function rellenarCamposDeVenta() {
  try {
    let dineroDeCuotas = parseInt(
      document
        .querySelector("#wrapperSumaCuotasPagadas .textInputP")
        .textContent.replace(/[^\d-]/g, "")
    );
    if (window.location.href.includes("negociacion")) {
      // Todo en pesos enteros: el % a reconocer sobre un total de pagos impar da medio peso
      // (ej. 529167 * 50% = 264583,5) y el server exige enteros (daba 500 con "3630207.5").
      let subTotalSinIntereses = Math.round(
        parseInt(id_importe.value) -
          (dineroDeCuotas * (parseInt(id_porcentaje_a_reconocer.value) / 100) +
            parseInt(id_anticipo.value))
      );
      id_intereses_generados.value = parseInt(
        (subTotalSinIntereses * id_tasa_interes.value) / 100
      );

      id_total_a_pagar.value =
        subTotalSinIntereses + parseInt(id_intereses_generados.value);
      id_importe_x_cuota.value = parseInt(
        parseInt(id_total_a_pagar.value) / parseInt(id_nro_cuotas.value)
      );
    } else {
      // let importeAFinanciar = parseInt(document.querySelector("#wrapperImporte .textInputP").textContent)
      let valor_inicial_a_financiar =
        parseInt(id_importe.value) - dineroDeCuotas;

      id_intereses_generados.value = parseInt(
        (parseInt(valor_inicial_a_financiar) * id_tasa_interes.value) / 100
      );

      id_total_a_pagar.value =
        parseInt(valor_inicial_a_financiar) +
        parseInt(id_intereses_generados.value);
      //   id_importe_x_cuota.value = parseInt(
      //     parseInt(id_importe.value) / parseInt(id_nro_cuotas.value) +
      //       parseInt(id_intereses_generados.value) / parseInt(id_nro_cuotas.value)
      //   );
      id_importe_x_cuota.value = parseInt(
        parseInt(id_total_a_pagar.value) / parseInt(id_nro_cuotas.value)
      );
    }
  } catch (error) {
    console.log(error);
  }
  sincronizarPrimerCuota();
}

// La cuota 1 se precarga con el importe por cuota mientras la administrativa no la toque;
// si la cambia (por ejemplo a 0 porque no se cobra) se respeta su valor.
const inputPrimerCuota = document.querySelector("#id_primer_cuota");
inputPrimerCuota.addEventListener("input", () => {
  inputPrimerCuota.dataset.editado = "1";
});

function sincronizarPrimerCuota() {
  if (inputPrimerCuota.dataset.editado) return;
  const valor = parseInt(document.querySelector("#id_importe_x_cuota").value);
  inputPrimerCuota.value = Number.isNaN(valor) ? "" : valor;
}

// Esto evita el comportamiento predeterminado del boton "Enter"
document.addEventListener("keydown", function (e) {
  if (e.key === "Enter") {
    e.preventDefault();
  }
});

// Crear un elemento li para el producto
function createLiHTMLElement(contenedor, li_id, li_name) {
  let stringForHTML = "";

  stringForHTML = `<li data-value="${li_id}">${li_name}</li>`;
  contenedor.insertAdjacentHTML("afterbegin", stringForHTML);
}

submitAdjudicacionButton.addEventListener("click", async () => {
  body = {};
  let inputs = form_create_sale.querySelectorAll("input");
  let textareas = form_create_sale.querySelectorAll("textarea");

  inputs = [...inputs, ...textareas];

  inputs.forEach((element) => {
    body[element.name] = element.value;
  });

  let response = await fetchFunction(body, window.location.pathname);

  if (!response || !response["success"]) {
    mostrarErrores(response ? response["errors"] : {}, form_create_sale);
  } else {
    window.location.href = response["urlRedirect"];
  }
});

function setSubmitEnabled(enabled) {
  submitAdjudicacionButton.disabled = !enabled;
  if (enabled) {
    submitAdjudicacionButton.removeAttribute("disabled");
    submitAdjudicacionButton.classList.remove("blocked");
  } else {
    submitAdjudicacionButton.setAttribute("disabled", "");
    submitAdjudicacionButton.classList.add("blocked");
  }
}

// Busca la etiqueta visible de un campo para armar el mensaje de "faltan completar"
function getFieldLabel(input) {
  const wrapper = input.closest(".inputWrapper, .field-block");
  const label = wrapper?.querySelector("label");
  return label ? label.textContent.trim() : input.name || input.id;
}

function showMissingFieldsMessage(labels) {
  const msgEl = document.getElementById("missingFieldsMsg");
  if (!msgEl) return;
  if (labels.length === 0) {
    msgEl.textContent = "";
    msgEl.classList.remove("active");
  } else {
    msgEl.textContent = "Faltan completar: " + labels.join(", ");
    msgEl.classList.add("active");
  }
}

function checkInputs() {
  let requiredFields = Array.from(
    form_create_sale.querySelectorAll("input[required]")
  );

  // Ignorá requeridos que estén dentro de un bloque desactivado
  requiredFields = requiredFields.filter((el) => !el.closest(".desactive"));

  const missing = requiredFields.filter((input) => input.value.trim() === "");
  setSubmitEnabled(missing.length === 0);
  showMissingFieldsMessage(missing.map(getFieldLabel));
}

// Agregar evento de input a los inputs requeridos
const requiredInputs = form_create_sale.querySelectorAll("input[required]");
requiredInputs.forEach((input) => {
  input.addEventListener("input", checkInputs);
});

checkInputs(); // muestra el mensaje de campos faltantes ya desde la carga inicial

// ================= Pre-completar Tipo de Producto / Producto / Contrato =================
// El producto que se está adjudicando ya se conoce (es el de la venta), así
// que evitamos que la administrativa tenga que volver a elegirlo a mano.
async function prefillDesdeVenta() {
  const pre = window.prefillAdjudicacion;
  if (!pre || !pre.tipoProducto) return;

  const tipoLi = document.querySelector(
    `#contenedorTipo li[data-value="${CSS.escape(pre.tipoProducto)}"]`
  );
  if (!tipoLi) return; // tipo desconocido: dejamos el form como estaba

  window.setSelectValue("#tipoProductoInput", {
    value: pre.tipoProducto,
    label: tipoLi.textContent.trim(),
    fire: false,
    markSelected: true,
  });

  productos = await requestProductos();
  listProducto.innerHTML = "";
  if (!productos || !productos.length) return;

  inputProducto.parentElement.parentElement.classList.remove("desactive");
  [...productos].reverse().forEach((product) => {
    createLiHTMLElement(listProducto, product.id, product.nombre);
  });

  const productoPreSeleccionado = productos.find(
    (p) => String(p.id) === String(pre.productoId)
  );
  if (productoPreSeleccionado) {
    productoHandled = productoPreSeleccionado;
    window.setSelectValue("#productoInput", {
      value: productoPreSeleccionado.id,
      label: productoPreSeleccionado.nombre,
      fire: false,
      markSelected: true,
    });
    id_importe.value = productoHandled["importe"] * cantidadChances;
    rellenarCamposDeVenta();
  }

  // El contrato solo se pre-completa si la venta tiene una única chance:
  // si tiene varias, tiene que elegir cuál se está adjudicando.
  if (pre.contrato) {
    window.setSelectValue("#id_nro_contrato", {
      value: pre.contrato,
      label: pre.contrato,
      fire: true,
      markSelected: true,
    });
  }

  checkInputs();
}
prefillDesdeVenta();
