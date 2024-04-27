const mainModalFilters = document.querySelector(".modalFilters")
const buttonModalFilters = document.getElementById("openFilters")
const closeFormFilter = document.getElementById("closeFormFilter")
const urlParams = new URLSearchParams(window.location.search);

buttonModalFilters.addEventListener('click', ()=>{
    mainModalFilters.classList.add("active")
    mainModalFilters.style.opacity = "1"
})

closeFormFilter.addEventListener("click",()=>{
    mainModalFilters.style.opacity = "0"
    setTimeout(()=>{
        mainModalFilters.classList.remove("active")

    },300)
})

if(urlParams["size"] != 0){
    clear_filters.classList.add("show")
}