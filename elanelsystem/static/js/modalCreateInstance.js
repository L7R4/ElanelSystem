var url = window.location.pathname;
if (url.includes("planes")) {
    planesUrl.classList.add("active")
}

const createInstanceWrapper = document.querySelector(".createInstanceWrapper");
const buttonCreate = document.querySelector(".buttonCreate")
const closeFormCreateInstance = document.getElementById("closeFormCreateInstance")

buttonCreate.addEventListener("click",()=>{
    createInstanceWrapper.classList.add("active")
    buttonCreate.style.display = "none"
})

closeFormCreateInstance.addEventListener("click",()=>{
    createInstanceWrapper.classList.remove("active")
    buttonCreate.style.display = "block"
})