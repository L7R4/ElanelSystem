const filterIconsWrapper = document.querySelectorAll(".filter-iconWrapper");

document.addEventListener("DOMContentLoaded", listenerIconFilter);

// Abrir/cerrar el select al hacer clic en el icono
function listenerIconFilter() {
    filterIconsWrapper.forEach((filterIcon) => {
        filterIcon.addEventListener("click", () => {
            const filterSelect = filterIcon.querySelector(".filter-select");
            console.log("Filtro seleccionado:", filterSelect);
            filterSelect.classList.toggle("open");
        });
    })

    const allFilterSelects = document.querySelectorAll(".filter-select");

    // Manejar la selección de opciones
    allFilterSelects.forEach(fs => {
        fs.addEventListener("click", (event) => {
            if (event.target.classList.contains("filter-option")) {
                const selectedOption = event.target;
                const input = fs.parentElement.querySelector("input");
                // Alternar la selección en el elemento clickeado
                if (!selectedOption.classList.contains("selected")) {
                    clearSelected(fs);
                    selectedOption.classList.add("selected");

                    const selectedValue = selectedOption.dataset.value;
                    console.log("Filtro seleccionado:", selectedValue);
                    input.value = selectedValue;

                } else {
                    clearSelected(fs);
                    input.value = ""
                }

                input.dispatchEvent(new Event("input", { bubbles: true })); // Dispara el evento input en el input


                fs.classList.remove("open");

            }
        });
    });



    // Cerrar el select si se hace clic fuera
    document.addEventListener("click", (event) => {
        filterIconsWrapper.forEach((filterIcon) => {
            if (!filterIcon.contains(event.target) && !filterIcon.querySelector(".filter-select").contains(event.target)) {

                filterIcon.querySelector(".filter-select").classList.remove("open");
            }
        })
    });
}

function clearSelected(parentUL) {
    // Quitar la clase 'selected' de todas las opciones dentro del mismo ul
    parentUL.querySelectorAll(".filter-option").forEach(option => {
        option.classList.remove("selected");
    });
}
