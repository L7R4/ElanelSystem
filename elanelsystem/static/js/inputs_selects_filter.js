document.addEventListener('DOMContentLoaded', function() {
    const selectInputsFilter = document.querySelectorAll('.selectInputFilter > input');
    // const selectOptions = document.querySelectorAll('.select');
    selectInputsFilter.forEach(element => {
        element.addEventListener('click', function(event) {
            event.stopPropagation();
            element.nextElementSibling.style.height = (element.nextElementSibling.style.height === '13rem') ? '0' : '13rem';
        });
        document.addEventListener('click', function(event) {
            // if (!element.contains(event.target)) {
            //     element.nextElementSibling.style.height = '0';
            // }
            let childrenArray = element.nextElementSibling.children;
            let isEventTargetInArray = false;

                for (let i = 0; i < childrenArray.length; i++) {
                    if (childrenArray[i] === event.target) {
                        isEventTargetInArray = true;
                        break;
                    }
                }
            if (!element.contains(event.target) && !isEventTargetInArray) {
                element.nextElementSibling.style.height = '0';
            }
        });
        element.nextElementSibling.querySelectorAll('li').forEach(function(option) {
            option.addEventListener('click', function() {
                toggleOption(option)
            });
        });
    });

    function toggleOption(option) {
        // Obtenemos el input asociado al botón
        const input = option.closest('.selectInputFilter').querySelector('input');
    
        // Obtenemos las opciones actualmente seleccionadas del valor del input, separadas por comas
        let selectedOptions = input.value.split('-').map(option => option.trim());
    
        // Verificamos si la opción actual ya está seleccionada
        const optionText = option.textContent.trim();
        const index = selectedOptions.indexOf(optionText);
        
        if (index !== -1) {
            // Si la opción está seleccionada, la eliminamos de las opciones seleccionadas
            selectedOptions.splice(index, 1);
            option.classList.remove("itemPicked")
        } else {
            // Si la opción no está seleccionada, la agregamos a las opciones seleccionadas
            selectedOptions.push(optionText);
            option.classList.add("itemPicked")
        }
    
        // Actualizamos el valor del input con las opciones seleccionadas, separadas por comas
        input.value = (input.value != "") ? selectedOptions.join(' - ') : optionText;
    }
    
    function checkValorEnInput() {
        let query = window.location.search;
        let queryTodict = parseQueryString(query)
        let inputsFilter = document.querySelectorAll(".inputFilter");
        console.log(queryTodict)
        if(Object.keys(queryTodict).length != 1){
            inputsFilter.forEach(element => {
                if(queryTodict[element.name] != ""){
                    if(element.type =="radio"){
                        let radioPicked = queryTodict[element.name].toLowerCase()
                        let labelOfRadioPicked = document.getElementById(radioPicked).nextElementSibling
                        if(!labelOfRadioPicked.classList.contains("active")){
                            labelOfRadioPicked.click()
                        }
                    }else{
                        // Por si vienen varios valores, limpiamos el string
                        let valores = queryTodict[element.name].replace(/\+/g, ' ')

                        // Guarda los valores en el value del input
                        element.value = valores

                        // Sepera los valores en un array
                        valores = valores.split('-').map(option => option.trim());
                        console.log(valores)

                        // Para convertir a array se utiliza ese nomencaltura "..."
                        let listItemsArray = [...element.nextElementSibling.children]

                        uploadStyles(listItemsArray,valores)
                    }
                }
            });
        }
        
        
    }  
    function uploadStyles(options,valores) {
        options.forEach(option=>{
            
            if(valores.filter(e=>e == option.textContent).length != 0){
                option.classList.add("itemPicked")
            }
        })
    }
    checkValorEnInput()
    
});