let buttonSubmitChange = document.querySelector("#yesConfirm")
let buttonsWrapper = document.querySelector(".buttonsWrapper")

function seleccionarNuevoCliente() {
  let customer_items = document.querySelectorAll(".customer_item");

  customer_items.forEach(item => {
    item.addEventListener("click", () => {
      let id = item.querySelector("#dni").textContent;
      customer_input.value = id != customer_input.value ? id : "";

      // Crea un nuevo evento Change
      const inputEvent = new Event('input');

      // Forzar el evento Change en el elemento input
      customer_input.dispatchEvent(inputEvent);

      let checkbox = item.querySelector(".checkbox_select_client");

      if (checkbox.checked) {
        checkbox.checked = false
      } else {
        limpiarCheckboxsActivos(customer_items);
        checkbox.checked = true;
      }
      
    });
  });

}

seleccionarNuevoCliente();

function limpiarCheckboxsActivos(customer_items) {
  customer_items.forEach(item => {
    let checkbox = item.querySelector(".checkbox_select_client");
    checkbox.checked = false;
  });

}

buttonSubmitChange.addEventListener("click", async () => {

  let reponse = await fetch(window.location.href, {
    method: 'POST',
    headers: { "X-CSRFToken": getCookie('csrftoken') },
    body: JSON.stringify({ "customer": customer_input.value })
  })
  let data = await reponse.json();

  console.log(data)

  if (!data["success"]) {
    if (!document.querySelector(".message_error")) {
      buttonsWrapper.insertAdjacentHTML("afterbegin", createMessageError(data["errors"]))
    }

  } else {
    window.location.href = data["urlRedirect"]
  }

});

function checkInputs() {
  const requiredInputs = formSelectCustomer.querySelectorAll('input[required]');
  let allInputsCompleted = true;

  requiredInputs.forEach(input => {
      if (input.value.trim() === '') {
          allInputsCompleted = false;
      }
  });

  if (allInputsCompleted) {
      buttonSubmitChange.disabled = false;
  } else {
      buttonSubmitChange.disabled = true;
  }
}

// Agregar evento de input a los inputs requeridos
const requiredInputs = formSelectCustomer.querySelectorAll('input[required]');
requiredInputs.forEach(input => {
  input.addEventListener('input', checkInputs);
});



function createMessageError(errorMessage) {
  let string = `<h5 class="message_error">${errorMessage}</h5>`
  return string
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}