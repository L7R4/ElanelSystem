let formNewMov;

function templateFormIngreso(uniqueFechaId) {
  return `
        <h2 class="tittleModal">Añadir ingreso</h2>
        
        <form method="POST" class="modal_form" id="formNewMov">
            ${CSRF_TOKEN}
            <input name="movimiento" id="typeMov" type="hidden" value="ingreso">

            <div id="selectWrapperSelectTypeTicket" class="wrapperInput wrapperSelectCustom">
                <h3 class="labelInput">Tipo de Comprobante</h3>
                <div class="containerInputAndOptions">
                    <img id="tipoComprobanteIconDisplay"class="iconDesplegar" src="${imgNext}" alt="">
                    <input type="hidden" name="tipoComprobante" id="tipoComprobante" placeholder ="Seleccionar" autocomplete="off">
                    <div class="onlySelect pseudo-input-select-wrapper">
                        <h3></h3>
                    </div>
                    <ul class="list-select-custom options">
                        <li data-value="A">A</li>
                        <li data-value="B">B</li>
                        <li data-value="C">C</li>
                        <li data-value="TK">TK</li>
                        <li data-value="X">X</li>
                        <li data-value="RC">RC</li>
                    </ul>
                </div>
            </div>

            <div class="wrapperInput">
                <h3 class="labelInput" >N° de comprobante</h3>
                <input name="nroComprobante" id="nroComprobanteMov" class="input-read-write-default inputEgresoIngreso">
            </div>

            <div id="selectWrapperSelectTypeID" class="wrapperInput wrapperSelectCustom">
                <h3 class="labelInput">Tipo de Identificacion</h3>
                <div class="containerInputAndOptions">
                    <img id="tipoIDIconDisplay" class="iconDesplegar" src="${imgNext}" alt="">
                    <input type="hidden" name="tipoID" id="tipoID" placeholder ="Seleccionar" autocomplete="off">
                    <div class="onlySelect pseudo-input-select-wrapper">
                        <h3></h3>
                    </div>
                    
                    <ul class="list-select-custom options">
                          <li data-value="DNI">DNI</li>
                          <li data-value="CUIT">CUIT</li>
                          <li data-value="Legajo">Legajo</li>
                          <li data-value="Otro">Otro</li>
                    </ul>
                </div>
            </div>

            <div class="wrapperInput">
                <h3 class="labelInput">N° de Identificacion</h3>
                <input name="nroIdentificacion" id="nroIdentificacionMov" class="input-read-write-default">
            </div>

            <div class="wrapperInput">
                <h3 class="labelInput">Denominacion</h3>
                <input name="denominacion" id="denominacionMov" class="input-read-write-default">
            </div>

            <div id="selectWrapperSelectTypeMoneda" class="wrapperInput wrapperSelectCustom">
                <h3 class="labelInput">Tipo de moneda</h3>
                <div class="containerInputAndOptions">
                    <img id="tipoMonedaIconDisplay" class="iconDesplegar" src="${imgNext}" alt="">
                    <input type="hidden" name="tipoMoneda" id="tipoMoneda" placeholder ="Seleccionar" autocomplete="off">
                    <div class="onlySelect pseudo-input-select-wrapper">
                        <h3></h3>
                    </div>
                    <ul class="list-select-custom options">
                        <li data-value="ARS">ARS</li>
                        <li data-value="USD">USD</li>
                    </ul>
                </div>
            </div>

            <div id="selectWrapperAgencia" class="wrapperInput wrapperSelectCustom">
                <h3 class="labelInput">Agencia</h3>
                <div class="containerInputAndOptions">
                    <img id="tipoMonedaIconDisplay" class="iconDesplegar" src="${imgNext}" alt="">
                    <input type="hidden" name="agencia" id="agencia" placeholder ="Seleccionar" autocomplete="off">
                    
                    <div class="onlySelect pseudo-input-select-wrapper">
                        <h3></h3>
                    </div>
                    <ul class="list-select-custom options">
                        ${agencias
                          .map(
                            (ag) => `
                            <li data-value="${ag.id}">${ag.pseudonimo}</li>
                        `,
                          )
                          .join("")}
                    </ul>
                </div>
            </div>

            <div class="wrapperInput">
                <h3 class="labelInput">Importe</h3>
                <input name="dinero" id="dineroMov" class="input-read-write-default">
            </div>

            <div id="selectWrapperSelectTypePayments" class="wrapperInput wrapperSelectCustom">
                <h3 class="labelInput">Tipo de pago</h3>
                <div class="containerInputAndOptions">
                    <img id="tipoPagoIconDisplay"class="iconDesplegar" src="${imgNext}" alt="">
                    <input type="hidden" name="tipoPago" id="tipoDePago" placeholder="Seleccionar" autocomplete="off">
                    <div class="onlySelect pseudo-input-select-wrapper">
                        <h3></h3>
                    </div>
                  <ul class="list-select-custom options">
                        ${metodos_de_pago
                          .map(
                            (mp) => `
                            <li data-value="${mp.id}">${mp.nombre}</li>
                        `,
                          )
                          .join("")}
                  </ul>
                </div>
            </div>

            <div class="wrapperCalendario wrapperInput wrapperSelectCustom">
                <h3 class="labelInput">Fecha de emicion</h3>
                <div class="containerCalendario">
                    <input id="${uniqueFechaId}" name="fecha" class="pseudo-input-select-wrapper inputEgresoIngreso" type="text" placeholder="Seleccionar" readonly />
                </div>
            </div>

            <div id="selectWrapperSelectEnte" class="wrapperInput wrapperSelectCustom">
                <h3 class="labelInput">Ente recaudador</h3>
                <div class="containerInputAndOptions">
                    <img class="iconDesplegar" src="${imgNext}" alt="">
                    <input type="hidden" name="ente" id="enteMov" placeholder="Seleccionar" autocomplete="off">
                    
                    <div class="onlySelect pseudo-input-select-wrapper">
                        <h3></h3>
                    </div>
                    <ul class="list-select-custom options">
                        ${cuentas_de_cobro
                          .map(
                            (cc) => `
                            <li data-value="${cc.id}">${cc.nombre}</li>
                        `,
                          )
                          .join("")}       
                    </ul>
                </div>
            </div>

            <div id="selectWrapperSelectCampania" class="wrapperInput wrapperSelectCustom">
                <h3 class="labelInput">Campaña</h3>
                <div class="containerInputAndOptions">
                    <img class="iconDesplegar" src="${imgNext}" alt="">
                    <input type="hidden" name="campania" id="campaniaMov" placeholder="Seleccionar" autocomplete="off">
                    
                    <div class="onlySelect pseudo-input-select-wrapper">
                        <h3></h3>
                    </div>
                    <ul class="list-select-custom options">
                        ${campaniasDisponibles
                          .map(
                            (c) => `
                            <li data-value="${c}">${c}</li>
                        `,
                          )
                          .join("")}       
                    </ul>
                </div>
            </div>

            <div class="wrapperInput">
                <h3 class="labelInput">Concepto</h3>
                <input name="concepto" id="conceptoMov" class="input-read-write-default inputEgresoIngreso">
            </div>
        </form>
    `;
}

