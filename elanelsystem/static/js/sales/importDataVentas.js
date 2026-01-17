function renderFormImportData() {
  return `
    <div id="importDataContainer">
      <h2 class="tittleModal">Importar ventas</h2>
      <form id="importForm" enctype="multipart/form-data">
        ${csrf_token}

        <div id="sucursalWrapper" class="wrapperTypeFilter wrapperSelectCustom inputWrapper">
          <h3 class="labelInput">Agencia</h3>
          <div class="containerInputAndOptions">
            <img class="iconDesplegar" src="${logoDisplayMore}" alt="">
            <input type="hidden" class="filterInput" required name="agencia" id="agenciaInput"
                   placeholder="Seleccionar" autocomplete="off" readonly>
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
    </div>
  `;
}

function renderMessage(message, iconMessage) {
  return `
    <div id="messageStatusContainer">
      <img src="\${iconMessage}" alt="">
      <h2>\${message}</h2>
    </div>
  `;
}

//#region Loader
function showLoader() {
  document.querySelector(".modalContainerImport").children[0].style.display =
    "none";
  document.getElementById("wrapperLoader").style.display = "flex";
}
function hiddenLoader() {
  document.getElementById("wrapperLoader").style.display = "none";
}
//#endregion

// Lee la agencia seleccionada de forma robusta
function readAgenciaValue() {
  const input = document.getElementById("agenciaInput");
  let val = (input?.value || "").trim();
  if (!val) {
    // fallback: li seleccionado por tu select custom
    const liSel = document.querySelector(
      "#agenciaWrapper .options li.selected"
    );
    if (liSel) val = (liSel.textContent || "").trim();
  }
  // fallback extra: el texto visible del pseudo-input si tu lib lo usa
  if (!val) {
    const h3 = document.querySelector(
      "#agenciaWrapper .pseudo-input-select-wrapper h3"
    );
    if (h3) val = (h3.textContent || "").trim();
  }
  // Evitar que "Seleccionar" se considere válido
  if (val.toLowerCase() === "seleccionar") val = "";
  return val;
}

// Adjunta listeners al UL para que clic en un <li> setee el input
function bindBasicSelectBehavior() {
  const ul = document.querySelector("#agenciaWrapper .options");
  const input = document.getElementById("agenciaInput");
  if (!ul || !input) return;

  ul.querySelectorAll("li").forEach((li) => {
    li.addEventListener("click", () => {
      // Marcar seleccionado visualmente
      ul.querySelectorAll("li.selected").forEach((x) =>
        x.classList.remove("selected")
      );
      li.classList.add("selected");
      // Cargar valor en el input visible
      input.value = (li.textContent || "").trim();
      // Disparar eventos para validación
      input.dispatchEvent(new Event("input", { bubbles: true }));
      input.dispatchEvent(new Event("change", { bubbles: true }));
    });
  });
}

function newModalImport() {
  const modal = new tingle.modal({
    footer: true,
    closeMethods: [""],
    cssClass: ["modalContainerImport"],
    onOpen: function () {
      // igual que clientes:
      const el = document.querySelector("#sucursalWrapper .onlySelect");
      if (typeof initSingleSelect === "function") initSingleSelect(el);
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
      const agencia = (
        document.getElementById("agenciaInput")?.value || ""
      ).trim();

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

      const body = { file: fileEl.files[0], agencia }; // agencia = pseudónimo
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
  document.querySelector(".tingle-btn--primary").disabled = true;
}

function enableImportButton() {
  const btn = document.querySelector(".tingle-btn--primary");
  const agenciaHidden = document.getElementById("agenciaInput");
  const importDataInput = document.getElementById("importDataInput");

  function checkInputs() {
    const okAgencia = !!(agenciaHidden.value || "").trim();
    const okFile = importDataInput.files.length > 0;
    btn.disabled = !(okAgencia && okFile);
    btn.classList.toggle("disabled", btn.disabled);
  }
  checkInputs();
  agenciaHidden.addEventListener("input", checkInputs);
  agenciaHidden.addEventListener("change", checkInputs);
  importDataInput.addEventListener("input", checkInputs);
}

function enableImportButton() {
  const importButton = document.querySelector(".tingle-btn--primary");
  const agenciaInput = document.getElementById("agenciaInput");
  const importDataInput = document.getElementById("importDataInput");

  function checkInputs() {
    const okAgencia = !!readAgenciaValue();
    const okFile = importDataInput.files.length > 0;
    importButton.disabled = !(okAgencia && okFile);
    importButton.classList.toggle("disabled", importButton.disabled);
  }

  checkInputs();

  // Cuando cambia el input visible (o el li seleccionado desde bindBasicSelectBehavior)
  agenciaInput.addEventListener("input", checkInputs);
  agenciaInput.addEventListener("change", checkInputs);
  importDataInput.addEventListener("input", checkInputs);
}

function newModalMessage(message, iconMessage) {
  let modalMessage = new tingle.modal({
    footer: true,
    closeMethods: ["overlay", "button", "escape"],
    cssClass: ["modalContainerMessage"],
  });

  modalMessage.setContent(renderMessage(message, iconMessage));

  modalMessage.addFooterBtn(
    "Cerrar",
    "tingle-btn tingle-btn--default",
    function () {
      modalMessage.close();
      modalMessage.destroy();
    }
  );

  modalMessage.open();
}

function displayNameFile(input) {
  document.getElementById("nameFile").textContent = input.files[0]
    ? input.files[0].name
    : "";
}
//#region Fetch data
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
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
    const formData = new FormData();
    formData.append("file", body.file);
    formData.append("agencia", body.agencia); // pseudónimo

    const resp = await fetch(url, {
      method: "POST",
      body: formData,
      headers: { "X-CSRFToken": getCookie("csrftoken") },
    });
    if (!resp.ok) throw new Error("Error");
    return await resp.json();
  } catch (e) {
    return {
      status: false,
      message: "Error de red.",
      iconMessage: "/static/images/icons/error_icon.svg",
    };
  }
}
//#endregion
