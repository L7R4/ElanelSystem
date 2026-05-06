function renderFormCleanExcel() {
    return `
      <div id="cleanExcelContainer" style="padding: 20px; min-height: 35vh; display: flex; flex-direction: column; justify-content: center; color: #333;">
        <div style="border-bottom: 2px solid var(--blue-0);">
          <h2 class="tittleModal" style="color: #2b6cb0; font-size: 2.2rem; margin-bottom: 25px; padding-bottom: 10px; font-family: 'Inter', sans-serif;">Limpiar Archivo Excel</h2>
        </div>
        <form id="cleanExcelForm" enctype="multipart/form-data" style="display: flex; flex-direction: column; gap: 20px; flex-grow: 1; margin-top:20px;">
          <style>
            .hover-container-file {
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
            <label for="cleanExcelInput">
               Seleccionar Archivo (Excel)
               <span id="nameFileCleanExcel" style="margin-top: 12px; font-size: 1.4rem; color: var(--blue-3); text-align: center; font-weight: 600; display: block; min-height: 20px;"></span>
            </label>
            <input type="file" id="cleanExcelInput" class="checkInput" accept=".xlsx, .xls, .xlsm" oninput="displayNameFileCleanExcel(this)" style="display:none;"/>
          </div>
        </form>
      </div>
    `;
}

function displayNameFileCleanExcel(input) {
    document.getElementById("nameFileCleanExcel").textContent = input.files[0] ? input.files[0].name : "";
    const btn = document.querySelector(".tingle-btn--primary-clean-preview");
    if (btn) {
        btn.disabled = !input.files[0];
        btn.classList.toggle("disabled", btn.disabled);
    }
}

function renderPreviewCleanExcel(sheets) {
    let sheetsHtml = Object.keys(sheets).map(key => {
        const s = sheets[key];
        const statusIcon = s.found ? '✅' : '❌';
        const color = s.found ? 'var(--blue-1)' : '#c53030';
        const bgColor = s.found ? '#f0fff4' : '#fff5f5';
        const realNameInfo = s.found ? `<span style="font-size: 1.2rem; color: #718096; margin-left:10px;">(Encontrada como: "${s.real_name}")</span>` : '';
        
        return `
          <li style="background-color: ${bgColor}; border: 1px solid ${color}40; padding: 12px 18px; margin-bottom: 8px; border-radius: 8px; display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.6rem;">${statusIcon}</span>
                <strong style="font-size: 1.5rem; color: ${color}">${key}</strong>
                ${realNameInfo}
            </div>
          </li>
        `;
    }).join('');

    return `
      <div id="previewCleanContainer" style="padding: 20px; font-family: 'Inter', sans-serif;">
        <h2 class="tittleModal" style="color: var(--third-color); font-size: 2.2rem; border-bottom: 2px solid var(--blue-1); padding-bottom: 12px; margin-bottom: 20px;">Resultado de Verificación</h2>
        <p style="font-size: 1.4rem; color: #4a5568; margin-bottom: 20px;">Se verificaron las hojas necesarias. Los nombres con espacios se detectaron correctamente.</p>
        <ul style="list-style: none; padding: 0; margin: 0;">
          ${sheetsHtml}
        </ul>
      </div>
    `;
}

function getRawCsrfToken() {
    const t = document.createElement('div');
    t.innerHTML = (typeof csrf_token !== 'undefined') ? csrf_token : '';
    const input = t.querySelector('input');
    return input ? input.value : ((typeof csrf_token !== 'undefined') ? csrf_token : '');
}

function newModalCleanExcel() {
    const modal = new tingle.modal({
        footer: true,
        closeMethods: ["overlay", "button", "escape"],
        cssClass: ["modalContainerImport"],
        onClose: function () {
            modal.destroy();
        },
    });

    modal.setContent(renderFormCleanExcel());

    modal.addFooterBtn(
        "Verificar Hojas",
        "tingle-btn tingle-btn--primary tingle-btn--primary-clean-preview",
        async function () {
            const fileEl = document.getElementById("cleanExcelInput");
            if (!fileEl.files[0]) return;

            document.getElementById("wrapperLoader").style.display = "flex";

            const formData = new FormData();
            formData.append("file", fileEl.files[0]);

            try {
                const resp = await fetch(urlPreviewCleanExcel, {
                    method: "POST",
                    body: formData,
                    headers: { "X-CSRFToken": getRawCsrfToken() },
                });
                
                if (!resp.ok) {
                    const text = await resp.text();
                    console.error("Error response:", text);
                    throw new Error(`Server returned ${resp.status}`);
                }

                const data = await resp.json();
                document.getElementById("wrapperLoader").style.display = "none";

                if (!data.status) {
                    alert(data.message || "Error al verificar el archivo");
                    return;
                }

                modal.close();
                modal.destroy();
                showPreviewModalClean(data.sheets, fileEl.files[0]);

            } catch (e) {
                document.getElementById("wrapperLoader").style.display = "none";
                console.error("Fetch error:", e);
                alert("Error al comunicar con el servidor: " + e.message);
            }
        }
    );

    modal.addFooterBtn("Cancelar", "tingle-btn tingle-btn--default", function () {
        modal.close();
        modal.destroy();
    });

    modal.open();
    document.querySelector(".tingle-btn--primary-clean-preview").disabled = true;
    document.querySelector(".tingle-btn--primary-clean-preview").classList.add("disabled");
}

function showPreviewModalClean(sheets, originalFile) {
    const modal = new tingle.modal({
        footer: true,
        closeMethods: ["overlay", "button", "escape"],
        cssClass: ["modalContainerImport"],
    });

    modal.setContent(renderPreviewCleanExcel(sheets));

    const allFound = Object.values(sheets).every(s => s.found);
    
    // Construir clases evitando tokens vacíos que rompen tingle/DOMTokenList
    let btnClasses = ["tingle-btn", "tingle-btn--primary"];
    if (!allFound) btnClasses.push("disabled");

    modal.addFooterBtn("Limpiar y Descargar", btnClasses.join(" "), async function () {
        if (!allFound) {
            alert("No se puede proceder si faltan hojas requeridas.");
            return;
        }

        document.getElementById("wrapperLoader").style.display = "flex";

        const formData = new FormData();
        formData.append("file", originalFile);

        try {
            const resp = await fetch(urlExecuteCleanExcel, {
                method: "POST",
                body: formData,
                headers: { "X-CSRFToken": getRawCsrfToken() },
            });

            if (!resp.ok) {
                const data = await resp.json();
                alert(data.message || "Error al procesar el archivo");
                document.getElementById("wrapperLoader").style.display = "none";
                return;
            }

            const blob = await resp.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            const lastDotIndex = originalFile.name.lastIndexOf('.');
            const baseName = lastDotIndex !== -1 ? originalFile.name.substring(0, lastDotIndex) : originalFile.name;
            a.download = `clean_${baseName}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            document.getElementById("wrapperLoader").style.display = "none";
            modal.close();
            modal.destroy();
        } catch (e) {
            document.getElementById("wrapperLoader").style.display = "none";
            alert("Error de red al procesar el archivo.");
        }
    });

    modal.addFooterBtn("Cancelar", "tingle-btn tingle-btn--default", function () {
        modal.close();
        modal.destroy();
    });

    if (!allFound) {
        document.querySelector(".tingle-btn--primary").disabled = true;
    }

    modal.open();
}