function templateFormEgreso(uniqueFechaId) {
  return `
        <h2 class="tittleModal">Añadir egreso</h2>

        <form method="POST" class="modal_form" id="formNewMov">
            ${CSRF_TOKEN}
            <input name="movimiento" id="typeMov" type="hidden" value="egreso">

            <div id="selectWrapperSelectTypeTicket" class="wrapperInput wrapperSelectCustom">
                <h3 class="labelInput">Tipo de Comprobante</h3>
                <div class="containerInputAndOptions">
                    <img id="tipoComprobanteIconDisplay"class="iconDesplegar" src="${imgNext}" alt="">
                    <input type="hidden" name="tipoComprobante" id="tipoComprobante" placeholder ="Seleccionar" autocomplete="off">
                    <div class="onlySelect pseudo-input-select-wrapper">
                        <h3></h3>
                    </div>
                    <ul class="list-select-custom options">
                        <li data-value="A">A</li>
                        <li data-value="B">B</li>
                        <li data-value="C">C</li>
                        <li data-value="TK">TK</li>
                        <li data-value="X">X</li>
                        <li data-value="RC">RC</li>
                    </ul>
                </div>
            </div>

            <div class="wrapperInput">
                <h3 class="labelInput" >N° de comprobante</h3>
                <input name="nroComprobante" id="nroComprobanteMov" class="input-read-write-default inputEgresoIngreso">
            </div>

            <div id="selectWrapperSelectTypeID" class="wrapperInput wrapperSelectCustom">
                <h3 class="labelInput">Tipo de Identificacion</h3>
                <div class="containerInputAndOptions">
                    <img id="tipoIDIconDisplay" class="iconDesplegar" src="${imgNext}" alt="">
                    <input type="hidden" name="tipoID" id="tipoID" placeholder ="Seleccionar" autocomplete="off">
                    <div class="onlySelect pseudo-input-select-wrapper">
                        <h3></h3>
                    </div>
                    
                    <ul class="list-select-custom options">
                          <li data-value="DNI">DNI</li>
                          <li data-value="CUIT">CUIT</li>
                          <li data-value="Legajo">Legajo</li>
                          <li data-value="Otro">Otro</li>
                    </ul>
                </div>
            </div>

            <div class="wrapperInput">
                <h3 class="labelInput">N° de Identificacion</h3>
                <input name="nroIdentificacion" id="nroIdentificacionMov" class="input-read-write-default">
            </div>

            <div class="wrapperInput">
                <h3 class="labelInput">Denominacion</h3>
                <input name="denominacion" id="denominacionMov" class="input-read-write-default">
            </div>

            <div id="selectWrapperAgencia" class="wrapperInput wrapperSelectCustom">
                <h3 class="labelInput">Agencia</h3>
                <div class="containerInputAndOptions">
                    <img id="tipoMonedaIconDisplay" class="iconDesplegar" src="${imgNext}" alt="">
                    <input type="hidden" name="agencia" id="agencia" placeholder ="Seleccionar" autocomplete="off">
                    
                    <div class="onlySelect pseudo-input-select-wrapper">
                        <h3></h3>
                    </div>
                    <ul class="list-select-custom options">
                        ${agencias
                          .map(
                            (ag) => `
                            <li data-value="${ag.id}">${ag.pseudonimo}</li>
                        `,
                          )
                          .join("")}
                    </ul>
                </div>
            </div>

            <div class="wrapperInput">
                <h3 class="labelInput">Importe</h3>
                <input name="dinero" id="dineroMov" class="input-read-write-default">
            </div>

            <div id="selectWrapperSelectTypePayments" class="wrapperInput wrapperSelectCustom">
                <h3 class="labelInput">Tipo de pago</h3>
                <div class="containerInputAndOptions">
                    <img id="tipoPagoIconDisplay"class="iconDesplegar" src="${imgNext}" alt="">
                    <input type="hidden" name="tipoPago" id="tipoDePago" placeholder="Seleccionar" autocomplete="off">
                    <div class="onlySelect pseudo-input-select-wrapper">
                        <h3></h3>
                    </div>
                  <ul class="list-select-custom options">
                        ${metodos_de_pago
                          .map(
                            (mp) => `
                            <li data-value="${mp.id}">${mp.nombre}</li>
                        `,
                          )
                          .join("")}
                  </ul>
                </div>
            </div>

            <div class="wrapperCalendario wrapperInput wrapperSelectCustom">
                <h3 class="labelInput">Fecha de emicion</h3>
                <div class="containerCalendario">
                    <input id="${uniqueFechaId}" name="fecha" class="pseudo-input-select-wrapper inputEgresoIngreso" type="text" placeholder="Seleccionar" readonly />
                </div>
            </div>

            <div id="selectWrapperSelectEnte" class="wrapperInput wrapperSelectCustom">
                <h3 class="labelInput">Ente recaudador</h3>
                <div class="containerInputAndOptions">
                    <img class="iconDesplegar" src="${imgNext}" alt="">
                    <input type="hidden" name="ente" id="enteMov" placeholder="Seleccionar" autocomplete="off">
                    
                    <div class="onlySelect pseudo-input-select-wrapper">
                        <h3></h3>
                    </div>
                    <ul class="list-select-custom options">
                        ${cuentas_de_cobro
                          .map(
                            (cc) => `
                            <li data-value="${cc.id}">${cc.nombre}</li>
                        `,
                          )
                          .join("")}       
                    </ul>
                </div>
            </div>
            
            <div id="selectWrapperSelectCampania" class="wrapperInput wrapperSelectCustom">
                <h3 class="labelInput">Campaña</h3>
                <div class="containerInputAndOptions">
                    <img class="iconDesplegar" src="${imgNext}" alt="">
                    <input type="hidden" name="campania" id="campaniaMov" placeholder="Seleccionar" autocomplete="off">
                    
                    <div class="onlySelect pseudo-input-select-wrapper">
                        <h3></h3>
                    </div>
                    <ul class="list-select-custom options">
                        ${campaniasDisponibles
                          .map(
                            (c) => `
                            <li data-value="${c}">${c}</li>
                        `,
                          )
                          .join("")}       
                    </ul>
                </div>
            </div>

            <div class="wrapperInput">
                <h3 class="labelInput">Concepto</h3>
                <input name="concepto" id="conceptoMov" class="input-read-write-default inputEgresoIngreso">
            </div>
        </form>
    `;
}

