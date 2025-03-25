document.addEventListener('DOMContentLoaded', function () {
    const selectInputs = document.querySelectorAll('.selectInput');
    selectInputs.forEach(element => {
        element.addEventListener('focus', function (event) {
            event.stopPropagation();
            element.nextElementSibling.style.height = (element.nextElementSibling.style.height === '14rem') ? '0' : '14rem';
        });
        document.addEventListener('click', function (event) {
            if (!element.contains(event.target)) {
                element.nextElementSibling.style.height = '0';
            }
        });
        element.nextElementSibling.querySelectorAll('li').forEach(function (option) {
            option.addEventListener('click', function () {
                element.value = option.textContent;
                element.nextElementSibling.style.display = '0';
                // Crea un nuevo evento Change
                const changeEvent = new Event('input');

                // Forzar el evento Change en el elemento input
                element.dispatchEvent(changeEvent);
            });
        });
    });

});