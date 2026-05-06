function getRawCsrfToken() {
  const t = document.createElement('div');
  t.innerHTML = (typeof csrf_token !== 'undefined') ? csrf_token : '';
  const input = t.querySelector('input');
  return input ? input.value : ((typeof csrf_token !== 'undefined') ? csrf_token : '');
}

function renderFormImportColaboradores() {
  return `
    <div id="importDataContainer" style="padding: 20px; min-height: 45vh; display: flex; flex-direction: column; justify-content: center; color: #333;">
      <div style="border-bottom: 2px solid var(--blue-0);">
        <h2 class="tittleModal" style="color: #2b6cb0; font-size: 2.2rem; margin-bottom: 25px; padding-bottom: 10px; font-family: 'Inter', sans-serif;">Importar Datos de Colaborador</h2>
      </div>
      <form id="importFormColaboradores" enctype="multipart/form-data" style="display: flex; flex-direction: column; gap: 20px; flex-grow: 1;">
        ${csrf_token}
        
        <div id="agenciaColaboradorWrapper" class="wrapperTypeFilter wrapperSelectCustom inputWrapper">
          <h3 class="labelInput" style="color: #4a5568; font-size: 1.5rem; margin-bottom: 8px;">Agencia</h3>
          <div class="containerInputAndOptions" style="position: relative;">
            <img class="iconDesplegar" src="${logoDisplayMore}" alt="" style="position: absolute; right: 15px; top: 50%; transform: translateY(-50%); pointer-events: none;">
            <input type="hidden" class="filterInput" required name="agencia" id="agenciaColaboradorInput"
                   placeholder="Seleccionar" autocomplete="off" readonly>
            <div class="onlySelect pseudo-input-select-wrapper" style="border: 1px solid var(--blue-2); border-radius: 8px; padding: 12px 15px; background: transparent; cursor: pointer;">
                <h3 style="margin: 0;color: var(--third-color);font-size: 1.4rem;font-weight: normal;">Seleccionar agencia...</h3>
            </div>
            <ul id="contenedorAgenciaColaborador" class="list-select-custom options" style="background: var(--blue-1);border: 1px solid var(--blue-0);border-radius: 8px;box-shadow: rgba(0, 0, 0, 0.1) 0px 4px 6px;color: var(--third-color);z-index: 1;margin-top: 15px;">
              ${sucursalesDisponibles
      .map((item) => `<li data-value="${item.id}" style="padding: 10px 15px; font-size: 1.3rem; border-bottom: 1px solid var(--blue-0); cursor: pointer;">${item.pseudonimo}</li>`)
      .join("")}
            </ul>
          </div>
        </div>

        <style>
          .hover-container-file {
            margin-top: 15px; 
            background-color: transparent; 
            border: 2px dashed var(--blue-1); 
            border-radius: 10px; 
            transition: all 0.3s ease;
          }
          .hover-container-file:hover {
            background-color: var(--blue-1);
            border: 2px dashed var(--blue-0);
          }
          .hover-container-file label {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 100%;
            min-height: 130px;
            cursor: pointer;
            font-size: 1.6rem;
            color: var(--third-color, #4a5568);
            font-weight: 500;
            box-sizing: border-box;
            padding: 20px;
          }
        </style>
        <div class="containerSelectFile hover-container-file">
          <label for="importColaboradorInput">
             Seleccionar Archivo (Excel)
             <span id="nameFileColaborador" style="margin-top: 12px; font-size: 1.4rem; color: var(--blue-3); text-align: center; font-weight: 600; display: block; min-height: 20px;"></span>
          </label>
          <input type="file" id="importColaboradorInput" class="checkInput" accept=".xlsx, .xls" oninput="displayNameFileColaborador(this)" style="display:none;"/>
        </div>
      </form>
    </div>
  `;
}

function displayNameFileColaborador(input) {
  document.getElementById("nameFileColaborador").textContent = input.files[0] ? input.files[0].name : "";
}

