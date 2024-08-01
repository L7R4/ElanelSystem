let buttonShowDeleteWrapper = document.getElementById("showDeleteWrapper");
let wrapperFormDeleteSale = document.querySelector(".wrapperFormDeleteSale");
let buttonConfirmDelete = document.getElementById("confirmDelete");
let buttonNotConfirmDelete = document.getElementById("notConfirmDelete");
let input_confirm_delete = document.getElementById("input_confirm_delete");
let formDeleteSale = document.getElementById("formDeleteSale");

buttonShowDeleteWrapper.addEventListener("click", () => {
    wrapperFormDeleteSale.classList.add("active");
})

buttonNotConfirmDelete.addEventListener("click", () => {
    wrapperFormDeleteSale.classList.remove("active");
    input_confirm_delete ="";
})

buttonConfirmDelete.addEventListener("click", async () => {
    let body = {
        "nro_orden_delete": input_confirm_delete.value
    }
    let response = await formFETCH(body, deleteSaleUrl)
    console.log(response)
    if(!response["status"]){
        document.querySelector('.errorMensaje')?.remove()
        formDeleteSale.insertAdjacentHTML('beforeend', createHTMLErrorMessaje(response["message"]))
    }
    else{
        window.location.href = response["urlRedirect"];
    }
})

function createHTMLErrorMessaje(message){
    let string =`<p class="errorMensaje">${message}</p>`
    return string
}