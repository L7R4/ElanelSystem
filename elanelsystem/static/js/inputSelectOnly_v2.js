// Inicializar los selects personalizados
function initCustomSelects() {
    document.querySelectorAll(".containerInputAndOptions > .onlySelect.pseudo-input-select-wrapper").forEach(initSelect);
}

// Configurar un select personalizado
function initSelect(selectWrapper) {
    let iconDisplay = selectWrapper.parentElement.querySelector(".iconDesplegar"); // Icono desplegable
    let hiddenInput = selectWrapper.previousElementSibling; // Input hidden
    let displayText = selectWrapper.querySelector("h3"); // H3 que muestra la opción seleccionada
    let optionsList = selectWrapper.nextElementSibling; // UL con opciones

    // Establecer placeholder inicial
    setPlaceholder(displayText, hiddenInput);

    // Abrir/cerrar opciones al hacer clic en el select o el icono
    selectWrapper.addEventListener("click", () => toggleOptionsList(optionsList, iconDisplay, true));
    iconDisplay.addEventListener("click", () => toggleOptionsList(optionsList, iconDisplay));

    // Delegación de eventos para seleccionar una opción
    optionsList.addEventListener("click", event => {
        if (event.target.tagName === "LI") {
            toggleOption(hiddenInput, displayText, event.target, optionsList);
        }
    });

    // Cerrar opciones si se hace clic fuera
    document.addEventListener("click", event => {
        if (!selectWrapper.contains(event.target) && !optionsList.contains(event.target) && !iconDisplay.contains(event.target)) {
            closeOptionsList(optionsList, iconDisplay);
        }
    });

    // Lógica para preseleccionar el valor al cargar la página
    let selectedValue = hiddenInput.value.trim(); // Obtiene el valor actual del input hidden
    if (selectedValue) {
        let selectedOption = optionsList.querySelector(`li[data-value="${selectedValue}"]`);
        if (selectedOption) {
            selectedOption.classList.add("selected"); // Marca la opción como seleccionada
            displayText.textContent = selectedOption.textContent; // Actualiza el h3 con el texto seleccionado
            displayText.classList.remove("placeholder");
        }
    }
}

// Función para establecer placeholder
function setPlaceholder(displayText, hiddenInput) {
    let placeholderText = hiddenInput.getAttribute("placeholder") || "Seleccionar";
    displayText.textContent = placeholderText;
    displayText.classList.add("placeholder");
}

// Función para abrir/cerrar la lista de opciones
function toggleOptionsList(optionsList, iconDisplay, forceOpen = false) {
    let isOpen = optionsList.classList.contains("open");
    if (forceOpen || !isOpen) {
        optionsList.classList.add("open");
        iconDisplay.classList.add("open");
    } else {
        closeOptionsList(optionsList, iconDisplay);
    }
}

// Función para cerrar la lista de opciones
function closeOptionsList(optionsList, iconDisplay) {
    optionsList.classList.remove("open");
    iconDisplay.classList.remove("open");
}

// Función para seleccionar una opción
function toggleOption(hiddenInput, displayText, option, optionsList) {
    let selectedText = option.textContent;
    let selectedValue = option.getAttribute("data-value") || selectedText;

    // Si la opción ya está seleccionada, la deseleccionamos
    if (option.classList.contains("selected")) {
        option.classList.remove("selected");
        hiddenInput.value = "";
        setPlaceholder(displayText, hiddenInput);
    } else {
        optionsList.querySelectorAll("li.selected").forEach(el => el.classList.remove("selected"));
        option.classList.add("selected");
        hiddenInput.value = selectedValue;
        displayText.textContent = selectedText;
        displayText.classList.remove("placeholder");
    }

    closeOptionsList(optionsList, hiddenInput.closest(".containerInputAndOptions").querySelector(".iconDesplegar"));
    hiddenInput.dispatchEvent(new Event('input'));
}

// Ejecutar la función en la carga del DOM
document.addEventListener("DOMContentLoaded", initCustomSelects);