function enableImportColaboradoresButton() {
  const btn = document.querySelector(".tingle-btn--primary-import");
  const inputE = document.getElementById("agenciaColaboradorInput");
  const importInputE = document.getElementById("importColaboradorInput");
  if (!btn) return;
  function check() {
    const okAgencia = !!(inputE.value || "").trim();
    const okFile = importInputE.files.length > 0;
    btn.disabled = !(okAgencia && okFile);
    btn.classList.toggle("disabled", btn.disabled);
  }
  check();
  inputE.addEventListener("input", check);
  inputE.addEventListener("change", check);
  importInputE.addEventListener("input", check);
}

function renderPreviewImportColaboradores(data) {
  const { vendedores = [], supervisores = [], gerentes = [], nuevos = [] } = data;

  const renderItem = (c, isNew) => {
    const isChanged = (field) => c.changed && c.changed.includes(field);
    const getStyle = (field) => {
      let base = `width:100%; border-radius: 6px; padding: 8px 10px; font-size: 1.3rem; color: var(--third-color) !important; background-color: var(--blue-1); outline: none; transition: border-color 0.2s; box-sizing: border-box;`;
      // Usar verde para resaltar los campos que provienen del Excel y están actualizando info.
      if (isNew || isChanged(field)) {
        return base + ` border: 2px solid #48bb78; box-shadow: 0 0 4px rgba(72,187,120,0.3);`;
      }
      return base + ` border: 1px solid var(--blue-1);`;
    };

    return `
    <li data-index="${c.index}" data-isnew="${isNew}" style="background-color: var(--blue-0);border: 1px solid var(--blue-1);padding: 15px 20px;margin-bottom: 12px;border-radius: 8px;box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid var(--blue-1); padding-bottom: 10px;">
        <strong style="font-size: 1.5rem; color: var(--third-color)">${c.nombre}</strong> 
        <div style="display: flex; align-items: center; gap: 10px;">
          ${isNew 
            ? `<select class="edit-rango" style="${getStyle('rango')} width: auto; font-weight: 600;">
                 <option value="Vendedor" ${c.rango === 'Vendedor' ? 'selected' : ''}>Vendedor</option>
                 <option value="Supervisor" ${c.rango === 'Supervisor' ? 'selected' : ''}>Supervisor</option>
                 <option value="Gerente sucursal" ${c.rango === 'Gerente sucursal' ? 'selected' : ''}>Gerente</option>
               </select>`
            : `<span style="background-color: var(--blue-2);color: var(--third-color);padding: 4px 10px;border-radius: 6px;font-size: 1.2rem;font-weight: 600;letter-spacing: 0.5px;">${c.rango}</span>`
          }
          <button type="button" title="Quitar este colaborador de la importación" onclick="this.closest('li').remove()" style="background-color: #e53e3e; color: white; border: none; border-radius: 6px; padding: 5px 12px; cursor: pointer; font-size: 1.2rem; font-weight: bold; transition: opacity 0.2s;" onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'">
            Quitar
          </button>
        </div>
      </div>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px;">
        <label style="font-size: 1.2rem; color: var(--third-color); font-weight: 600; display: flex; flex-direction: column; gap: 4px;">DNI:
          <input type="text" style="${getStyle('dni')}" class="edit-dni" value="${c.dni || ''}">
        </label>
        <label style="font-size: 1.2rem; color: var(--third-color); font-weight: 600; display: flex; flex-direction: column; gap: 4px;">Alias:
          <input type="text" style="${getStyle('alias')}" class="edit-alias" value="${c.alias || ''}">
        </label>
        <label style="font-size: 1.2rem; color: var(--third-color); font-weight: 600; display: flex; flex-direction: column; gap: 4px;">CBU:
          <input type="text" style="${getStyle('cbu')}" class="edit-cbu" value="${c.cbu || ''}">
        </label>
        <label style="font-size: 1.2rem; color: var(--third-color); font-weight: 600; display: flex; flex-direction: column; gap: 4px;">Entidad:
          <input type="text" style="${getStyle('entidad_bancaria')}" class="edit-entidad" value="${c.entidad_bancaria || ''}">
        </label>
        <label style="font-size: 1.2rem; color: var(--third-color); font-weight: 600; display: flex; flex-direction: column; gap: 4px;">F/Alta:
          <input type="text" style="${getStyle('fec_ingreso')}" class="edit-fec-ingreso" value="${c.fec_ingreso || ''}" placeholder="DD/MM/AAAA">
        </label>
        <label style="font-size: 1.2rem; color: var(--third-color); font-weight: 600; display: flex; flex-direction: column; gap: 4px;">F/Baja:
          <input type="text" style="${getStyle('fec_egreso')}" class="edit-fec-egreso" value="${c.fec_egreso || ''}" placeholder="DD/MM/AAAA">
        </label>
      </div>
   </li>
  `;
  };

  const renderSection = (title, items, isNew, emptyMsg) => {
    if (items.length === 0) return '';
    const sectionHtml = items.map(c => renderItem(c, isNew)).join('');
    return `
      <div style="background-color: var(--blue-1); border: 1px solid var(--blue-1); border-radius: 10px; padding: 20px; margin-bottom: 20px;">
        <h3 style="margin-top: 0; margin-bottom: 18px; font-size: 1.8rem; color: var(--third-color); display: flex; align-items: center; gap: 10px;">
           <span style="font-size: 2.2rem;"></span> ${title} (${items.length}):
        </h3>
        <ul style="list-style: none; padding: 0; margin: 0;">
          ${sectionHtml}
        </ul>
      </div>
    `;
  };

  const hasAny = vendedores.length > 0 || supervisores.length > 0 || gerentes.length > 0 || nuevos.length > 0;

  return `
    <style>
      .modalContainerImport .tingle-modal-box {
        width: 95% !important;
        max-width: 1600px !important;
      }
    </style>
    <div id="previewDataContainer" style="font-family: 'Inter', 'Segoe UI', sans-serif;">
      
      <div style="padding: 10px 20px;">
        <h2 class="tittleModal" style="color: var(--third-color); font-size: 2.4rem; border-bottom: 2px solid var(--blue-1); padding-bottom: 12px; margin-bottom: 12px; margin-top: 0;">Previsualización de Importación</h2>
        <p style="font-size: 1.5rem; color: #4a5568; line-height: 1.5; margin: 0;">Los colaboradores que ya tenían todos sus datos exactos no se muestran aquí.</p>
        ${!hasAny ? '<p style="font-size: 1.6rem; color: #4a5568; margin-top: 30px; font-style: italic;">No hay registros para actualizar o crear.</p>' : ''}
      </div>
      
      <div style="display: flex; gap: 20px; width: 100%; padding: 0 20px; box-sizing: border-box; max-height: 65vh;">
        <!-- COLUMNA 1: NUEVOS COLABORADORES -->
        <div style="flex: 1; overflow-y: auto; padding-right: 10px;">
          ${renderSection('Nuevos Colaboradores', nuevos, true)}
        </div>
        
        <!-- COLUMNA 2: VENDEDORES -->
        <div style="flex: 1; overflow-y: auto; padding-right: 10px;">
          ${renderSection('Vendedores A Actualizar', vendedores, false)}
        </div>

        <!-- COLUMNA 3: SUPERVISORES Y GERENTES -->
        <div style="flex: 1; overflow-y: auto; padding-right: 10px;">
          ${renderSection('Supervisores A Actualizar', supervisores, false)}
          ${renderSection('Gerentes A Actualizar', gerentes, false)}
        </div>
      </div>
    </div>
  `;
}

