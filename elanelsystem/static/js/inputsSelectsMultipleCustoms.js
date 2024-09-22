/* 
    Se hace de esta manera el manejo de el input select porque
    entonces evitamos el 'event listener duplication' que es basicamente
    cuando damos un click y se duplica el listener, es decir que toda
    la logica que se encuentra dentro se multiplicará por la cantidad de veces
    que hayamos multiplicado sin querer.
    Para esto evitar anidar addEventListener dentro de otros eventos que se activen repetidamente como "focus" o "click" u otro evento.

    Para prevenir este problema:
        -> Asegurarse de que los listeners se añaden solo una vez.
        -> Utiliza metodos para remover listeners cuando ya no sean necesarios.
        -> Verifica si el listener ya existe antes de agregar uno nuevo.
        -> Considera usar flags o controles que prevengan la duplicación de listeners.
        -> O hacerlo de esta manera que se hizo aqui abajo.

*/

let inputSelectMultipleCustom = document.querySelectorAll(".containerInputAndOptions > input.multipleSelect");


inputSelectMultipleCustom.forEach(input => {
    let optionsList = input.nextElementSibling;
    let options = optionsList.querySelectorAll("li");

    toggleOptionsLists(input, optionsList);

    options.forEach(option => {
        option.addEventListener("click", () => {
            toggleOptions(input, option)
            console.log("Dispara multiple input")

            // Disparar el evento "input" en el input después de seleccionar una opción
            input.dispatchEvent(new Event('input'));
        });
    });
});

// Funcion que controla la seleccion de las opciones del menu select
function toggleOptions(input, option) {
    // Obtenemos las opciones actualmente seleccionadas del valor del input, separadas por comas
    let selectedOptions = input.value.split('-').map(option => option.trim());

    // Verificamos si la opción actual ya está seleccionada
    const optionText = option.textContent.trim();

    const index = selectedOptions.indexOf(optionText);
    if (index !== -1) {
        // Si la opción está seleccionada, la eliminamos de las opciones seleccionadas
        selectedOptions.splice(index, 1);
        option.classList.remove("selected")
    } else {
        // Si la opción no está seleccionada, la agregamos a las opciones seleccionadas
        selectedOptions.push(optionText);
        option.classList.add("selected")
    }

    // Actualizamos el valor del input con las opciones seleccionadas, separadas por comas
    input.value = (input.value != "") ? selectedOptions.join(' - ') : optionText;
}

// Funcion donde se le pasa el input en el cual se hizo click para que pueda MOSTRAR O NO MOSTRAR la lista de opciones
function toggleOptionsLists(input, optionsList) {
    // Si hace click directamente en el input
    input.addEventListener("focus", () => {
        if (!optionsList.classList.contains("open")) {
            optionsList.classList.add("open");
            iconDisplay.classList.add("open")

        }
    });

    // Si hacen click en el icono
    let iconDisplay = input.previousElementSibling
    iconDisplay.addEventListener("click", () => {

        if (iconDisplay.classList.contains("open")) {
            iconDisplay.classList.remove("open")
            optionsList.classList.remove("open"); // Cierra la lista 
        } else {
            optionsList.classList.add("open");
            iconDisplay.classList.add("open");
        }
    });

    // Cerrar la lista si se hace clic fuera
    document.addEventListener("click", function (event) {
        if (!input.contains(event.target) && !optionsList.contains(event.target) && !iconDisplay.contains(event.target)) {
            optionsList.classList.remove("open"); // Cierra la lista si se hace clic fuera
            iconDisplay.classList.remove("open"); // Cierra la lista si se hace clic fuera
        }
    });
}

