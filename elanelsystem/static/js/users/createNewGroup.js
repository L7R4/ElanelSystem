let inputNewGroup = document.getElementById("groupName")
let sendNewGroup = document.getElementById("saveNewGroup")
let containerItemsGroup = document.querySelector("#itemsGrupos > ul")
const buttonCreateNewGroup = document.getElementById("buttonCreateNewGroup")
const modalCreateGroup = document.getElementById("wrapperFormNewGroup")
const closeModalForm = document.getElementById("closeModalForm")


async function createNewGroup() {
    let body = {
        "newGroup": inputNewGroup.value
    }
    let response = await fetchCRUD(body,urlCreateNewGroup)

    var newItem = document.createElement("li");
    newItem.innerHTML = response["group"];
    containerItemsGroup.appendChild(newItem)
    
    selectGroupListener(newItem)
    menuConceptual_click_derecho(newItem,urlImageDelete)

}

sendNewGroup.addEventListener("click", ()=>{
    createNewGroup();
    inputNewGroup.value =""
    modalCreateGroup.classList.remove("active")
    clearActivePermisos()
    clearActiveOfGroups()
})


// MODAL MANAGER
buttonCreateNewGroup.addEventListener("click",()=>{
    modalCreateGroup.classList.add("active")
    clearActivePermisos()
    clearActiveOfGroups()
    backgroundPermission.classList.remove("active")
    formUpdatePermisos.style.pointerEvents ="none"
    sendUpdatePermisos.classList.remove("enabled")
})

closeModalForm.addEventListener("click",()=>{
    modalCreateGroup.classList.remove("active")
})


