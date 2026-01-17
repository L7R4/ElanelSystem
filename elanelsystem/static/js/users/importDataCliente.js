function renderFormImportData() {
  return `
  <div id="importDataContainer">
    <h2 class="tittleModal">Importar clientes</h2>
    <form id="importForm" enctype="multipart/form-data">
      ${csrf_token}
      <div id="sucursalWrapper" class="wrapperTypeFilter wrapperSelectCustom inputWrapper">
        <h3 class="labelInput">Agencia</h3>
        <div class="containerInputAndOptions">
          <img class="iconDesplegar" src="${logoDisplayMore}" alt="">
          <input type="hidden" class="filterInput" required name="agencia" id="agenciaInput" placeholder="Seleccionar" autocomplete="off" readonly>
          <div class="onlySelect pseudo-input-select-wrapper"><h3></h3></div>
          <ul id="contenedorSucursal" class="list-select-custom options">
            ${sucursalesDisponibles
              .map(
                (item) => `
              <li data-value="${item.id}">${item.pseudonimo}</li>
            `
              )
              .join("")}
          </ul>
        </div>
      </div>
      <div class="containerSelectFile">
        <label for="importDataInput" class="button-default-style">Seleccionar Archivo</label>
        <p id="nameFile"></p>
        <input type="file" id="importDataInput" class="checkInput" oninput="displayNameFile(this)" style="display:none;"/>
      </div>
    </form>
  </div>`;
}

function renderMessage(message, iconMessage) {
  return `
        <div id="messageStatusContainer">
            <img src="${iconMessage}" alt="">
            <h2>${message}</h2>
        </div>
    `;
}

//#region Manejar el display del loader
function showLoader() {
  document.querySelector(".modalContainerImport").children[0].style.display =
    "none";
  document.getElementById("wrapperLoader").style.display = "flex";
}

function hiddenLoader() {
  document.getElementById("wrapperLoader").style.display = "none";
}
//#endregion

function newModalImport() {
  let modal = new tingle.modal({
    footer: true,
    closeMethods: [""],
    cssClass: ["modalContainerImport"],
    onOpen: function () {
      // inicializa el select del modal
      initSingleSelect(document.querySelector("#sucursalWrapper .onlySelect"));
      enableImportButton();
    },
    onClose: function () {
      modal.destroy();
    },
  });

  modal.setContent(renderFormImportData());

  modal.addFooterBtn(
    "Importar",
    "tingle-btn tingle-btn--primary",
    async function () {
      const fileEl = document.getElementById("importDataInput");
      const hiddenEl = document.getElementById("agenciaInput");

      // 1) leer desde la API del select
      let agencia = "";
      if (typeof getSelectValue === "function") {
        const gv = getSelectValue("#sucursalWrapper .containerInputAndOptions");
        agencia = gv && gv.value ? String(gv.value).trim() : "";
      }
      // 2) fallback al hidden
      if (!agencia) agencia = String(hiddenEl?.value || "").trim();
      // 3) último fallback: li.selected
      if (!agencia) {
        const liSel = document.querySelector(
          "#sucursalWrapper .containerInputAndOptions ul.options li.selected"
        );
        if (liSel)
          agencia = String(liSel.getAttribute("data-value") || "").trim();
      }

      // Validaciones
      if (!agencia) {
        newModalMessage(
          "Seleccioná una agencia.",
          "/static/images/icons/error_icon.svg"
        );
        return;
      }
      if (!fileEl.files || !fileEl.files[0]) {
        newModalMessage(
          "Seleccioná un archivo.",
          "/static/images/icons/error_icon.svg"
        );
        return;
      }

      showLoader();

      const body = { file: fileEl.files[0], agencia };
      const response = await fetchFunction(body, urlImportData);

      hiddenLoader();
      modal.close();
      modal.destroy();

      newModalMessage(
        response?.message || "Proceso finalizado",
        response?.iconMessage || "/static/images/icons/checkMark.svg"
      );
    }
  );

  modal.addFooterBtn("Cancelar", "tingle-btn tingle-btn--default", function () {
    modal.close();
    modal.destroy();
  });

  modal.open();

  // se bloquea hasta que los campos estén completos
  document.querySelector(".tingle-btn--primary").disabled = true;
}

function enableImportButton() {
  const importButton = document.querySelector(".tingle-btn--primary");
  const agenciaHidden = document.getElementById("agenciaInput");
  const importDataInput = document.getElementById("importDataInput");

  function readAgencia() {
    if (typeof getSelectValue === "function") {
      const gv = getSelectValue("#sucursalWrapper .containerInputAndOptions");
      return gv && gv.value
        ? String(gv.value).trim()
        : String(agenciaHidden.value || "").trim();
    }
    return String(agenciaHidden.value || "").trim();
  }

  function checkInputs() {
    const okAgencia = !!readAgencia();
    const okFile = importDataInput.files.length > 0;
    importButton.disabled = !(okAgencia && okFile);
    importButton.classList.toggle("disabled", importButton.disabled);
  }

  checkInputs();
  agenciaHidden.addEventListener("input", checkInputs);
  importDataInput.addEventListener("input", checkInputs);
}

function newModalMessage(message, iconMessage) {
  let modalMessage = new tingle.modal({
    footer: true,
    closeMethods: ["overlay", "button", "escape"],
    cssClass: ["modalContainerMessage"],
  });

  // set content
  modalMessage.setContent(renderMessage(message, iconMessage));

  modalMessage.addFooterBtn(
    "Cerrar",
    "tingle-btn tingle-btn--default",
    function () {
      // here goes some logic
      modalMessage.close();
      modalMessage.destroy();
    }
  );

  // open modal
  modalMessage.open();
}

function displayNameFile(input) {
  if (input.files[0]) {
    document.getElementById("nameFile").textContent = input.files[0].name;
  } else {
    document.getElementById("nameFile").textContent = "";
  }
}

//#region Fetch data
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

async function fetchFunction(body, url) {
  try {
    let formData = new FormData();
    formData.append("file", body.file); // Añadir el archivo
    formData.append("agencia", body.agencia); // Añadir la agencia

    let response = await fetch(url, {
      method: "POST",
      body: formData,
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
    });

    if (!response.ok) {
      throw new Error("Error");
    }

    const data = await response.json();
    return data;
  } catch (error) {}
}
//#endregion - - - - - - - - - - - - - - -
