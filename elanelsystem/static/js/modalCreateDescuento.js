function renderFormDescuento(item, type, uniqueFechaId) {
    let nombre = item.querySelector(".nombreUser").textContent
    let email = item.querySelector(".emailUser").textContent
    let operationType = type.id == "descuentoButton" ? "descuento" : "premio"

    return `
    <div class="modal_newEgresoIngreso">
      <div class="tittleModal">
          <h3 id="tittleModalEgresoIngreso">
            ${operationType == "descuento" ?
            "Adelanto" :
            "Premio"} 
            a ${nombre}
            </h3>
      </div>

      <form method="POST" class="modal_form" id="formNewDescuento">
        ${csrf_token}
        <input type="hidden" name="usuarioEmail" id="usuarioEmailInput" value="${email}">
        <input type="hidden" name="operationType" id="operationTypeInput" value="${operationType}">
        

          <div class="wrapperInput">
              <h3 class="labelInput">Dinero</h3>
              <input type="number" name="dinero" id="dineroInput" class="input-read-write-default">
          </div>

          <div id="selectWrapperMetodoPago" class="wrapperInput wrapperSelectCustom">
              <h3 class="labelInput">Metodo de Pago</h3>
              <div class="containerInputAndOptions">
                  <img id="tipoMonedaIconDisplay" class="iconDesplegar" src="${imgNext}" alt="">
                  <input type="hidden" name="metodoPago" id="metodoPagoInput" placeholder ="Seleccionar" autocomplete="off">
                  
                  <div class="onlySelect pseudo-input-select-wrapper">
                      <h3></h3>
                  </div>
                  <ul class="list-select-custom options">
                      ${metodosDePago.map(mp => `
                          <li data-value="${mp.id}">${mp.alias}</li>
                      `).join('')}
                  </ul>
              </div>
          </div>

          <div id="selectWrapperCampanias" class="wrapperInput wrapperSelectCustom">
              <h3 class="labelInput">Campaña</h3>
              <div class="containerInputAndOptions">
                  <img id="tipoMonedaIconDisplay" class="iconDesplegar" src="${imgNext}" alt="">
                  <input type="hidden" name="campania" id="campaniaInput" placeholder ="Seleccionar" autocomplete="off">
                  
                  <div class="onlySelect pseudo-input-select-wrapper">
                      <h3></h3>
                  </div>
                  <ul class="list-select-custom options">
                      ${campaniasDisponibles.map(c => `
                          <li data-value="${c}">${c}</li>
                      `).join('')}
                  </ul>
              </div>
          </div>

          <div id="selectWrapperMetodoPago" class="wrapperInput wrapperSelectCustom">
              <h3 class="labelInput">Agencia</h3>
              <div class="containerInputAndOptions">
                  <img id="tipoMonedaIconDisplay" class="iconDesplegar" src="${imgNext}" alt="">
                  <input type="hidden" name="agencia" id="agenciaInput" placeholder ="Seleccionar" autocomplete="off">
                  
                  <div class="onlySelect pseudo-input-select-wrapper">
                      <h3></h3>
                  </div>
                  <ul class="list-select-custom options">
                      ${sucursalesDisponibles.map(sd => `
                          <li data-value="${sd.id}">${sd.pseudonimo}</li>
                      `).join('')}
                  </ul>
              </div>
          </div>

          <div id="selectWrapperEnteRecaudador" class="wrapperInput wrapperSelectCustom">
              <h3 class="labelInput">Ente recaudador</h3>
              <div class="containerInputAndOptions">
                  <img id="tipoMonedaIconDisplay" class="iconDesplegar" src="${imgNext}" alt="">
                  <input type="hidden" name="ente" id="enteInput" placeholder ="Seleccionar" autocomplete="off">
                  
                  <div class="onlySelect pseudo-input-select-wrapper">
                      <h3></h3>
                  </div>
                  <ul class="list-select-custom options">
                      ${ente_recaudadores.map(er => `
                          <li data-value="${er.id}">${er.alias}</li>
                      `).join('')}
                  </ul>
              </div>
          </div>

          <div class="wrapperCalendario wrapperInput wrapperSelectCustom">
                <h3 class="labelInput">Fecha</h3>
                <div class="containerCalendario">
                    <input id="${uniqueFechaId}" name="fecha" class="pseudo-input-select-wrapper inputEgresoIngreso" type="text" placeholder="Seleccionar" readonly />
                </div>
          </div>

          
          <div class="wrapperInput wrapperObservaciones">
            <h3 class="labelInput">Observaciones</h3>
            <textarea name="observaciones" id="observacionesInput" class="input-read-write-default inputEgresoIngreso" rows="10"></textarea>            
          </div>
          
      </form>
    </div>`
}


function newModal(type) {
    var modal = new tingle.modal({
        footer: true,
        closeMethods: ['overlay', 'button', 'escape'],
        cssClass: ['modalNewDescuentoPremio'],
        onOpen: function () {
            initCustomSingleSelects() // Para cargar los listeners de los inputs selects custom
        },

        onClose: function () {
            deleteSingleCalendarTimeDOM()
            modal.destroy();
        },
    });

    // set content
    let uniqueFechaId = 'newFecha_' + Date.now();
    modal.setContent(renderFormDescuento(userSelectedDOM, type, uniqueFechaId));

    initSelectSingleDateWithTime(document.getElementById(`${uniqueFechaId}`));

    // add a button
    modal.addFooterBtn('Confirmar', 'tingle-btn tingle-btn--primary', async function () {
        // here goes some logic

        let body = {
            "usuarioEmail": usuarioEmailInput.value,
            "operationType": operationTypeInput.value,
            "metodoPago": metodoPagoInput.value,
            "dinero": dineroInput.value,
            "campania": campaniaInput.value,
            "agencia": agenciaInput.value,
            "fecha": document.querySelector(".wrapperCalendario input").value,
            "ente_recaudador": enteInput.value,
            "observaciones": observacionesInput.value
        }
        showLoader("modalNewDescuentoPremio")
        let response = await formFETCH(body, urlPostDescuento)
        hiddenLoader();

        if (response.status) {
            console.log("Salio todo bien")
            modal.close();
            modal.destroy();
        }
        else {
            console.log("Salio todo mal")
            modal.close();
            modal.destroy();
        }

        newModalMessage(response.message, response.iconMessage, "modalNewDescuentoPremio");


    });

    // add another button
    modal.addFooterBtn('Cancelar', 'tingle-btn tingle-btn--default', function () {
        // here goes some logic
        modal.close();
        modal.destroy();
    });

    // open modal
    modal.open();
}


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

async function formFETCH(form, url) {
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
            },
            body: JSON.stringify(form)
        })
        if (!res.ok) {
            throw new Error("Error")
        }
        const data = await res.json()
        return data;
    } catch (error) {
    }
}
//#endregion - - - - - - - - - - - - - - -
