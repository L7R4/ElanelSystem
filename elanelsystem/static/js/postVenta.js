var url = window.location.pathname;

// Displays items de ventas ---------------------------
function showDetailsVentas() {
    let buttonsDisplaysDetailsVentas = document.querySelectorAll(".displayDetailInfoButton")
    buttonsDisplaysDetailsVentas.forEach(button => {
        button.addEventListener("click",()=>{
            let wrapperDetailInfo = button.parentElement.querySelector(".wrapperDetailInfo")
            let heightDetail = wrapperDetailInfo.scrollHeight
                
            if(wrapperDetailInfo.style.maxHeight === heightDetail+'px'){
                wrapperDetailInfo.style.maxHeight ='0px'
                wrapperDetailInfo.style.height ='0px'
                wrapperDetailInfo.classList.remove("active")
                
            }else{
                wrapperDetailInfo.style.maxHeight = heightDetail+'px'
                wrapperDetailInfo.style.height = heightDetail+'px'
                wrapperDetailInfo.classList.add("active")
            }
    
    
            if(button.children[0].classList.contains("active")){
                button.children[0].classList.remove("active")
            }else{
                button.children[0].classList.add("active")
            }
            
        })
    });
}
showDetailsVentas();

// ----------------------------------------------------


// Fetch POST para auditoria --------------------------

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

async function sendGradeVenta(form){
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
            },
            body: new FormData(form)
        })
        if (!res.ok){
            throw new Error("Error")
        }
        const data = await res.json()
        return data;
    } catch (error) {
    }
}

// ----------------------------------------------------

// Crear form para comentar en auditoria pendiente --------------------------

