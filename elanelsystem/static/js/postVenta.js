var url = window.location.pathname;

// #region Displays items de ventas ---------------------------

// Función reutilizable para alternar la altura y clase de un elemento de detalle
function toggleWrapperDetail(button) {
    let wrapperDetailInfo = button.parentElement.querySelector(".wrapperDetailInfo");
    let heightDetail = wrapperDetailInfo.scrollHeight;

    if (wrapperDetailInfo.style.maxHeight === heightDetail + 'px') {
        wrapperDetailInfo.style.maxHeight = '0px';
        wrapperDetailInfo.style.height = '0px';
        wrapperDetailInfo.classList.remove("active");
    } else {
        wrapperDetailInfo.style.maxHeight = heightDetail + 'px';
        wrapperDetailInfo.style.height = heightDetail + 'px';
        wrapperDetailInfo.classList.add("active");
    }

    if (button.children[0].classList.contains("active")) {
        button.children[0].classList.remove("active");
    } else {
        button.children[0].classList.add("active");
    }
}


function showDetailsVentas() {
    let buttonsDisplaysDetailsVentas = document.querySelectorAll(".displayDetailInfoButton");
    buttonsDisplaysDetailsVentas.forEach(button => {
        button.addEventListener("click", () => {
            toggleWrapperDetail(button);
        });
    });
}
showDetailsVentas();

// #endregion ----------------------------------------------------


//#region Fetch POST para auditoria --------------------------

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

async function sendGradeVenta(form) {
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
            },
            body: new FormData(form)
        })
        if (!res.ok) {
            throw new Error("Error")
        }
        const data = await res.json()
        return data;
    } catch (error) {
    }
}

//#endregion ----------------------------------------------------


function renderFormAuditoria(venta_id) {
    let stringForHTML = `
    <form method="POST" class="containerModularForm" id="containerModularForm">
        ${CSRF_TOKEN}
        <input type="hidden" name="idVenta" id="idVenta" value="${venta_id}" readonly>
        <h2>Selecciona el estado de la auditoria</h2>
        <div class="wrapperButtonsGrade">
            <div class="buttonsWrapper">
                <input type="radio" name="grade" id="aprobarI" value="a">
                <label for="aprobarI" id="aprobarLabel" class="labelInputGrade">Aprobar</label>
                <input type="radio" name="grade" id="desaprobarI" value="d">
                <label for="desaprobarI" id="desaprobarLabel" class="labelInputGrade">Desaprobar</label>
            </div>       
        </div>
        <div class="wrapperFormComentario">
            <div class="wrapperInputComent">
                <label for="comentarioInput">Comentario</label>
                <textarea name="comentarioInput" id="comentarioInput" cols="30" rows="10"></textarea>
            </div>
        </div>
    </form> 
    `;
    return stringForHTML;
}


function refreshVenta(ventaUpdated) {
    const ventaElement = document.getElementById(`v${ventaUpdated["ventaUpdated_id"]}`);

    const statusText_updated = ventaUpdated.statusText;
    const statusIcon_updated = ventaUpdated.statusIcon;
    const auditorias_updated = ventaUpdated.auditorias;

    //#region Actualiza las auditorias
    if (ventaElement.querySelector(".containerHistorialAuditorias")) {
        ventaElement.querySelector(".containerHistorialAuditorias").innerHTML = "";
    } else {
        let containerHistorialAuditorias = `<div class="containerHistorialAuditorias"></div>`;
        ventaElement.querySelector(".wrapperDetailInfo").insertAdjacentHTML("beforeend", containerHistorialAuditorias)
    }

    let stringHTMLAuditorias = ``;
    auditorias_updated.forEach((e, i, array) => {
        stringHTMLAuditorias += `
            <div class="infoCheckWrapper">
                <div class="wrapperComentarios">
                    <h4>Comentarios</h4>
                    <p>${e.comentarios}</p>
                </div>
                <div class="wrapperFechaHora">
                    <p>${e.fecha_hora}</p>
                </div>
                <div class="wrapperGrade">
                    ${e["grade"] ? '<p>Aprobada</p>' : '<p>Desaprobada</p>'}
                </div>
                ${i === array.length - 1 ? '<div class="wrapperUltimo"><p>Último</p></div>' : ""}
            </div>`;
    });

    ventaElement.querySelector(".containerHistorialAuditorias").innerHTML = stringHTMLAuditorias;
    // #endregion


    // #region Actualiza el status
    ventaElement.querySelector(".statusWrapperShortInfo").innerHTML = `
        <img src="${statusIcon_updated}" alt="">
        <p>${statusText_updated}</p>
    `;
    // #endregion


    // #region Actualiza los botones
    ventaElement.querySelector(".buttonsWrapper").innerHTML = `
    <button class="editarButton" onclick="modalForm('v${ventaUpdated["ventaUpdated_id"]}')">Editar</button>
    `;
    // #endregion


}

