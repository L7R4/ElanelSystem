// Inicializar los selects personalizados
function initMultipleCustomSelects(preValues = {}) {
    document
        .querySelectorAll(".containerInputAndOptions > .multipleSelect.pseudo-input-select-wrapper")
        .forEach(selectWrapper => {
            // Si se tiene algún valor previo, se lo puede pasar como segundo argumento.
            // Por ejemplo: { data: 'valor1 - valor2', text: 'Valor 1 - Valor 2' }
            // Si no, se pasa undefined.
            initMultipleSelect(selectWrapper, preValues);
        });
    ordersZindexSelects()

}

// Configurar un select personalizado con valores previos opcionales
function initMultipleSelect(selectWrapper, preValues = {}) {

    let iconDisplay = selectWrapper.parentElement.querySelector(".iconDesplegar");
    let hiddenInput = selectWrapper.previousElementSibling;
    let displayText = selectWrapper.querySelector("h3");
    let optionsList = selectWrapper.nextElementSibling;

    // Si se pasan valores previos y existe para este input (usamos el atributo name para identificarlo)
    if (preValues && Object.keys(preValues).length > 0 && preValues[hiddenInput.name]) {
        let preValue = preValues[hiddenInput.name];
        hiddenInput.value = preValue.data || "";
        displayText.textContent = preValue.text || "";
        if (displayText.textContent.trim() !== "") {
            displayText.classList.remove("placeholder");
        }
        // console.log("Valores previos asignados para", hiddenInput.name);
    } else {
        // Establecer placeholder inicial
        setPlaceholder(displayText, hiddenInput);
        // console.log("No hay valores previos para", hiddenInput.name);
    }

    // Abrir/cerrar opciones al hacer clic en el select o el icono
    selectWrapper.addEventListener("click", () => toggleOptionsList(optionsList, iconDisplay, true));
    iconDisplay.addEventListener("click", () => toggleOptionsList(optionsList, iconDisplay));

    // Delegación de eventos para seleccionar múltiples opciones
    optionsList.addEventListener("click", event => {
        if (event.target.tagName === "LI") {
            toggleOption_multipleSelect(hiddenInput, displayText, event.target, optionsList);
        }
    });

    // Cerrar opciones si se hace clic fuera
    document.addEventListener("click", event => {
        if (!selectWrapper.contains(event.target) && !optionsList.contains(event.target) && !iconDisplay.contains(event.target)) {
            closeOptionsList(optionsList, iconDisplay);
        }
    });

    // Lógica para preseleccionar valores al cargar la página
    let selectedValues = hiddenInput.value.trim().split(" - ").filter(Boolean);
    let selectedValuesText = displayText.textContent.trim().split(" - ").filter(Boolean);
    console.log("wepss");

    console.log(selectedValues);
    if (selectedValues.length > 0) {
        selectedValues.forEach(value => {
            let selectedOption = optionsList.querySelector(`li[data-value="${value}"]`);
            if (selectedOption) {
                selectedOption.classList.add("selected");
            }
        });
        updateDisplayText(displayText, selectedValuesText);
    }
    ordersZindexSelects()
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

// Función para seleccionar/deseleccionar múltiples opciones
function toggleOption_multipleSelect(hiddenInput, displayText, option, optionsList) {
    let selectedValues = hiddenInput.value ? hiddenInput.value.split(" - ") : [];

    // Si el h3 muestra el placeholder, se borra para empezar a mostrar valores seleccionados
    if (displayText.textContent.trim() === (hiddenInput.getAttribute("placeholder") || "Seleccionar")) {
        displayText.textContent = "";
    }

    let selectedValuesText = displayText.textContent ? displayText.textContent.split(" - ") : [];

    let selectedText = option.textContent;
    let selectedValue = option.getAttribute("data-value") || selectedText;

    if (option.classList.contains("selected")) {
        option.classList.remove("selected");
        selectedValues = selectedValues.filter(value => value !== selectedValue);
        selectedValuesText = selectedValuesText.filter(value => value !== selectedText);
    } else {
        option.classList.add("selected");
        selectedValues.push(selectedValue);
        selectedValuesText.push(selectedText);
    }

    hiddenInput.value = selectedValues.join(" - ");
    updateDisplayText(displayText, selectedValuesText);
    hiddenInput.dispatchEvent(new Event('input'));
}

// Función para actualizar el texto mostrado
function updateDisplayText(displayText, selectedValues) {
    if (selectedValues.length > 0) {
        displayText.textContent = selectedValues.join(" - ");
        displayText.classList.remove("placeholder");
    } else {
        setPlaceholder(displayText, displayText.parentElement.previousElementSibling);
    }
}

// Ejecutar la función en la carga del DOM
document.addEventListener("DOMContentLoaded", initMultipleCustomSelects);
