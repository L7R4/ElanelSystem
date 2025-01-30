const filterIcons = document.querySelectorAll(".filter-icon");
const filterSelect = document.querySelector(".filter-select");

document.addEventListener("DOMContentLoaded", listenerIconFilter);

// Abrir/cerrar el select al hacer clic en el icono
function listenerIconFilter() {
    filterIcons.forEach((filterIcon) => {
        filterIcon.addEventListener("click", () => {
            filterSelect.classList.toggle("open");
        });
    })

    // Manejar la selección de opciones
    filterSelect.addEventListener("click", (event) => {
        if (event.target.classList.contains("filter-option")) {
            const selectedValue = event.target.dataset.value;
            console.log("Filtro seleccionado:", selectedValue);
            filterSelect.classList.remove("open");
        }
    });

    // Cerrar el select si se hace clic fuera
    document.addEventListener("click", (event) => {
        filterIcons.forEach((filterIcon) => {
            if (!filterIcon.contains(event.target) && !filterSelect.contains(event.target)) {
                filterSelect.classList.remove("open");
            }
        })
    });
}
