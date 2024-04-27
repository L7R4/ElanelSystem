document.addEventListener('DOMContentLoaded', function() {
    const selectInputs = document.querySelectorAll('.selectInput > input');
    
    selectInputs.forEach(element => {
        element.addEventListener('click', function(event) {
            event.stopPropagation();
            element.nextElementSibling.style.height = (element.nextElementSibling.style.height === '13rem') ? '0' : '13rem';
        });
        document.addEventListener('click', function(event) {
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
                if(element.value == option.textContent){
                    element.value = "";
                    option.classList.remove("itemPicked")
                }else{
                    element.value = option.textContent;
                    element.nextElementSibling.querySelectorAll('li').forEach(item => item.classList.remove("itemPicked"))
                    option.classList.add("itemPicked")
                }
                // element.nextElementSibling.style.display = '0';
                
            });
        });
        element.nextElementSibling.querySelectorAll('li').forEach(item => item.classList.remove("itemPicked"))
    });
})