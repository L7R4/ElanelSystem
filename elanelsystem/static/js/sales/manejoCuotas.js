// ================= imports =================
import { openActionModal, apiFetch } from "../vanilla_components/async_ui.js";

// ================= DOM refs =================
const cuotasWrapper = document.querySelectorAll(".cuota");
const payCuotaForm = document.getElementById("payCuotaForm");
const wrapperVerDetallesPago = document.getElementById(
  "wrapperVerDetallesPago",
);

const btnPayCuota = document.getElementById("sendPayment");
const btnCloseFormCuota = document.getElementById("closeFormCuota");
const btnCloseViewCuota = document.getElementById("closeViewCuota");

// Ids/inputs globales que ya usabas
const ventaID = document.getElementById("ventaID");
const cuotaID = document.getElementById("cuotaID");

// ================= Descuento en cuotas (con openActionModal) =================
let resto = 0;

function escapeHTML(s) {
  return String(s ?? "").replace(
    /[&<>"']/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c],
  );
}

function buildDescuentoContent({ cuota }) {
  const num = String(cuota ?? "").match(/\d+/)?.[0] ?? "";
  const tipos = Array.isArray(window.tiposDescuento) ? window.tiposDescuento : [];
  // Mismo select personalizado que el resto del sistema (se inicializa en onOpen).
  // Es opcional: volver a tocar la opción elegida la deselecciona.
  const tipoSelectHTML = tipos.length
    ? `
        <div class="wrapperInput wrapperSelectCustom">
          <label class="labelInput" for="tipoDescuento">Tipo de descuento <span class="labelOptional">(opcional)</span></label>
          <div class="containerInputAndOptions">
            <input type="hidden" id="tipoDescuento" name="tipoDescuento"
                   placeholder="Sin especificar" autocomplete="off" readonly>
            <div class="onlySelect pseudo-input-select-wrapper">
              <h3></h3>
            </div>
            <i class="fa-solid fa-chevron-down iconDesplegar"></i>
            <ul class="list-select-custom options">
              ${tipos.map((t) => `<li data-value="${t.id}">${escapeHTML(t.alias)}</li>`).join("")}
            </ul>
          </div>
        </div>`
    : "";
  return `
    <div class="modalDescuento__content">
      <h2 class="titleModalDescuento">Descuento de cuota ${num}</h2>
      <form id="descuentoCuotaForm" class="wrapperDescuentoCuota" autocomplete="off">
        <div class="wrapperInput">
          <label class="labelInput" for="dineroDescuento">Monto</label>
          <input type="number" id="dineroDescuento" name="dineroDescuento"
                 class="input-read-write-default" placeholder="Monto a descontar" min="0">
        </div>
        ${tipoSelectHTML}
        <div class="wrapperInput">
          <label class="labelInput" for="autorizacionDescuento">Autorizado por</label>
          <input type="text" id="autorizacionDescuento" name="autorizacionDescuento"
                 class="input-read-write-default" placeholder="Nombre de quien autoriza">
        </div>
        <div data-status style="margin-top:.75rem;"></div>
      </form>
    </div>`;
}

function validateDescuento(root) {
  const monto = root.querySelector("#dineroDescuento")?.value.trim();
  const aut = root.querySelector("#autorizacionDescuento")?.value.trim();
  return !!aut && !!monto && Number(monto) > 0;
}

async function runDescuento({ root, signal }) {
  const ventaId = ventaID?.value;
  const cuotaId = cuotaID?.value;
  const monto = root.querySelector("#dineroDescuento").value.trim();
  const aut = root.querySelector("#autorizacionDescuento").value.trim();
  const tipoDescuento = root.querySelector("#tipoDescuento")?.value || "";

  const resp = await apiFetch("/ventas/detalle_venta/descuento_cuota/", {
    method: "POST",
    data: {
      ventaID: ventaId,
      cuota: cuotaId,
      descuento: monto,
      autorizado: aut,
      tipoDescuento: tipoDescuento,
    },
    signal,
  });

  if (!resp || resp.status === false) {
    return {
      ok: false,
      message: resp?.message || "No se pudo aplicar el descuento",
    };
  }

  // Actualización local opcional (mantengo tu lógica)
  if (typeof calcularDineroRestante === "function" && resp.cuotaUpdate) {
    const nuevoResto = calcularDineroRestante(resp.cuotaUpdate);
    if (
      typeof checkFormValid === "function" &&
      typeof validarInputsRellenados === "function" &&
      typeof validarMontoParcial === "function"
    ) {
      checkFormValid(
        validarInputsRellenados(),
        validarMontoParcial(nuevoResto),
      );
    }
  }
  descuentoAmountUpdate(resp.cuotaUpdate);
  return { ok: true, message: "Descuento aplicado" };
}

function descuentoAmountUpdate(cuotaData) {
  const descuentoDisplay = document.querySelector(
    ".descuento_cuota_total h3:last-child",
  );
  if (descuentoDisplay) {
    descuentoDisplay.textContent = cuotaData["descuento"]["monto"];
  }
}

export function openModalDescuento(cuota) {
  return openActionModal({
    modalOpts: {
      cssClass: ["modalDescuento"],
      closeMethods: ["button", "overlay", "escape"],
      // activa el select personalizado recién insertado en el modal
      onOpen: () => window.initCustomSingleSelects?.(),
    },
    buildContent: (ctx) => buildDescuentoContent(ctx),
    validate: validateDescuento,
    run: runDescuento,
    // el botón "Aplicar descuento" llama openModalDescuento() sin argumentos: la cuota abierta está en #cuotaID
    ctx: { cuota: cuota ?? cuotaID?.value },
    texts: {
      working: "Aplicando descuento...",
      success: "Descuento aplicado",
      error: "Error de red. Intenta nuevamente.",
      canceled: "Operación cancelada",
    },
    buttons: { confirm: "Confirmar", cancel: "Cerrar" },
  });
}
window.openModalDescuento = openModalDescuento;

// El botón lo devuelve el server solo para las cuotas 0 y 1 sin pagar. Se lo quita
// al cambiar de cuota o al terminar un pago: si quedaba, aparecía en cuotas donde
// el descuento no aplica (y el server lo rechazaba con "Descuento fallido").
function clearDescuentoButton() {
  payCuotaForm?.querySelector("#btnDescuentoCuota")?.remove();
}

function habilitacionDeBotonDescuento(buttonHTML) {
  const wrapperButtonPayCuota = payCuotaForm.querySelector(
    ".wrapperButtonPayCuota",
  );
  const lastButton = wrapperButtonPayCuota.lastElementChild;

  const parser = new DOMParser();
  const doc = parser.parseFromString(buttonHTML, "text/html");
  const buttonElement = doc.body.firstChild;

  if (!wrapperButtonPayCuota.querySelector("#btnDescuentoCuota")) {
    lastButton.insertAdjacentElement("beforebegin", buttonElement);
  }
}

// ================= Selección de cuota (carga detalle) =================
cuotasWrapper.forEach((cuota) => {
  cuota.addEventListener("click", async () => {
    // LIMPIEZA GLOBAL de la selección anterior:
    clearCancelButtons();
    clearDescuentoButton();
    clearAnularButtons();
    clearDetalleCuotaView();
    wrapperVerDetallesPago.classList.remove("active");
    payCuotaForm.classList.remove("active");

    try {
      const form = {
        ventaID: ventaID.value,
        cuota: cuota.id,
        dolar: dolar_oficial,
      };
      const data = await apiFetch("/ventas/detalle_venta/get_specific_cuota/", {
        method: "POST",
        data: form,
      });
      console.log(data);

      if (data.status === "Pagado") {
        wrapperVerDetallesPago.classList.add("active");
        verDetalleCuota(data);
        console.log(data);

        // Sólo insertás si viene del backend
        if (data.buttonCancelacionDePago) {
          habilitacionDeCancelacionPago(data.buttonCancelacionDePago, true);
        } else {
          // Por si acaso, asegúrate de que no haya quedado nada
          clearCancelButtons();
        }

        if (data.buttonAnularCuota) {
          habilitacionDeAnulacionPago(data.buttonAnularCuota, true);
        } else {
          console.log("Entro a clearAnularButtons");

          // Por si acaso, asegúrate de que no haya quedado nada
          clearAnularButtons();
        }
      } else if (data.status === "Pendiente") {
        payCuotaForm.classList.add("active");
        activeFormCuotas(data);
        const wrapperButtons = document.querySelector(".wrapperButtonPayCuota");
        wrapperButtons.insertAdjacentHTML(
          "beforebegin",
          htmlDetalleCuota(data),
        );
        clearCancelButtons(); // no tiene sentido que haya botón de cancelación ni de anulacion
        clearAnularButtons();

        if (data.buttonDescuentoCuota) {
          habilitacionDeBotonDescuento(data.buttonDescuentoCuota);
        }
      } else {
        payCuotaForm.classList.add("active");
        activeFormCuotas(data);
        const wrapperButtons = document.querySelector(".wrapperButtonPayCuota");
        wrapperButtons.insertAdjacentHTML(
          "beforebegin",
          htmlDetalleCuota(data),
        );

        if (data.buttonCancelacionDePago) {
          habilitacionDeCancelacionPago(data.buttonCancelacionDePago, false);
        } else {
          clearCancelButtons();
        }

        if (data.buttonDescuentoCuota) {
          habilitacionDeBotonDescuento(data.buttonDescuentoCuota);
        }

        if (data.buttonAnularCuota) {
          habilitacionDeAnulacionPago(data.buttonAnularCuota, false);
        } else {
          // Por si acaso, asegúrate de que no haya quedado nada
          // console.log("Entro a clearAnularButtons");
          clearAnularButtons();
        }
      }
    } catch (err) {
      console.log(err);
      showReponseModal(
        "No se pudo cargar la cuota. Intenta nuevamente.",
        "/static/images/icons/error_icon.png",
      );
    }
  });
});

function habilitacionDeCancelacionPago(buttonHTML, isView) {
  const container = isView
    ? wrapperVerDetallesPago?.querySelector(".buttonsActions")
    : payCuotaForm?.querySelector(".buttonsActions");

  if (!container) return;

  const lastButton = container.lastElementChild;

  // Parsear el HTML del botón que viene del backend
  const parser = new DOMParser();
  const doc = parser.parseFromString(buttonHTML, "text/html");
  const buttonEl = doc.body.firstElementChild;

  // Limpio botones previos para evitar duplicados
  payCuotaForm
    ?.querySelector(".buttonsActions > .buttonCancelarPago")
    ?.remove();
  wrapperVerDetallesPago
    ?.querySelector(".buttonsActions > .buttonCancelarPago")
    ?.remove();

  // Evito que traiga onclick viejos del backend
  buttonEl.removeAttribute("onclick");

  // Inserto el botón y le engancho el handler que corresponda (ajustá si tu acción es otra)
  lastButton.insertAdjacentElement("beforebegin", buttonEl);

  // Ejemplo: que abra el confirm de anulación que ya tenés
  const nuevoBtn = container.querySelector(".buttonCancelarPago");
  if (nuevoBtn) {
    nuevoBtn.addEventListener("click", () => {
      solicitudBajaCuota();
    });
  }
}

// si algún HTML inline intenta llamarla como global:
window.habilitacionDeCancelacionPago = habilitacionDeCancelacionPago;

function habilitacionDeAnulacionPago(buttonHTML, isView) {
  const container = isView
    ? wrapperVerDetallesPago?.querySelector(".buttonsActions")
    : payCuotaForm?.querySelector(".buttonsActions");

  if (!container) return;

  // Una sola copia: se quitan las anteriores (en ambos paneles) antes de insertar la nueva.
  clearCancelButtons();
  clearAnularButtons();

  // Parsear el HTML del botón que viene del backend
  const parser = new DOMParser();
  const doc = parser.parseFromString(buttonHTML, "text/html");
  const buttonEl = doc.body.firstElementChild;
  if (!buttonEl) return;

  // El backend manda onclick inline e ids distintos ("anularButton" / "btnAnularCuota"). Se
  // normaliza acá: una clase común (para poder limpiarlo siempre) y el clic enganchado directo
  // al botón. Antes se le borraba el onclick y el handler se buscaba por un id que no coincidía,
  // así que el botón se duplicaba en cada cuota abierta y no hacía nada al hacer clic.
  const texto = buttonEl.textContent.trim() || "Anular cuota";
  buttonEl.removeAttribute("onclick");
  buttonEl.removeAttribute("class");
  buttonEl.classList.add("btn-anular-cuota");
  buttonEl.type = "button";
  buttonEl.innerHTML = `<i class="fa-solid fa-rotate-left"></i> ${texto}`;
  buttonEl.addEventListener("click", () => anulacionCuota());

  container.lastElementChild.insertAdjacentElement("beforebegin", buttonEl);
}
function clearAnularButtons() {
  // .btn-anular-cuota es el botón actual; los ids son los que traía el backend (por si quedara alguno)
  document
    .querySelectorAll(
      ".containerDetalleCuota .buttonsActions > :is(.btn-anular-cuota, #anularButton, #btnAnularCuota)",
    )
    .forEach((b) => b.remove());
}

function clearCancelButtons() {
  payCuotaForm
    ?.querySelector(".buttonsActions > .buttonCancelarPago")
    ?.remove();
  wrapperVerDetallesPago
    ?.querySelector(".buttonsActions > .buttonCancelarPago")
    ?.remove();
}

function clearDetalleCuotaView() {
  wrapperVerDetallesPago?.querySelector(".wrapperInfo_cuota")?.remove();
  payCuotaForm?.querySelector(".wrapperInfo_cuota")?.remove();
}

// ================= Anular cuota (con pass en panel lateral) =================
async function anularCuota() {
  const url = "/ventas/detalle_venta/anular_cuota/";
  const form = { cuota: cuotaID.value, password: passwordAnularCuota.value };

  try {
    const response = await apiFetch(url, { method: "POST", data: form });

    if (response["status"]) {
      if (response["password"]) {
        actualizarEstadoCuota(cuotaID.value);
        actualizarEstadoProximasCuota(cuotaID.value, cantidadCuotas);
        displayMensajePostCuotaPagada(response.status, response.message);
        cerrarAnularCuotaForm();
        wrapperVerDetallesPago.classList.remove("active");
        document.querySelector("#anularButton")?.remove();
        document.querySelector(".wrapperInfo_cuota")?.remove();
      } else {
        showMessageFormAnularCuota();
      }
    } else {
      displayMensajePostCuotaPagada(response.status, response.message);
      cerrarAnularCuotaForm();
      wrapperVerDetallesPago.classList.remove("active");
    }
  } catch (err) {
    displayMensajePostCuotaPagada(false, "Error de red al anular la cuota");
  }
}
window.anularCuota = anularCuota; // la llamás desde el botón generado

// function htmlPassAnularCuota() {
//   if (!document.querySelector("#formAnularCuota")) {
//     const wrapper = document.querySelector("#wrapperVerDetallesPago");
//     const stringHTML = `
//       <form id="formAnularCuota" method="POST">
//         <h3>Para anular la cuota, ingrese su contraseña</h3>
//         <input type="text" placeholder="Contraseña" id="passwordAnularCuota" name="passwordAnularCuota" class="input-read-write-default">
//         <div class="buttonsWrapperAnularCuota">
//           <button type="button" onclick="anularCuota()" id="anularButton" class="delete-button-default">Anular cuota</button>
//           <button type="button" onclick="cerrarAnularCuotaForm()" id="cancelarAnularButton" class="button-default-style">Cancelar</button>
//         </div>
//       </form>`;
//     wrapper.insertAdjacentHTML('beforeend', stringHTML);
//   }
// }
function showMessageFormAnularCuota() {
  const inputForm = document.querySelector("#formAnularCuota > input");
  inputForm.insertAdjacentHTML(
    "afterend",
    `<h3 class="messageAnularCuota">Contraseña incorrecta</h3>`,
  );
}
function cerrarAnularCuotaForm() {
  document.querySelector("#formAnularCuota")?.remove();
}

// ================= Ver detalle de cuota =================
function verDetalleCuota(cuotaSelected) {
  clearDetalleCuotaView();
  const wrapper = document.querySelector("#wrapperVerDetallesPago");
  wrapper.insertAdjacentHTML("beforeend", htmlDetalleCuota(cuotaSelected));

  wrapper.querySelector(".cuotaPicked").innerHTML = cuotaSelected["cuota"];

  // Setear input hidden global
  const cuotaInput = payCuotaForm.querySelector("#cuotaID");
  cuotaInput.value = cuotaSelected["cuota"];

  // // Mostrar botón "Anular cuota" si corresponde
  // if (cuotaSelected["buttonAnularCuota"]) {
  //   if (!document.querySelector("#btnAnularCuota")) {
  //     wrapper.insertAdjacentHTML('beforeend', cuotaSelected["buttonAnularCuota"]);
  //     document.querySelector("#btnAnularCuota").addEventListener("click", ()=>{
  //       anulacionCuota();
  //     });
  //   }
  // } else {
  //   document.querySelector("#btnAnularCuota")?.remove();
  // }
}

function viewMoreFunction(elemento) {
  const icon = elemento.querySelector(".iconDisplayViewMore");
  const viewMoreContent = elemento.querySelector(".wrapperDetail_view_more");
  icon.classList.toggle("active");
  viewMoreContent.classList.toggle("active");
}
window.viewMoreFunction = viewMoreFunction; // lo usás en el HTML generado

function htmlDetalleCuota(cuota) {
  const cantPagos = Array.isArray(cuota["pagos"]) ? cuota["pagos"].length : 0;
  const hasPagos = cantPagos > 0;
  // stopPropagation: el botón está dentro de la fila desplegable y no debe abrirla/cerrarla
  const botonRecibo = hasPagos
    ? `<button type="button" onclick="event.stopPropagation(); abrirVistaPreviaRecibo(${cuota["pagos"][0].id})" id="btnReciboCuota">Ver recibo</button>`
    : "";
  // Solo se despliega si hay pagos registrados; sin pagos no hay nada que abrir.
  const filaPagos = hasPagos
    ? `<div onclick="viewMoreFunction(this)" class="info_cuota view_more" title="Ver el detalle de cada pago de esta cuota (fecha, método, cobrador y monto)">
        <h3>Pagos registrados</h3>
        <span class="pagos-meta">${cantPagos} ${cantPagos === 1 ? "pago" : "pagos"} · ver detalle</span>
        ${botonRecibo}
        <img class="iconDisplayViewMore" src="/static/images/icons/arrowDown.png" alt="">
        <div class="wrapperDetail_view_more">
          ${htmlPagos(cuota["pagos"])}
        </div>
      </div>`
    : `<div class="info_cuota view_more sin-pagos">
        <h3>Pagos registrados</h3>
        <span class="pagos-meta">Sin pagos todavía</span>
      </div>`;
  let stringHTML = `
    <div class="wrapperInfo_cuota">
      ${filaPagos}
      <div class="info_cuota descuento_cuota_total">
        <h3>Descuento</h3>
        <h3>${cuota["descuento"]["monto"]}</h3>
      </div>`;
  if (cuota["cuota"] !== "Cuota 0") {
    stringHTML += `
      <div class="info_cuota"><h3>Dias de atraso</h3><h3>${
        cuota["diasRetraso"]
      }</h3></div>
      <div class="info_cuota"><h3>Interes por mora</h3><h3>${
        cuota["interesPorMora"]
      }</h3></div>
      <div class="info_cuota"><h3>Total</h3><h3>$${
        cuota["total"] + cuota["interesPorMora"] - cuota["descuento"]["monto"]
      }</h3></div>
      <div class="info_cuota"><h3>Fecha de venc.</h3><h3>${cuota[
        "fechaDeVencimiento"
      ].substring(0, 10)}</h3></div>`;
  }
  stringHTML += `</div>`;
  return stringHTML;
}

// 1234.5 -> "1.234,50" (formato es-AR)
function formatUSD(n) {
  return Number(n).toLocaleString("es-AR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function htmlPagos(pagos) {
  // console.log(pagos);
  return pagos
    .map(
      (p, i) => `
    <div class="info_cuota detail_view_more title_payment">
    <h3>Pago ${i + 1}:</h3>
    </div>
    <div class="info_cuota detail_view_more"><h3>Fecha de pago</h3><h3>${
      p["fecha"]
    }</h3></div>
    <div class="info_cuota detail_view_more"><h3>Metodo de pago</h3><h3>${
      p["metodo_pago"] ?? p["metodoPago"] ?? "—"
    }</h3></div>
    <div class="info_cuota detail_view_more"><h3>Cobrador</h3><h3>${
      p["cobrador"] ?? "—"
    }</h3></div>
    <div class="info_cuota detail_view_more"><h3>Monto</h3><h3>$${
      p["monto"]
    }</h3></div>
    ${
      p["moneda"] === "USD" && p["monto_usd"] != null
        ? `<div class="info_cuota detail_view_more pago-usd"><h3>Pagado en dólares</h3><h3>USD ${formatUSD(
            p["monto_usd"],
          )} · cambio $${formatUSD(p["tipo_cambio"])}</h3></div>`
        : ""
    }
  `,
    )
    .join("");
}

// ================= Pagar cuota =================
btnPayCuota.addEventListener("click", async () => {
  console.log("Pagando cuota...");
  const typePaymentSelected = payCuotaForm.querySelector(
    '.wrapperChoices input[type="radio"]:checked',
  );
  const cobrador = payCuotaForm.querySelector(".input-cobrador");
  const metodoPago = payCuotaForm.querySelector(".input-metodoPago");
  const monedaInput = payCuotaForm.querySelector("input.input-moneda");

  const body = {
    cobrador: cobrador.value,
    typePayment: typePaymentSelected.value,
    metodoPago: metodoPago.value,
    ventaID: ventaID.value,
    cuota: cuotaID.value,
    // valorParcial va en la moneda elegida; el server lo pasa a pesos con el tipo de cambio
    valorParcial: amountParcial.value,
    moneda: String(monedaInput?.value || "ars").toLowerCase(),
    tipoCambio: Number(window.dolar_oficial ?? 0) || 0,
  };

  // pequeña protección de UI
  btnPayCuota.disabled = true;
  btnPayCuota.classList.add("blocked");

  try {
    const data = await apiFetch("/ventas/detalle_venta/pay_cuota/", {
      method: "POST",
      data: body,
    });

    document.querySelector(".wrapperUrlRecupero")?.remove();

    actualizarEstadoCuota(cuotaID.value);
    actualizarEstadoProximasCuota(cuotaID.value, cantidadCuotas);

    displayMensajePostCuotaPagada(data.status, data.message);
    hideFormCuotas();
  } catch (err) {
    displayMensajePostCuotaPagada(false, "No se pudo procesar el pago");
  } finally {
    btnPayCuota.disabled = false;
    btnPayCuota.classList.remove("blocked");
  }
});

// ================= Cierres simples =================
btnCloseFormCuota.addEventListener("click", hideFormCuotas);

btnCloseViewCuota.addEventListener("click", () => {
  wrapperVerDetallesPago.classList.remove("active");
  clearDetalleCuotaView(); // remueve contenido anterior
  clearCancelButtons(); // evita que quede el botón en la vista
});

function hideFormCuotas() {
  payCuotaForm.classList.remove("active");
  payCuotaForm.reset();
  clearCancelButtons(); // <-- importante
  clearDescuentoButton();
  clearInputs([], payCuotaForm); // inputs vacíos, pero con scope = form
}

// ================= Lógica de validaciones del form de pago =================
function verificarEstadoDeLaCuenta(cuota) {
  return cuota["status"] === "Parcial";
}

function validarMontoParcial(restoValor) {
  const monto = payCuotaForm.querySelector("#amountParcial").value;
  // restoValor está en ARS: si se paga en USD, el monto tipeado se compara ya convertido
  const enUSD =
    String(payCuotaForm.querySelector("input.input-moneda")?.value || "ars").toLowerCase() === "usd";
  const dolar = Number(window.dolar_oficial ?? 0) || 0;
  const esTotal =
    payCuotaForm.querySelector('input[name="typePayment"]:checked')?.value === "total";
  const montoARS = enUSD ? Number(monto) * dolar : Number(monto);
  // En USD el monto se redondea al centavo (ej. 175000/1485 = 117,845 -> 117,85), lo que puede pasarse
  // de unos pesos: se tolera hasta 1 centavo de dólar. "Abonar total" nunca se bloquea: el server
  // cobra el total exacto en pesos.
  const tolerancia = enUSD ? dolar * 0.01 : 0;
  if (!esTotal && montoARS > Number(restoValor) + tolerancia) {
    btnPayCuota.disabled = true;
    btnPayCuota.classList.add("blocked");
    amountParcial.style.border = "2px solid var(--danger-color)";
    return false;
  } else {
    btnPayCuota.disabled = false;
    btnPayCuota.classList.remove("blocked");
    amountParcial.style.border = "2px solid var(--blue-accent-color)";
    return true;
  }
}

function calcularDineroRestante(cuota) {
  const dineroRestanteHTML = payCuotaForm.querySelector("#dineroRestante");

  // El total de la cuota siempre está expresado en ARS; la conversión a USD
  // para mostrar en pantalla la hace setupMonedaWatcher() a partir de este
  // valor (dividiendo por dolar_oficial), no esta función.
  const sumaPagos = cuota["pagos"]
    .map(({ monto }) => monto)
    .reduce((acc, n) => acc + n, 0);

  resto = cuota["total"] - (sumaPagos + cuota["descuento"]["monto"]);
  dineroRestanteHTML.textContent = "Dinero restante: $" + resto;
  return resto;
}

function activeFormCuotas(cuotaSelected) {
  payCuotaForm.querySelector(".cuotaPicked").innerHTML = cuotaSelected["cuota"];
  payCuotaForm.querySelector("#cuotaID").value = cuotaSelected["cuota"];

  const choices = payCuotaForm.querySelectorAll(".wrapperChoices > .choice");
  if (verificarEstadoDeLaCuenta(cuotaSelected)) {
    choices[0].style.display = "none";
    setearInputAFormaDePago(choices[1]);
  } else {
    setearInputAFormaDePago(choices[0]);
    choices[0].style.display = "block";
    choices.forEach((choice) =>
      choice.addEventListener("click", () => {
        setearInputAFormaDePago(choice);
      }),
    );
  }

  resto = calcularDineroRestante(cuotaSelected);
  setupMonedaWatcher(payCuotaForm, () => resto);

  checkFormValid(validarInputsRellenados(), validarMontoParcial(resto));
  payCuotaForm.querySelectorAll("input").forEach((field) => {
    field.addEventListener("input", () => {
      checkFormValid(validarInputsRellenados(), validarMontoParcial(resto));
    });
  });
}

function actualizarEstadoProximasCuota(cuota, cantidadCuota) {
  const n = parseInt(cuota.split(" ")[1]);
  for (let i = n + 1; i < cantidadCuota; i++) {
    actualizarEstadoCuota("Cuota " + i);
  }
}

function displayMensajePostCuotaPagada(status, message) {
  const bar = document.querySelector(".payCuotaStatus");
  if (!bar) return;
  bar.classList.add("active", status ? "ok" : "failed");
  bar.querySelector("#okPostPagoImg").style.display = status ? "unset" : "none";
  bar.querySelector("#failedPostPagoImg").style.display = status
    ? "none"
    : "unset";
  bar.querySelector(".infoCuotaStatus").textContent = message;

  setTimeout(() => {
    bar.classList.remove("active", "ok", "failed");
  }, 3000);
}

function setearInputAFormaDePago(choice) {
  btnPayCuota.disabled = true;
  btnPayCuota.classList.add("blocked");

  const inputsFormaDePago = payCuotaForm.querySelectorAll(
    ".wrapperChoices > .choice",
  );
  const montoParcialBox = payCuotaForm.querySelector(".pickedAmount");

  inputsFormaDePago.forEach((c) => c.classList.remove("active"));
  payCuotaForm.reset();

  const requiredFields = payCuotaForm.querySelectorAll(
    "input[type='hidden']:not(.notForm):not([name='csrfmiddlewaretoken']), input[type='text']:not(.notForm):not([name='csrfmiddlewaretoken'])",
  );

  clearInputs(requiredFields, payCuotaForm);

  initCustomSingleSelects({
    inputMoneda: "ars",
  });

  choice.classList.add("active");
  choice.children[0].checked = true;

  if (choice.id === "choiceParcial") {
    montoParcialBox.classList.remove("blocked");
    montoParcialBox.children[1].disabled = false;
  } else {
    montoParcialBox.classList.add("blocked");
    montoParcialBox.children[1].disabled = true;
  }
}

function checkFormValid(okInputs, okMontoParcial) {
  if (okInputs && okMontoParcial) {
    btnPayCuota.disabled = false;
    btnPayCuota.classList.remove("blocked");
  } else {
    btnPayCuota.disabled = true;
    btnPayCuota.classList.add("blocked");
  }
}

// Busca la etiqueta visible de un campo para armar el mensaje de "faltan completar"
function getFieldLabel(input) {
  const wrapper = input?.closest(".wrapperInput, .pickedAmount");
  const label = wrapper?.querySelector(".labelInput, label, h4");
  return label ? label.textContent.trim() : input?.name || input?.id || "";
}

function showMissingFieldsMessage(labels) {
  const msgEl = document.getElementById("missingFieldsMsgCuota");
  if (!msgEl) return;
  if (labels.length === 0) {
    msgEl.textContent = "";
    msgEl.classList.remove("active");
  } else {
    msgEl.textContent = "Faltan completar: " + labels.join(", ");
    msgEl.classList.add("active");
  }
}

function validarInputsRellenados() {
  const formaPago = payCuotaForm.querySelector(
    ".typesPayments > .wrapperChoices > .choice.active",
  );

  // 🔒 Guard: si aún no hay opción activa, no validamos
  if (!formaPago) {
    showMissingFieldsMessage([]);
    return false;
  }

  // Cobrador y método de pago son obligatorios siempre: sin esto, el pago
  // queda guardado sin responsable ni método asociado (imposible de arquear).
  const cobradorInput = payCuotaForm.querySelector(".input-cobrador");
  const metodoPagoInput = payCuotaForm.querySelector(".input-metodoPago");
  const amountInput = payCuotaForm.querySelector("#amountParcial");

  const missing = [];
  if (!cobradorInput?.value) missing.push(getFieldLabel(cobradorInput));
  if (!metodoPagoInput?.value) missing.push(getFieldLabel(metodoPagoInput));
  if (formaPago.id === "choiceParcial" && !amountInput?.value) {
    missing.push(getFieldLabel(amountInput));
  }
  showMissingFieldsMessage(missing);

  return missing.length === 0;
}

// ================= Actualizar estado de cuotas en la grilla =================
async function actualizarEstadoCuota(cuota) {
  try {
    const data = await apiFetch("/ventas/detalle_venta/get_specific_cuota/", {
      method: "POST",
      data: { ventaID: ventaID.value, cuota },
    });

    cuotasWrapper.forEach((c) => {
      if (c.id === data["cuota"]) {
        removeSpecificClasses(c);
        removeSpecificClasses(c.children[0]);
        if (c.classList.contains("Vencido")) c.children[2]?.remove();

        if (!data["bloqueada"]) {
          c.classList.add(data["status"]);
          c.children[0].classList.add(data["status"]);
          c.children[0].removeAttribute("style");
        } else {
          c.classList.add("bloqueado");
          c.children[0].classList.add("bloqueado");
          c.children[0].setAttribute("style", data["styleBloqueado"]);
        }
      }
    });
  } catch (err) {
    // Podés mostrar un toast si querés
  }
}

function removeSpecificClasses(el) {
  ["Pendiente", "Pagado", "bloqueado", "Vencido", "Parcial"].forEach((cls) =>
    el.classList.remove(cls),
  );
}

// ================= Modales simples de confirmación → openActionModal =================
function buildConfirmContent({ titulo, mensaje }) {
  return `
    <div class="modalConfirm__content">
      <h2>${titulo}</h2>
      <p>${mensaje}</p>
      <div data-status style="margin-top:.75rem;"></div>
    </div>`;
}

// Solicitar baja de cuota
function solicitudBajaCuota() {
  const ctx = {
    titulo: "Solicitar baja de la cuota",
    mensaje:
      "Se enviara un correo solicitando la cancelación de la cuota. ¿Deseas continuar?",
  };
  openActionModal({
    modalOpts: {
      cssClass: ["modalContainerFilter"],
      closeMethods: ["overlay", "button", "escape"],
    },
    buildContent: () => buildConfirmContent(ctx),
    validate: () => true,
    run: async () => {
      const resp = await apiFetch(solicitudAnulacionCuotaUrl, {
        method: "POST",
        data: { ventaID: ventaID.value, cuota: cuotaID.value },
      });
      if (!resp?.status)
        return {
          ok: false,
          message: resp?.message || "No se pudo solicitar la baja",
        };
      return { ok: true, message: resp.message || "Solicitud enviada" };
    },
    texts: {
      working: "Enviando solicitud...",
      success: "Solicitud enviada",
      error: "Error al enviar",
      canceled: "Cancelado",
    },
    buttons: { confirm: "Solicitar", cancel: "Cancelar" },
  }).then((res) => {
    if (res?.ok)
      showReponseModal(
        res.result?.message || "Solicitud enviada",
        "/static/images/icons/checkMark.png",
      );
  });
}
window.solicitudBajaCuota = solicitudBajaCuota;

// Confirmar anulación definitiva
function anulacionCuota() {
  const ctx = {
    titulo: "Anular cuota",
    mensaje: "¿Estás seguro de anular la cuota?",
  };
  openActionModal({
    modalOpts: {
      cssClass: ["modalContainerFilter"],
      closeMethods: ["overlay", "button", "escape"],
    },
    buildContent: () => buildConfirmContent(ctx),
    validate: () => true,
    run: async () => {
      const resp = await apiFetch(confirmacionAnulacionCuotaUrl, {
        method: "POST",
        data: { ventaID: ventaID.value, cuota: cuotaID.value },
      });
      if (!resp?.status)
        return {
          ok: false,
          message: resp?.message || "No se pudo anular la cuota",
        };

      await actualizarEstadoCuota(cuotaID.value);
      await actualizarEstadoProximasCuota(cuotaID.value, cantidadCuotas);
      cerrarContenedores_formPago_viewDetails();
      return { ok: true, message: resp.message || "Cuota anulada" };
    },
    texts: {
      working: "Anulando...",
      success: "Cuota anulada",
      error: "Error al anular",
      canceled: "Cancelado",
    },
    buttons: { confirm: "Anular", cancel: "Cancelar" },
  }).then((res) => {
    if (res?.ok)
      showReponseModal(
        res.result?.message || "Cuota anulada",
        "/static/images/icons/checkMark.png",
      );
    else if (res?.error) {
      showReponseModal(
        "No se pudo anular",
        "/static/images/icons/error_icon.png",
      );
      console.log(res.error);
    }
  });
}
window.anulacionCuota = anulacionCuota;

// ================= Modal de respuesta genérico =================
function showReponseModal(contenido, icon) {
  const modal = new tingle.modal({
    footer: true,
    closeMethods: ["button", "overlay"],
    cssClass: ["modalResponse"],
    onClose: () => modal.destroy(),
  });

  modal.setContent(`<div class="messageReponseModal">
      <img src="${icon}"/>
      <h2>${contenido}</h2>
    </div>`);

  modal.addFooterBtn(
    "Cerrar",
    "tingle-btn tingle-btn--default button-default-style",
    () => modal.close(),
  );
  modal.open();
}

function cerrarContenedores_formPago_viewDetails() {
  document
    .querySelectorAll(".containerDetalleCuota")
    .forEach((el) => el.classList.remove("active"));
  payCuotaForm.reset();
}

// --- START: Moneda watcher / sync amounts ---
function setupMonedaWatcher(root, getRestFn) {
  const hiddenMoneda = root.querySelector('input.input-moneda');
  const amountInput = root.querySelector("#amountParcial");
  const dineroRestanteEl = root.querySelector("#dineroRestante");

  if (!hiddenMoneda || !amountInput || !dineroRestanteEl) return;

  const readDolar = () => {
    const d = window.dolar_oficial ?? window.dolarOficial ?? 0;
    return Number(d) || 0;
  };

  const formatNumber = (n) => {
    return (Math.round((Number(n) || 0) * 100) / 100).toFixed(2);
  };

  const updateDisplay = () => {
    const moneda = String(hiddenMoneda.value || "ars").toLowerCase();
    const resto =
      typeof getRestFn === "function"
        ? Number(getRestFn())
        : Number(window.resto || 0);
    const dolar = readDolar();

    if (moneda === "usd") {
      const converted = dolar > 0 ? resto / dolar : 0;
      // si el tipo de pago es total, mostramos el monto calculado convertido
      amountInput.value = document.querySelector("#total:checked")
        ? formatNumber(converted)
        : amountInput.value;
      dineroRestanteEl.textContent = `Dinero restante: USD ${formatNumber(converted)}`;
    } else {
      // ARS
      amountInput.value = document.querySelector("#total:checked")
        ? formatNumber(resto)
        : amountInput.value;
      dineroRestanteEl.textContent = `Dinero restante: $ ${formatNumber(resto)}`;
    }
  };

  // actualizo inmediatamente
  updateDisplay();

  // escucho eventos que emite inputSelectOnly.js
  ["input", "change"].forEach((ev) =>
    hiddenMoneda.addEventListener(ev, () => {
      // cuando cambia moneda, limpiar/actualizar amount si es tipo total
      updateDisplay();
    }),
  );

  // Si el usuario cambia el tipo de pago (radio total/parcial), reacciono:
  const radios = root.querySelectorAll('input[name="typePayment"]');
  radios.forEach((r) =>
    r.addEventListener("change", () => {
      // si seleccionaron total, bloquear y rellenar; si parcial, desbloquear
      const isTotal =
        root.querySelector('input[name="typePayment"]:checked')?.value ===
        "total";
      if (isTotal) {
        amountInput.readOnly = true;
      } else {
        amountInput.readOnly = false;
      }
      updateDisplay();
    }),
  );
}
// --- END: Moneda watcher / sync amounts ---
