let modalFilter = document.querySelector(".modalFilterContainer")
let buttonsActiveModalFilter = document.querySelectorAll(".buttonActiveModalFilter")
let buttonCloseModal = document.querySelector("#closeFormFilter")


buttonsActiveModalFilter.forEach(button => {
    button.addEventListener("click", () => {
        modalFilter.classList.add("active")
        modalFilter.style.opacity = "1";
    })
})

buttonCloseModal.addEventListener("click", () => {
    modalFilter.style.opacity = "0";
    setTimeout(() => {
        modalFilter.classList.remove("active")
    }, 300)

})
