const selects = document.querySelectorAll(".image_display");
let flag = false;
window.addEventListener('load',()=>{
    selects.forEach(element => {
        form_create_sale.addEventListener('click', (event)=> {
                if (!element.parentElement.contains(event.target)) {
                    element.classList.remove('active')
                    activeSelect(element) 
                }else if(event.target == element && element.classList.contains("active")){
                    element.classList.remove('active')
                    activeSelect(element) 
                }else if(element.parentElement.contains(event.target)){
                    element.classList.add('active')
                    activeSelect(element)
                }
        });
    });
})

function activeSelect(inputSelect){
    // flag=true
    const height = inputSelect.nextElementSibling.scrollHeight;
    if (inputSelect.classList.contains('active')) {
        console.log("entro al active")
        inputSelect.previousElementSibling.style.zIndex = "5"
        inputSelect.nextElementSibling.style.zIndex = "4"
        inputSelect.nextElementSibling.style.height = height +'px'
        let hijos_select = inputSelect.nextElementSibling.children
        Array.from(hijos_select).forEach(item =>{
            item.addEventListener("click", ()=>{
                let text_value = item.textContent
                inputSelect.previousElementSibling.value = text_value
                inputSelect.previousElementSibling.dispatchEvent(new Event("input"))
            })
        })
    }else{
        inputSelect.nextElementSibling.style.height = '0px'
        inputSelect.nextElementSibling.style.zIndex = "1"
        setTimeout(() => {
            inputSelect.previousElementSibling.style.zIndex = "2";
          }, "400");
    }
    
}



