// Inicializar los selects personalizados
function initCustomSingleSelects(preValues = {}) {
    document.querySelectorAll(".containerInputAndOptions > .onlySelect.pseudo-input-select-wrapper").forEach(selectWrapper => {
        initSingleSelect(selectWrapper, preValues);
    });
    ordersZindexSelects()
}

// Configurar un select personalizado
function initSingleSelect(selectWrapper, preValues = {}) {
    if (selectWrapper.dataset._inited === "1") return;   // ← evita doble init
        selectWrapper.dataset._inited = "1";                 // ← marca como inicializado
    let iconDisplay = selectWrapper.parentElement.querySelector(".iconDesplegar"); // Icono desplegable
    let hiddenInput = selectWrapper.previousElementSibling; // Input hidden
    let displayText = selectWrapper.querySelector("h3"); // H3 que muestra la opción seleccionada
    let optionsList = selectWrapper.nextElementSibling; // UL con opciones

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

    // Delegación de eventos para seleccionar una opción
    optionsList.addEventListener("click", event => {
        if (event.target.tagName === "LI") {
            toggleOption_singleSelect(hiddenInput, displayText, event.target, optionsList);
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

    if (selectedValue.length > 0) {
        let selectedOption = optionsList.querySelector(`li[data-value="${selectedValue}"]`);
        if (selectedOption) {
            selectedOption.classList.add("selected"); // Marca la opción como seleccionada
            displayText.textContent = selectedOption.textContent; // Actualiza el h3 con el texto seleccionado
            displayText.classList.remove("placeholder");
        }
    }
    ordersZindexSelects()

}


// Función para limpiar los inputs
// function clearInputs(inputs) {
//     console.log(inputs)
//     inputs.forEach(input => input.value = "");
//     let pseudo_input = document.querySelectorAll(".pseudo-input-select-wrapper > h3");
//     pseudo_input.forEach(input => {
//         input.textContent = ""
//         setPlaceholder(input, input.parentElement.previousElementSibling);
//     });

//     inputs.forEach(element => {
//         let options = element.parentElement.querySelector(".options");
//         console.log(options)
//         options.querySelectorAll("li.selected").forEach(el => el.classList.remove("selected"));
//     });

// }

function clearInputs(inputs, scope = document) {
  // 1) limpiar valores de inputs pasados
  console.log("aaaaaaaaa")
  console.log(inputs)

  inputs.forEach(input => { input.value = ""; });

  // 2) limpiar selects custom dentro del scope
  scope.querySelectorAll(".containerInputAndOptions").forEach(container => {
    const hidden  = container.querySelector("input[type='hidden']");
    const h3      = container.querySelector(".pseudo-input-select-wrapper > h3");
    const options = container.querySelector(".options");

    // a) quitar selección visual de las opciones
    if (options) options.querySelectorAll("li.selected").forEach(li => li.classList.remove("selected"));

    // b) resetear placeholder del pseudo input
    if (h3 && hidden) setPlaceholder(h3, hidden);

    // c) asegurar que el hidden quede vacío
    if (hidden) hidden.value = "";
  });
}
window.clearInputs = clearInputs;


// Función para establecer placeholder
function setPlaceholder(displayText, hiddenInput) {
    let placeholderText = hiddenInput.getAttribute("placeholder") || "Seleccionar";
    displayText.textContent = placeholderText;
    displayText.classList.add("placeholder");
}
window.setPlaceholder = setPlaceholder;


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
function toggleOption_singleSelect(hiddenInput, displayText, option, optionsList) {
    let selectedText = option.textContent;
    let selectedValue = option.getAttribute("data-value") || selectedText;

    // Si la opción ya está seleccionada, la deseleccionamos
    if (option.classList.contains("selected")) {
        option.classList.remove("selected");
        hiddenInput.value = "";
        setPlaceholder(displayText, hiddenInput);
    } else {
        console.log("weps")
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
document.addEventListener("DOMContentLoaded", initCustomSingleSelects);

function updateEventsLisOptions(input, optionsList) {
    let options = optionsList.querySelectorAll("li");
    // toggleOptionsList(input, optionsList);

    options.forEach(option => {
        option.addEventListener("click", () => {
            let displayText = optionsList.previousElementSibling.querySelector("h3");
            toggleOption_singleSelect(input, displayText, option, optionsList);
        });
    });
}