function modalNewMov(typeMov) {
  let modal = new tingle.modal({
    footer: true,
    closeMethods: ["button", "escape"],
    cssClass: ["modalContainerFilter"],

    onOpen: function () {
      initCustomSingleSelects();
    },
    onClose: function () {
      deleteSingleCalendarTimeDOM();
      modal.destroy();
    },
  });

  let uniqueFechaId = "newFecha_" + Date.now();
  template =
    typeMov == "egreso"
      ? templateFormEgreso(uniqueFechaId)
      : templateFormIngreso(uniqueFechaId);
  modal.setContent(template);

  initSelectSingleDateWithTime(document.getElementById(`${uniqueFechaId}`));

  // add a button
  modal.addFooterBtn(
    "Guardar",
    "tingle-btn tingle-btn--primary add-button-default",
    async function () {
      formNewMov = document.getElementById("formNewMov");
      let response = await makeMov();
      if (response.status) {
        console.log("Salio todo bien");
        try {
          window.dispatchEvent(new CustomEvent("caja:reload"));
        } catch (e) {}
        modal.close();
        modal.destroy();
      } else {
        console.log("Salio todo mal");
        // hiddenLoader();
        modal.close();
        modal.destroy();
      }
    },
  );

  // add another button
  modal.addFooterBtn(
    "Cancelar",
    "tingle-btn tingle-btn--default button-default-style",
    function () {
      modal.close();
      modal.destroy();
    },
  );

  // open modal
  modal.open();
}

// Permite abrir el modal desde la nueva tabla (caja_table.js)
document.addEventListener("caja:new-ingreso", function () {
  modalNewMov("ingreso");
});

document.addEventListener("caja:new-egreso", function () {
  modalNewMov("egreso");
});

//#region ENVIA EL FORMULARIO DEL MOVIMIENTO ----------------------------------------------------------------------------

async function makeMov() {
  let newMov = await fetch("/create_new_mov/", {
    method: "POST",
    body: new FormData(formNewMov),
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
    },
  });
  let data = await newMov.json();
  return data;
}

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
//#endregion -----------------------------------------------------------------------------------------------------------------
