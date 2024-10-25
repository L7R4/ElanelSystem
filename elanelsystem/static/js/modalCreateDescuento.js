function renderFormDescuento(item,type){
    let nombre = item.querySelector(".nombreUser").textContent
    let email = item.querySelector(".emailUser").textContent
    let operationType = type.id == "descuentoButton" ? "Descuento" : "Premio"
    
    return `
    <div class="modal_newEgresoIngreso">
      <div class="tittleModal">
          <h3 id="tittleModalEgresoIngreso">${operationType} a ${nombre}</h3>
      </div>

      <form method="POST" class="modal_form" id="formNewDescuento">
        ${csrf_token}
        <input type="hidden" name="usuarioEmail" id="usuarioEmailInput" value="${email}">
        <input type="hidden" name="operationType" id="operationTypeInput" value="${operationType}">
        

          <div class="wrapperInput">
              <h3 class="labelInput">Dinero</h3>
              <input name="dinero" id="dineroInput" class="input-read-write-default">
          </div>

          <div id="selectWrapperSelectTypePayments" class="wrapperInput">
              <h3 class="labelInput">Metodo de pago</h3>
              <div class="containerInputAndOptions">
                <img id="tipoPagoIconDisplay" class="iconDesplegar" src="{% static 'images/icons/arrowDown.png' %}" alt="">
                <input type="text" name="metodoPago" class="onlySelect input-select-custom " id="metodoPagoInput" placeholder="Seleccionar" autocomplete="off" readonly="">
                <ul class="list-select-custom options">
                    <li data-value="Efectivo">Efectivo</li>
                    <li data-value="Banco">Banco</li>
                    <li data-value="Transferencia">Transferencia</li>
                </ul>
              </div>
          </div>

          <div class="wrapperInput">
              <h3 class="labelInput">Fecha</h3>
              <input name="fecha" id="fechaInput" class="input-read-only-default inputEgresoIngreso">
          </div>

          <div id="selectWrapperSelectCampania" class="wrapperInput">
              <h3 class="labelInput">Campaña</h3>

              <div class="containerInputAndOptions">
                  <img class="iconDesplegar" src="{% static 'images/icons/arrowDown.png' %}" alt="">
                  <input type="text" name="campania" id="campaniaInput" class="input-select-custom onlySelect" placeholder="Seleccionar" autocomplete="off" readonly="">
                  <ul class="list-select-custom options">
                    ${campaniasDisponibles.map(item => `
                        <li>${item}</li>
                    `).join('')}   
                  </ul>
              </div>
          </div>

          
          <div class="wrapperInput">
            <h3 class="labelInput">Concepto</h3>
            <input name="concepto" id="conceptoInput" class="input-read-write-default inputEgresoIngreso">
          </div>
          
      </form>
    </div>`
}


function newModal(type){
    var modal = new tingle.modal({
        footer: true,
        closeMethods: ['overlay', 'button', 'escape'],
        cssClass: ['custom-class-1', 'custom-class-2'],
        onOpen: function() {
            cargarListenersEnInputs() // Para cargar los listeners de los inputs selects custom
        },
        // onClose: function() {
        //     console.log('modal closed');
        // },
        beforeClose: function() {
            // here's goes some logic
            // e.g. save content before closing the modal
            return true;
            
        }
    });
    
    // set content
    modal.setContent(renderFormDescuento(itemDOMSelected,type));
    
    // add a button
    modal.addFooterBtn('Confirmar', 'tingle-btn tingle-btn--primary', async function() {
        // here goes some logic
        
        let body = {
            "usuarioEmail": usuarioEmailInput.value,
            "operationType": operationTypeInput.value,
            "metodoPago": metodoPagoInput.value,
            "dinero": dineroInput.value,
            "campania": campaniaInput.value,
            "fecha": fechaInput.value,
            "concepto": conceptoInput.value
        }
        let response = await fetchFunction(body,urlPostDescuento)
        if(response.status){
            console.log("Salio todo bien")
            modal.close();
            modal.destroy();
        }
        else{
            console.log("Salio todo mal")
            modal.close();
            modal.destroy();
        }

    });
    
    // add another button
    modal.addFooterBtn('Cancelar', 'tingle-btn tingle-btn--default', function() {
        // here goes some logic
        modal.close();
        modal.destroy();
    });
    
    // open modal
    modal.open();
}
// close modal
// modal.close();

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
