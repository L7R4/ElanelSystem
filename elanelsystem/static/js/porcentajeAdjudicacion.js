if (document.querySelector('#wrapperPorcetajeAReconocer')) {
    let inputWrapper = document.querySelector('#wrapperPorcetajeAReconocer');

    const menuHtml = `
    <div class="wrapperEdicionPorcentaje">
        <div class="wrapperButton">
            <button type="button" class="add-button-default" onclick ="editarProcentaje(this)" id="editarProcentajeButton">Editar porcentaje</button>
        </div>

        <div class="wrapperFormAutorizacion">
            <label for="inputAutorizacion">Autorizado por</label>
            <input type="text" class="input-read-write-default" required id="inputAutorizacion">
            <div class="wrapperButtons">
                <button type="button" class="add-button-default" onclick ="guardarAutorizado()" id="guardarAutorizado">Guardar</button>
                <button id="cancelarAutorizado" onclick ="cancelarAutorizado()" class="delete-button-default">Cancelar</button>
            </div> 
        </div>
    </div> 
    `;

    createContextMenu(menuHtml, inputWrapper);



}

function editarProcentaje(element) {
    document.querySelector('.wrapperFormAutorizacion').style.display = 'block';
    element.style.display = 'none';
}

function guardarAutorizado() {
    let autorizadoInput = document.querySelector("#inputAutorizacion");
    document.querySelector("#id_autorizado_por").value = autorizadoInput.value;
    document.querySelector('.wrapperEdicionPorcentaje').style.display = 'none';
    autorizadoInput.value = "";
    document.querySelector("#id_porcentaje_a_reconocer").classList.remove("not_ed");
}

function cancelarAutorizado() {
    let autorizadoInput = document.querySelector("#inputAutorizacion");
    document.querySelector('.context-menu').style.display = 'none';
    autorizadoInput.value = "";
}

