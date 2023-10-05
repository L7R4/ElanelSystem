const mainModalFilters = document.querySelector(".modalFilters")
const buttonModalFilters = document.getElementById("openFilters")
const closeFormFilter = document.getElementById("closeFormFilter")

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