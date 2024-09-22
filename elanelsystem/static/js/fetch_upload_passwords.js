let buttonsEnableForms = document.querySelectorAll(".enableForm")
let path = window.location.pathname
let messageWrapper = document.querySelector(".messageWrapper")


// SWITCH BUTTONS
function editarSucursal(buttons) {
    buttons.forEach(buttonE => {
        buttonE.addEventListener("click", () => {
            let form = buttonE.parentElement.parentElement
            let buttonDesable = form.querySelector(".desableForm")
            let buttonUpload = form.querySelector(".uploadForm")
            let inputValues = [];
            form.querySelectorAll(".wrapperInput > input").forEach(element => {
                element.classList.remove("not_ed")
                inputValues.push(element.value);
                
            });

            buttonE.style.display = "none";

            buttonDesable.classList.add("active")
            buttonUpload.classList.add("active")

            buttonDesable.addEventListener("click", () => {
                    form.querySelectorAll(".wrapperInput > input").forEach((element, index) => {
                        element.classList.add("not_ed")
                        element.value = inputValues[index]

                    });

                    let enableForm = form.querySelector(".enableForm")

                    if (!form) { return; }

                    buttonDesable.classList.remove("active")
                    buttonDesable.previousElementSibling.classList.remove("active")

                    enableForm.style.display = "flex";

                })

            buttonUpload.addEventListener("click", async () => {
                    let inputs = form.querySelectorAll(".wrapperInput > input:not([type='hidden'])");
                    let enableForm = form.querySelector(".enableForm")

                    if (!form) { return; } 

                    buttonUpload.classList.remove("active")
                    buttonUpload.nextElementSibling.classList.remove("active")

                    enableForm.style.display = "flex";
                
                    let body = {}
                    inputs.forEach(element => {
                        body[element.name] = element.value
                    });
                    console.log(body)

                    let response = await fetchCRUD(body, path)
                    if (response["success"]) {
                        inputs.forEach(element => {
                            element.classList.add("not_ed")
                        });
                    }else{
                        inputs.forEach((element, index) => {
                            element.classList.add("not_ed")
                            element.value = inputValues[index]
                        });
                    }
                    show_hide_message(response["message"])
                })
        })
    });
}

editarSucursal(buttonsEnableForms)

function cleanAddSucursal() {
    if (document.getElementById("addSucursalForm")) {
        document.querySelector(".sucursalItem.new").remove()
    }
}

function show_hide_message(mensaje) {
    let message = messageWrapper.querySelector("h3")
    message.textContent = mensaje
    messageWrapper.classList.add("active")
    setTimeout(() => {
        messageWrapper.classList.remove("active")
    }, 3000)
}
//  - - - - - - - - - - - - - - - - - - - - - - 
 
// FUNCTION FETCH - - - - - - - - - 
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


async function fetchCRUD(body, url) {
    try {
        let response = await fetch(url, {
            method: "POST",
            body: JSON.stringify(body),
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
            }
        })
        if (!response.ok) {
            throw new Error("Error")
        }
        const data = await response.json();
        return data;
    } catch (error) {
    }
}
// - - - - - - - - - - - - - - - - -

