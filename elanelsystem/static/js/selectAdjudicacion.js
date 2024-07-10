const buttonSelectOption = document.querySelector(".selectedOption");
const optionWrapper = document.querySelector(".options");
// const options = document.querySelectorAll(".options > li");
let textOptionPicked = document.querySelector(".selectedOption > h2")

buttonSelectOption.addEventListener("click", () => {
    optionWrapper.classList.toggle("active")
})

// Si toca fuera del select, se cierra
document.addEventListener("click", function (event) {
    if (!buttonSelectOption.contains(event.target) && !optionWrapper.contains(event.target)) {
        optionWrapper.classList.remove("active"); // Cierra la lista si se hace clic fuera
    }
});