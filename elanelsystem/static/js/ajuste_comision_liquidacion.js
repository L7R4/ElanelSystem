function render_form_ajuse_comision(nombre_usuario, comision) {
    return `<form method="POST" class="modal_form" id="formNewAjuste">

            <div class="wrapperTittle">
                <h3 class="labelInput">Ajustar comisiones a ${nombre_usuario} <span>${formatMoney(comision)}</span></h3>
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
                <textarea class="input-read-write-default" name="observaciones" id="observacionesInput" rows="10"></textarea>
            </div>
        </form>`
}

function modal_ajuste_comision(id_usuario, nombre_usuario, comision) {
    let modal = new tingle.modal({
        footer: true,
        closeMethods: [''],
        cssClass: ['moda_container_ajusteComision'],

        onOpen: function () {
            // initCustomSingleSelects()
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
            tipoColaborador: colaboradoresAFiltrar,
            agencia: document.querySelector("#sucursalInput").value,
            total_comisiones: document.querySelector("#totalComisionesInput").value,
        };

        console.log(body)
        showLoader('.moda_container_ajusteComision')
        let response = await fetchFunction(body, '/ventas/liquidaciones/comisiones/nuevo_ajuste/')

        if (response.status) {
            console.log("Salio todo bien");
            update_colaborador(response.user_id, response.user_name, response.new_comision, response.ajuste_sesion)
            update_total_comisiones(response.nuevo_total_comisiones)
        } else {
            console.log("Salio mal")
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


function update_colaborador(colaborador_id, colaborador_nombre, new_comision, nuevos_ajustes) {
    // #1 Cambiamos el valor de la comision en el DOM
    const li = document.querySelector(`ul.values li#idColaborador_${colaborador_id}`);
    if (li) {
        const p = li.querySelector(".wrapperComisionColaborador > p");
        if (p) {
            p.textContent = `$ ${new_comision}`;
        }
    }

    // #2 Cambiamos el boton para ajustar comision del usuario en el DOM
    const button = document.querySelector(`ul.values li#idColaborador_${colaborador_id} button.ajusteComisionButton`);
    if (button) {
        button.setAttribute("onclick", `modal_ajuste_comision(${colaborador_id}, '${colaborador_nombre}', ${new_comision})`);
    }

    // #3 Actualizar los datos del colaborador en itemsColaboradores
    const index = itemsColaboradores.findIndex(c => c.id == colaborador_id);
    if (index !== -1) {
        itemsColaboradores[index].comisionTotal = new_comision;
        itemsColaboradores[index].ajustes_comision = nuevos_ajustes;
    }
}

function update_total_comisiones(new_total) {
    const textTotal = document.querySelector("#dineroTotalComisiones")
    let inputDinero = document.querySelector("#totalComisionesInput");


    const dineroFormateado = new Intl.NumberFormat("es-AR").format(new_total);
    textTotal.textContent = dineroFormateado
    inputDinero.value = new_total
}
