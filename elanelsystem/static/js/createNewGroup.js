let inputNewGroup = document.getElementById("groupName")
let sendNewGroup = document.getElementById("saveNewGroup")
let containerItemsGroup = document.querySelector("#itemsGrupos > ul")
const buttonCreateNewGroup = document.getElementById("buttonCreateNewGroup")
const modalCreateGroup = document.getElementById("wrapperFormNewGroup")
const closeModalForm = document.getElementById("closeModalForm")


function createNewGroup() {
    let body = {
        "newGroup": inputNewGroup.value
    }
    fetchCRUD(body,urlCreateNewGroup).then(data=>{
        var newItem = document.createElement("li");
        newItem.innerHTML = data["group"];
        containerItemsGroup.appendChild(newItem);
        itemsGrupo = document.querySelectorAll("#itemsGrupos > ul > li")
        selectGroup(itemsGrupo);
        menuConceptual_click_derecho(itemsGrupo,urlImageDelete)

    })
}

sendNewGroup.addEventListener("click", ()=>{
    createNewGroup();
    inputNewGroup.value =""
    modalCreateGroup.classList.remove("active")
})

// MODAL MANAGER
buttonCreateNewGroup.addEventListener("click",()=>{
    modalCreateGroup.classList.add("active")
})

closeModalForm.addEventListener("click",()=>{
    modalCreateGroup.classList.remove("active")
})