function modalForm(venta_id) {
    let modal = new tingle.modal({
        footer: true,
        closeMethods: [''],
        cssClass: ['modalContainerAuditar'],

        onOpen: function () {
            enableAuditarButton()
        },
        onClose: function () {
            modal.destroy();
        },
    });

    venta_id_formated = venta_id.slice(1); // Limpia el primer caracter de venta_id
    // set content
    modal.setContent(renderFormAuditoria(venta_id_formated));


    // add a button
    modal.addFooterBtn('Auditar', 'tingle-btn tingle-btn--primary buttonAuditControl', async function () {

        let form = document.querySelector("#containerModularForm")
        showLoader()
        let response = await sendGradeVenta(form)
        console.log(response);

        if (response.status) {
            console.log("Salio todo bien");
            hiddenLoader();
            refreshVenta(response);

            const ventaElement = document.getElementById(venta_id);
            const button = ventaElement.querySelector('.displayDetailInfoButton'); // Ajusta el selector según tu caso
            if (button) toggleWrapperDetail(button);

            modal.close();
            modal.destroy();
        } else {
            console.log("Salio todo mal");
            hiddenLoader();

            modal.close();
            modal.destroy();
        }
        newModalMessage(response["message"], response["iconMessage"]);

    });

    // add another button
    modal.addFooterBtn('Cancelar', 'tingle-btn tingle-btn--default buttonAuditControl', function () {
        modal.close();
        modal.destroy();
    });

    // open modal
    modal.open();

    // Se bloquea hasta que los campos esten todos completos
    document.querySelector(".tingle-btn--primary").disabled = true;
}



// #region Manejar el display del loader
function showLoader() {
    document.querySelector('.modalContainerAuditar').children[0].style.display = "none";
    document.getElementById('wrapperLoader').style.display = 'flex';
}

function hiddenLoader() {
    document.getElementById('wrapperLoader').style.display = 'none';
}
// #endregion


function enableAuditarButton() {
    // Obtener el botón de importar
    const auditarButton = document.querySelector(".tingle-btn--primary");

    // Obtener los inputs que queremos validar
    const inputsGrade = document.querySelectorAll("#containerModularForm > .wrapperButtonsGrade input");


    inputsGrade.forEach(input => {
        input.addEventListener("input", () => {
            auditarButton.disabled = false;  // Habilitar el botón
            auditarButton.classList.remove("disabled")
        });
        // if (input.checked) {

        // } else {
        //     auditarButton.disabled = true;  // Deshabilitar el botón
        //     auditarButton.classList.add("disabled")
        // }

    })
}


function renderMessage(message, iconMessage) {
    return `
        <div id="messageStatusContainer">
            <img src="${iconMessage}" alt="">
            <h2>${message}</h2>
        </div>
    `
}


function newModalMessage(message, iconMessage) {
    let modalMessage = new tingle.modal({
        footer: true,
        closeMethods: ['overlay', 'button', 'escape'],
        cssClass: ['modalContainerMessage'],

    });

    // set content
    modalMessage.setContent(renderMessage(message, iconMessage));


    modalMessage.addFooterBtn('Cerrar', 'tingle-btn tingle-btn--default buttonAuditControl', function () {
        // here goes some logic
        modalMessage.close();
        modalMessage.destroy();
    });

    // open modal
    modalMessage.open();
}