function newModalImportColaboradores() {
  const modal = new tingle.modal({
    footer: true,
    closeMethods: ["overlay", "button", "escape"],
    cssClass: ["modalContainerImport"],
    onOpen: function () {
      const el = document.querySelector("#agenciaColaboradorWrapper .onlySelect");
      if (typeof initSingleSelect === "function") initSingleSelect(el);
      enableImportColaboradoresButton();
    },
    onClose: function () {
      modal.destroy();
    },
  });

  modal.setContent(renderFormImportColaboradores());

  modal.addFooterBtn(
    "Previsualizar Importación",
    "tingle-btn tingle-btn--primary tingle-btn--primary-import",
    async function () {
      const fileEl = document.getElementById("importColaboradorInput");
      const agencia = (document.getElementById("agenciaColaboradorInput")?.value || "").trim();

      if (!agencia || !fileEl.files || !fileEl.files[0]) return;

      document.getElementById("wrapperLoader").style.display = "flex";

      const formData = new FormData();
      formData.append("file", fileEl.files[0]);
      formData.append("agencia", agencia);

      try {
        const resp = await fetch(urlPreviewImportColaboradores, {
          method: "POST",
          body: formData,
          headers: { "X-CSRFToken": getRawCsrfToken() },
        });
        const data = await resp.json();
        document.getElementById("wrapperLoader").style.display = "none";

        if (!resp.ok || !data.status) {
          alert(data.message || "Error al previsualizar la importación");
          return;
        }

        // Si salió bien, mostramos el preview modal
        modal.close();
        modal.destroy();
        showPreviewModalColaboradores(data, agencia);

      } catch (e) {
        document.getElementById("wrapperLoader").style.display = "none";
        alert("Error de red.");
      }
    }
  );

  modal.addFooterBtn("Cancelar", "tingle-btn tingle-btn--default", function () {
    modal.close();
    modal.destroy();
  });

  modal.open();
  document.querySelector(".tingle-btn--primary-import").disabled = true;
}

