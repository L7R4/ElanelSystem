document.addEventListener('DOMContentLoaded', function() {
    const selectInputs = document.querySelectorAll('.selectInput > input');
    // const selectOptions = document.querySelectorAll('.select');
    selectInputs.forEach(element => {
        element.addEventListener('click', function(event) {
            event.stopPropagation();
            element.nextElementSibling.style.height = (element.nextElementSibling.style.height === '13rem') ? '0' : '13rem';
        });
        document.addEventListener('click', function(event) {
            if (!element.contains(event.target)) {
                element.nextElementSibling.style.height = '0';
            }
        });
        element.nextElementSibling.querySelectorAll('li').forEach(function(option) {
            option.addEventListener('click', function() {
                element.value = option.textContent;
                element.nextElementSibling.style.display = '0';
            });
        });
    });

});