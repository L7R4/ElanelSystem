function render_form_ajuse_comision(nombre_usuario) {
    return `<form method="POST" class="modal_form" id="formNewMov">

            <div class="wrapperTittle">
                <h3 class="labelInput">Ajustar comisiones a ${nombre_usuario}</h3>
            </div>
            ${CSRF_TOKEN}

            <div class="wrapperInput">
                <h3 class="labelInput">Dinero</h3>
                <input type="number" name="dinero" id="dineroAjusteInput" class="input-read-write-default">
            </div>
            <div class="wrapperInputObservaciones">
                <label for="observacionesInput">Observaciones</label>
                <textarea name="observaciones" id="observacionesInput" cols="30" rows="10"></textarea>
            </div>
        </form>`
}

function modal_ajuste_comision(id_usuario, nombre_usuario){
    let modal = new tingle.modal({
        footer: true,
        closeMethods: [''],
        cssClass: ['moda_container_ajusteComision'],

        onOpen: function () {
            initCustomSingleSelects()
        },

        onClose: function () {
            modal.destroy();
        },
    });
    console.log(id_usuario, nombre_usuario)


    // set content
    modal.setContent(render_form_ajuse_comision(nombre_usuario));


    // add a button
    modal.addFooterBtn('Guardar', 'tingle-btn tingle-btn--primary', async function () {

        body = {
            "campania": document.querySelector("#campaniaInput").value,
            "agencia": document.querySelector("#sucursalInput").value,
        }
        console.log(body)
        // showLoader()
        // let response = await fetchCRUD(body, urlLiquidacion)

        // if (response.status) {
        //     console.log("Salio todo bien");
        //     hiddenLoader();
        //     modal.close();
        //     modal.destroy();
        // }else{
        //     console.log("Salio mal")
        //     hiddenLoader()
        //     modal.close();
        //     modal.destroy();
        // }
    });

    modal.addFooterBtn('Cancelar', 'tingle-btn tingle-btn--default', function () {
        modal.close();
        modal.destroy();
    });

    modal.open();
}

function update_comision_colaborador(colaborador){
    itemsColaboradores.forEach(c => {
        if(c.id == colaborador.id){
            let comisionColaborador = c.querySelector(".wrapperComisionColaborador > p")
            comisionColaborador.textContent = `$ ${colaborador.new_comision}`
            return
        }
    });
}