function formComentario(idVenta,contenedor,grade){
    let venta = contenedor
    let stringForHTML = crearFormSegunEstadoAuditoria(idVenta,false,grade)

    // Limpia otros forms o preForms que estan activado para que solo quede uno form activado
    cleanOtherForms(venta)

    // Crea en el DOM el formulario segun si fue desde una auditoria realizada anteoriormente o no
    if(venta.querySelector(".containerModularForm")){
        let formParent = venta.querySelector(".containerModularForm")
        formParent.insertAdjacentHTML('beforeend', stringForHTML);
    }else{
        venta.insertAdjacentHTML('beforeend', stringForHTML);
    }
    let containerWrapperComentario = document.querySelector(".containerModularForm");

    
    
    // Para cuando se edite una auditoria y se elija el "grado" pueda colocar un background para que de la sensacion de bloqueado
    if(venta.querySelector(".wrapperButtonsGrade")){
        let wrapperEditGrade = venta.querySelector(".wrapperButtonsGrade")
        wrapperEditGrade.classList.add("selectedGrade")
        wrapperEditGrade.insertAdjacentHTML('afterbegin', `<div class="backgroundSelect active"></div>`);
    }else{
        let optionsGrade_inputs = venta.querySelectorAll(".labelInputGrade")
        optionsGrade_inputs.forEach(element => element.classList.add("selected"))
    }
    
    let form = venta.querySelector(".containerModularForm")
    let confirmAuditoria = form.querySelector("#confirmComentario")

    //Envia la auditoria
    confirmAuditoria.addEventListener("click",async()=>{
        
        let data = await sendGradeVenta(form)
        let messageWrapper = crearMensajePostAuditoria(data["status"], data["message"])
        let wrapper_content = document.querySelector(".wrapper_content")
        wrapper_content.insertAdjacentHTML('beforeend', messageWrapper);

        containerWrapperComentario.remove()
        try {venta.querySelector(".wrapperButtonsGrade").remove()}catch(error){}

        // Para cambiar el estado de la venta despues de la auditoria
        let oldStatus = venta.querySelector(".statusPostVenta")
        let padreStatus = oldStatus.parentElement
        venta.querySelector(".statusPostVenta").remove()
        let newStatus = crearNuevoStatusAuditoria(data["grade"])
        padreStatus.insertAdjacentHTML('beforeend', newStatus);

        // SECCION PARA AGREGAR EL NUEVO COMENTARIO -----------------

        // Elimina el tag de 'ultimo' del comentario
        if(venta.querySelector(".wrapperUltimo")){
            venta.querySelector(".wrapperUltimo").remove()
        }

        let wrapperComentarios;
        // Agrega al DOM el nuevo comentario
        if (venta.querySelector(".containerHistorialAuditorias")) {
            wrapperComentarios = venta.querySelector(".containerHistorialAuditorias")
        }else{
            wrapperComentarios = document.createElement('div')
            wrapperComentarios.classList.add("containerHistorialAuditorias")
            venta.querySelector(".wrapperDetailInfo").appendChild(wrapperComentarios)
        }
        let newComentario = crearNuevoComentario(data["comentarioString"],data["fechaString"], data["gradeString"])
        wrapperComentarios.insertAdjacentHTML('beforeend',newComentario)
        
        // Obtiene la altura del elemento a agregar
        let newComentarioNode = venta.querySelector(".wrapperUltimo").parentElement
        let heightNewComentario = newComentarioNode.offsetHeight

        // Obtiene la altura del wrapper que contiene la info detallada
        let valueHeightWrapperComentarios = wrapperComentarios.parentElement.scrollHeight

        // Asiga la nueva altura al wrapper de la info detallada sumando su altura + la del nuevo elemento
        wrapperComentarios.parentElement.style.height =  valueHeightWrapperComentarios + heightNewComentario + "px"

        // Si el wrapper de info detallada esta expandida aumenta su maxHeigth para que se pueda visualizar el nuevo elemento
        if(wrapperComentarios.parentElement.classList.contains("active")){
            wrapperComentarios.parentElement.style.maxHeight =  valueHeightWrapperComentarios + heightNewComentario  + "px" 
        }


        // ------------------------------------------------------------------------------------------------

        if(!venta.querySelector("#editar")){
            venta.querySelector(".buttonsWrapper").remove()
            let newButtonEditar = crearBotonEditar(idVenta)
            padreStatus.insertAdjacentHTML('afterbegin', newButtonEditar);
        }
        try {
            setTimeout(()=>{
                auditoriaMessageWrapper.classList.add("active")
            },"200")
            setTimeout(()=>{
                auditoriaMessageWrapper.classList.remove("active")
            },"3000")
            setTimeout(()=>{
                auditoriaMessageWrapper.remove()
            },"4500")
            
        } catch (error) {
        }

        receibedSells = await requestVentas(sucursalInput.value, inputCampania.value)
    })


    // Cierra el formulario
    let closeForm = venta.querySelector("#cancelarComentario")
    closeForm.addEventListener("click",()=>{
        // Limpia los checks de los inputs 
        let optionsGrade_inputs = venta.querySelectorAll(".labelInputGrade")
        optionsGrade_inputs.forEach(element =>{
            element.previousElementSibling.checked = false
            element.classList.remove("selected") 
        })
        try {
            venta.querySelector(".backgroundSelect").remove()
            venta.querySelector(".wrapperButtonsGrade").classList.remove("selectedGrade")
        } catch (error) { }
        
        containerWrapperComentario.remove()
    })
}




// Crear div para elegir el grado de la auditoria --------------------------

function formEditPostVenta(idVenta,contenedor){
    let venta = contenedor

    // Limpia otros forms o preForms que estan activado para que solo quede uno form activado
    cleanOtherForms(venta)
    let stringForHTML = crearFormSegunEstadoAuditoria(idVenta,true)
    if(document.querySelector(".wrapperButtonsGrade")){
        document.querySelectorAll(".wrapperButtonsGrade").forEach(element => element.remove());
    }
    venta.insertAdjacentHTML('beforeend', stringForHTML);
    let containerWrapperGrade = document.querySelector(".wrapperButtonsGrade");

    let closeGrade = venta.parentElement.querySelector("#cancelarGrade")
    closeGrade.addEventListener("click",()=>{
        containerWrapperGrade.remove()
    })

}

// --------------------------------------------------------------------------



// Form segun si la auditoria ya fue o no hecha ----------------------

