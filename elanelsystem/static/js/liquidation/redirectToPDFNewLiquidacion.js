let confirmNewAuditoria = document.getElementById("liquidarButton");
let urlLiquidacion = window.location.pathname
// const form_create_user = document.getElementById("form_create_user")

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

async function fetchCRUD(body, url) {
    try {
        let response = await fetch(url, {
            method: "POST",
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

function newModalLiquidacion() {
    let modal = new tingle.modal({
        footer: true,
        closeMethods: [''],
        cssClass: ['modalContainerMsj'],

        // onOpen: function () {
        // },
        onClose: function () {
            modal.destroy();
        },
    });

    // set content
    modal.setContent(renderTextSure());


    // add a button
    modal.addFooterBtn('Liquidar', 'tingle-btn tingle-btn--primary add-button-default', async function () {

        const body = {
            "campania": document.querySelector("#campaniaInput").value,
            "agencia": document.querySelector("#sucursalInput").value,
        }

        showLoader('.modalContainerMsj')
        let response = await fetchCRUD(body, urlLiquidacion)

        if (response.status === true) {
            hiddenLoader();
            modal.close();
            modal.destroy();
            window.open(response["urlPDF"], "_blank");
            window.location.href = response["urlRedirect"];
        } else if (response.status === "requiere_confirmacion") {
            hiddenLoader();
            modal.close();
            modal.destroy();
            newModalReliquidacion(response.version_actual, response.fecha_original);
        } else {
            hiddenLoader();
            modal.close();
            modal.destroy();
            newModalMessage(response.message, response.iconMessage);
        }

    });

    // add another button
    modal.addFooterBtn('Cancelar', 'tingle-btn tingle-btn--default button-default-style', function () {
        modal.close();
        modal.destroy();
    });

    // open modal
    modal.open();


}

//#region Manejar el display del loader
function showLoader(container) {
    document.querySelector(container).children[0].style.display = "none";
    document.getElementById('wrapperLoader').style.display = 'flex';
}

function hiddenLoader() {
    document.getElementById('wrapperLoader').style.display = 'none';
}
//#endregion

function newModalMessage(message, iconMessage) {
    let modalMessage = new tingle.modal({
        footer: true,
        closeMethods: ['overlay', 'button', 'escape'],
        cssClass: ['modalContainerMessage'],

    });

    // set content
    modalMessage.setContent(renderMessage(message, iconMessage));


    modalMessage.addFooterBtn('Cerrar', 'tingle-btn tingle-btn--default button-default-style', function () {
        // here goes some logic
        modalMessage.close();
        modalMessage.destroy();
    });

    // open modal
    modalMessage.open();
}


function renderTextSure() {
    return `
    <div id="containerMessageSure">
        <h2>¿Estas seguro que quieres liquidar?</h2>
    </div>
    `
}

function newModalReliquidacion(versionActual, fechaOriginal) {
    let modal = new tingle.modal({
        footer: true,
        closeMethods: ['overlay', 'button', 'escape'],
        cssClass: ['modalContainerMsj'],
        onClose: function () { modal.destroy(); },
    });

    modal.setContent(`
        <div id="containerMessageSure">
            <h2>⚠️ Ya existe la versión ${versionActual} cerrada el ${fechaOriginal}</h2>
            <p>¿Querés crear una reliquidación (versión ${versionActual + 1})?<br>
            Se usará la configuración vigente para esa campaña.</p>
            <label style="display:block;margin-top:12px;font-weight:600">Motivo de la reliquidación *</label>
            <textarea id="motivoReliquidacion" rows="3" style="width:100%;margin-top:6px;padding:8px;border:1px solid #ccc;border-radius:4px"
                placeholder="Ej: Corrección de cuota, error en datos..."></textarea>
        </div>
    `);

    modal.addFooterBtn('Confirmar reliquidación', 'tingle-btn tingle-btn--primary add-button-default', async function () {
        const motivo = document.getElementById('motivoReliquidacion').value.trim();
        if (!motivo) {
            alert('El motivo es obligatorio para reliquidar.');
            return;
        }

        const body = {
            "campania": document.querySelector("#campaniaInput").value,
            "agencia": document.querySelector("#sucursalInput").value,
            "confirmar_reliquidacion": true,
            "motivo_reliquidacion": motivo,
        }

        showLoader('.modalContainerMsj')
        let response = await fetchCRUD(body, urlLiquidacion)

        if (response.status === true) {
            hiddenLoader();
            modal.close();
            modal.destroy();
            window.open(response["urlPDF"], "_blank");
            window.location.href = response["urlRedirect"];
        } else {
            hiddenLoader();
            modal.close();
            modal.destroy();
            newModalMessage(response.message, response.iconMessage);
        }
    });

    modal.addFooterBtn('Cancelar', 'tingle-btn tingle-btn--default button-default-style', function () {
        modal.close();
        modal.destroy();
    });

    modal.open();
}

function renderMessage(message, iconMessage) {
    return `
        <div id="messageStatusContainer">
            <img src="${iconMessage}" alt="">
            <h2>${message}</h2>
        </div>
    `
}