function showPreviewModalColaboradores(data, agencia_id) {
  const modal = new tingle.modal({
    footer: true,
    closeMethods: ["overlay", "button", "escape"],
    cssClass: ["modalContainerImport"],
  });

  modal.setContent(renderPreviewImportColaboradores(data));

  modal.addFooterBtn("Confirmar Importación", "tingle-btn tingle-btn--primary", async function () {
    const listElements = document.querySelectorAll("#previewDataContainer li");
    const updates = [];
    const creates = [];

    listElements.forEach(el => {
      const isNew = el.getAttribute("data-isnew") === "true";
      const user_id = el.dataset.index;
      const rawNombre = el.querySelector("strong").textContent.trim();
      const dni = el.querySelector(".edit-dni").value;
      const alias = el.querySelector(".edit-alias").value;
      const cbu = el.querySelector(".edit-cbu").value;
      const entidad = el.querySelector(".edit-entidad").value;
      const fec_ingreso = el.querySelector(".edit-fec-ingreso").value;
      const fec_egreso = el.querySelector(".edit-fec-egreso").value;

      if (isNew) {
        const rango = el.querySelector(".edit-rango").value;
        creates.push({
          nombre: rawNombre, dni, alias, cbu, entidad_bancaria: entidad, fec_ingreso, fec_egreso, rango
        });
      } else {
        const srcArray = [...(data.vendedores||[]), ...(data.supervisores||[]), ...(data.gerentes||[])];
        const match = srcArray.find(x => x.nombre === rawNombre);
        updates.push({
          user_id: match ? match.user_id : null,
          nombre: rawNombre, dni, alias, cbu, entidad_bancaria: entidad, fec_ingreso, fec_egreso
        });
      }
    });

    document.getElementById("wrapperLoader").style.display = "flex";

    try {
      const resp = await fetch(urlConfirmImportColaboradores, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getRawCsrfToken()
        },
        body: JSON.stringify({ updates, creates, agencia: agencia_id })
      });

      const respData = await resp.json();
      document.getElementById("wrapperLoader").style.display = "none";

      if (!resp.ok || !respData.status) {
        alert(respData.message || "Error al confirmar la importación");
        return;
      }

      modal.close();
      modal.destroy();
      alert("Los datos se actualizaron correctamente.");
    } catch (e) {
      document.getElementById("wrapperLoader").style.display = "none";
      alert("Error de red.");
    }
  });

  modal.addFooterBtn("Cancelar", "tingle-btn tingle-btn--default", function () {
    modal.close();
    modal.destroy();
  });

  const hasAny = (data.vendedores || []).length > 0 || (data.supervisores || []).length > 0 || (data.gerentes || []).length > 0 || (data.nuevos || []).length > 0;
  if (!hasAny) {
    document.querySelector(".tingle-btn--primary").disabled = true;
  }

  modal.open();
}