function crearFormSegunEstadoAuditoria(idVenta,realizada,grade="") {
    let stringForHTML = "";
    if(realizada){
        stringForHTML =`
        <div class="wrapperButtonsGrade">
            <div class="wrapperMessage">
                <h3>¿Que prefieres hacer?</h3>
            </div>
            <div class="buttonsWrapper">
                <input type="radio" name="grade" id="aprobarI" value="a" form="containerModularForm">
                <label for="aprobarI" id="aprobar"class ="labelInputGrade" onclick="formComentario('${idVenta}',this.offsetParent.parentElement,this.id)">Aprobar</label>
                <input type="radio" name="grade" id="desaprobarI" value="d" form="containerModularForm">
                <label for="desaprobarI" id="desaprobar"class ="labelInputGrade" onclick="formComentario('${idVenta}',this.offsetParent.parentElement,this.id)">Desaprobar</label>
                <button type="button" id="cancelarGrade">Cancelar</button>
            </div>       
        </div>
        `;
    }else{
        stringForHTML =`
        <form method="POST" class="containerModularForm" id="containerModularForm">
            <div class="wrapperFormComentario">
                <input type="hidden" name="idVenta" id="idVenta" value="${idVenta}" readonly>
                <div class="wrapperInputComent">
                    <label for="comentarioInput">Comentario</label>
                    <textarea name="comentarioInput" id="comentarioInput" cols="30" rows="10"></textarea>
                </div>
                <div class="wrapperMessage">
                    <h3>Estas seguro que quieres <span>${grade}</span> esta venta?</h3>
                </div>
                <div class="wrapperButtonsSendItem">
                    <button type="button" id="confirmComentario">Confirmar</button>
                    <button type="button" id="cancelarComentario">Cancelar</button>
                </div>
            </div>
        </form> 
        `;
    }
    return stringForHTML;
}

// ------------------------------------------------------------------

function crearMensajePostAuditoria(status,message){
    if(status){
        stringForHTML =`
            <div id="auditoriaMessageWrapper">
                <h2 id="messageSuccess">${message}</h2>
            </div>
            `;
    }else{
        stringForHTML =`
            <div id="auditoriaMessageWrapper">
                <h2 id="messageError">${message}</h2>
            </div>        
            `;
    }
    return stringForHTML;
}

function crearNuevoStatusAuditoria(grade) {
    let stringForHTML;
    if(grade){
        stringForHTML =`
        <div class="statusPostVenta">                                                    
            <div class="dotStatus aprobada"></div>
            <h3>Auditoria aprobada</h3>             
        </div>`;
    }else{
        stringForHTML =`
        <div class="statusPostVenta">                                                    
            <div class="dotStatus desaprobada"></div>
            <h3>Auditoria desaprobada</h3>             
        </div>`;
    }
    return stringForHTML;
}

function crearBotonEditar(idVenta) {
    stringForHTML =`
    <div class="buttonsWrapper">
        <label for="editarI" id="editar" onclick="formEditPostVenta('${idVenta}',this.offsetParent)">Editar</label>
    </div>`
    return stringForHTML;
}

function crearNuevoComentario(comentario,fecha,grade) {
    let stringForHTML =`
    <div class="infoCheckWrapper">
        <div class="wrapperComentarios">
            <h4>Comentarios</h4>
            <p>${comentario}</p>
        </div>
        <div class="wrapperFechaHora">
            <p>${fecha}</p>
        </div>
        <div class="wrapperGrade">
            <p>${grade}</p>
        </div>
            <div class="wrapperUltimo">
                <p>Último</p>
            </div>
    </div>  
    `;
    return stringForHTML
}


// Limpia otros forms o preForms que estan activado para que solo quede uno form activado
function cleanOtherForms(ventaItem){
    // Verifica si existe otros con esa clase para eliminarlos 
    if(document.querySelector(".containerModularForm") && !ventaItem.querySelector(".containerModularForm")){
        let formWrapper = document.querySelector(".containerModularForm")
        let options_grade = formWrapper.offsetParent.querySelectorAll(".labelInputGrade")
        options_grade.forEach(element =>{
            element.previousElementSibling.checked = false
            element.classList.remove("selected") 
        })
        formWrapper.remove()
    }

    // Verifica si existe otros con esa clase para eliminarlos 
    if(document.querySelector(".wrapperButtonsGrade") && !ventaItem.querySelector(".wrapperButtonsGrade")){
        document.querySelectorAll(".wrapperButtonsGrade").forEach(element => element.remove());
    }
}