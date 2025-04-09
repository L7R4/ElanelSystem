function render_form_ajuse_comision(nombre_usuario, comision) {
    return `<form method="POST" class="modal_form" id="formNewAjuste">

            <div class="wrapperTittle">
                <h3 class="labelInput">Ajustar comisiones a <span>${nombre_usuario} ($${comision})</span></h3>
            </div>

            <div class="wrapperButtonsSelectTipoAjuste">
                <div>
                    <input type="radio" name="ajuste" id="ajustePositivoInput" value="positivo" class="inputSelectTipoColaborador">
                    <label for="ajustePositivoInput">Ajuste positivo</label>
                </div>
                <div>
                    <input type="radio" name="ajuste" id="ajusteNegativoInput" value="negativo" class="inputSelectTipoColaborador">
                    <label for="ajusteNegativoInput">Ajuste negativo</label>
                </div>
            </div>
            ${CSRF_TOKEN}
            <div class="wrapperInputDinero">
                <h3 class="labelInput">Dinero</h3>
                <input type="number" name="dinero" id="dineroAjusteInput" class="input-read-write-default">
            </div>
            <div class="wrapperInputObservaciones">
                <h3>Observaciones</h3>
                <textarea name="observaciones" id="observacionesInput" rows="10"></textarea>
            </div>
        </form>`
}

function modal_ajuste_comision(id_usuario, nombre_usuario,comision){
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
    modal.setContent(render_form_ajuse_comision(nombre_usuario, comision));


    // add a button
    modal.addFooterBtn('Guardar', 'tingle-btn tingle-btn--primary add-button-default', async function () {

        const body = {
            user_id: id_usuario,
            ajuste: document.querySelector('input[name="ajuste"]:checked').value,
            dinero: document.getElementById("dineroAjusteInput").value,
            observaciones: document.getElementById("observacionesInput").value,
            campania: document.querySelector("#campaniaInput").value,
            agencia: document.querySelector("#sucursalInput").value,
        };
        
        console.log(body)
        showLoader('.moda_container_ajusteComision')
        let response = await fetchFunction(body, '/ventas/liquidaciones/comisiones/nuevo_ajuste/')
        
        if (response.status) {
            console.log("Salio todo bien");
            // update_comision_colaborador(user_id, )
        }else{
            console.log("Salio mal")
            // hiddenLoader()
        }
        
        hiddenLoader();
        modal.close();
        modal.destroy();
    });

    modal.addFooterBtn('Cancelar', 'tingle-btn tingle-btn--default button-default-style', function () {
        modal.close();
        modal.destroy();
    });

    modal.open();
}
function update_comision_colaborador(colaborador_id, new_comision){
    let comisionColaborador = c.querySelector(".wrapperComisionColaborador > p")

    itemsColaboradores.forEach(c => {
        if(c.id == colaborador_id){
            let comisionColaborador = c.querySelector(".wrapperComisionColaborador > p")
            comisionColaborador.textContent = `$ ${new_comision}`
            return
        }
    });
}