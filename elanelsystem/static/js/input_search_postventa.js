
const inputsFiltersVentas = document.querySelectorAll("input.inputFilterVentas");
const containerListVentas = document.querySelector(".operationsList");

inputsFiltersVentas.forEach(input => {
    input.addEventListener("input", async () => {
        let body = {
            "campania": document.getElementById("inputCampania").value,
            "sucursal": document.getElementById("inputSucursal").value,
            "estado": document.getElementById("inputEstado").value,
            "search": document.getElementById("inputSearch").value
        }
        let response = await formFETCH(body, "/ventas/postventas/filtrar/")
        console.log(response)
        containerListVentas.innerHTML = "";
        response["ventas"].forEach(e => {
            containerListVentas.innerHTML += itemVentaHTML(e.id, e.statusText, e.statusIcon, e.nombre, e.dni, e.nro_operacion, e.fecha, e.tel, e.cod_postal, e.loc, e.prov, e.domic, e.vendedor, e.supervisor, e.auditoria, e.campania)
        })
        showDetailsVentas() // Para recargar los listeners de los botones del detalle de la venta
        realodAmountAuditorias(response["resumen"])
    })
})



// Esto evita el comportamiento predeterminado del botón "Tab" y el "Enter"
document.addEventListener('keydown', function (e) {
    if (e.key === 'Tab' || e.key === 'Enter') {
        e.preventDefault();
    }
});

function itemVentaHTML(id,statusText,statusIcon, nombre, dni, nro_operacion, fecha, tel, cod_postal, loc, prov, domic, vendedor, supervisor, auditoria, campania) {
    let stringHTML = `
    <li class="operationItem">
        <div class="ventaWrapper">
                <div class="statusWrapperShortInfo">
                    <img src="${statusIcon}" alt="">
                    <p>${statusText}</p>
                </div>
                <div class="atributtes">
                    <button type="button" class="displayDetailInfoButton">
                        <img src="${imgNext}" alt="">
                    </button>

                    <div class="wrapperShortInfo">
                        <div class="wrapperInfoAtributte">
                            <h4>Cliente</h4>
                            <h1>${nombre}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>DNI</h4>
                            <h1>${dni}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>Nro Venta</h4>
                            <h1>${nro_operacion}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>Fecha de inscripcion</h4>
                            <h1>${fecha}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>Telefono</h4>
                            <h1>${tel}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>CP</h4>
                            <h1>${cod_postal}</h1>
                        </div>
                    </div>
                    <div class="wrapperDetailInfo">
                        <div class="wrapperInfoAtributte">
                            <h4>Localidad</h4>
                            <h1>${loc}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>Provincia</h4>
                            <h1>${prov}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>Direccion</h4>
                            <h1>${domic}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>Vendedor</h4>
                            <h1>${vendedor}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>Supervisor</h4>
                            <h1>${supervisor}</h1>
                        </div>
                        <div class="wrapperInfoAtributte">
                            <h4>Campaña</h4>
                            <h1>${campania}</h1>
                        </div>`;

    if (auditoria.length > 0 && auditoria[auditoria.length - 1]["realizada"]) {
        stringHTML += `<div class="containerHistorialAuditorias">`;
        auditoria.forEach((e, i, array) => {
            stringHTML += `
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
        stringHTML += `</div></div>`;
    }

    stringHTML += ` 
    <div class="statusWrapper">
        <div class="buttonsWrapper">`;

    if (auditoria.length > 0 && auditoria[auditoria.length - 1]["realizada"]) {
        stringHTML += `<label for="editarI" id="editar" onclick="formEditPostVenta(${id},this.offsetParent)">Editar</label>
        </div>
        <div class="statusPostVenta">`;

        if (auditoria[auditoria.length - 1]["grade"]) {
            stringHTML += `<div class="dotStatus aprobada"></div>
                           <h3>Auditoria aprobada</h3></div>`;
        } else {
            stringHTML += `<div class="dotStatus desaprobada"></div>
                            <h3>Auditoria desaprobada</h3></div>`;
        }

    } else {
        stringHTML += `<input type="radio" name="grade" id="aprobarI" value="a">
        <label for="aprobarI" id="aprobar" class ="labelInputGrade" onclick="formComentario(${id},this.offsetParent.parentElement,this.id)">Aprobar</label>
        <input type="radio" name="grade" id="desaprobarI" value="d">
        <label for="desaprobarI" id="desaprobar" class ="labelInputGrade" onclick="formComentario(${id},this.offsetParent.parentElement,this.id)">Desaprobar</label>
        </div>
        <div class="statusPostVenta">
            <div class="dotStatus pendiente"></div>
            <h3>Auditoria pendiente</h3>
        </div>`;
    }

    stringHTML += `</div>               
            </div>
        </div>
    </li>`;

    return stringHTML;
}

function realodAmountAuditorias(amountAuditoriasDict) {
    pendientesResumen.textContent = amountAuditoriasDict["cant_auditorias_pendientes"]
    realizadasResumen.textContent = amountAuditoriasDict["cant_auditorias_realizadas"]
    aprobadasResumen.textContent = amountAuditoriasDict["cant_auditorias_aprobadas"]
    desaprobadasResumen.textContent = amountAuditoriasDict["cant_auditorias_desaprobadas"]
}


//#region Funcion del formulario FETCH
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
//#endregion  

