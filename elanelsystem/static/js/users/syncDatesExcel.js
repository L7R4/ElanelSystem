function renderFormSyncExcel() {
    return `
      <div id="syncExcelContainer" style="padding: 20px; min-height: 45vh; display: flex; flex-direction: column; justify-content: center; color: #333; font-family: 'Inter', sans-serif;">
        <div style="border-bottom: 2px solid var(--blue-0);">
          <h2 class="tittleModal" style="color: #2b6cb0; font-size: 2.2rem; margin-bottom: 25px; padding-bottom: 10px;">Sincronizar Fechas de Pago</h2>
        </div>
        <p style="margin-top: 10px; font-size: 1.4rem; color: #4a5568;">Seleccione el Excel actual y el archivo Backup para recuperar las fechas de pago faltantes en el Excel actual.</p>
        
        <form id="syncExcelForm" enctype="multipart/form-data" style="display: flex; flex-direction: column; gap: 20px; flex-grow: 1; margin-top:20px;">
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
              min-height: 110px;
              cursor: pointer;
              font-size: 1.5rem;
              color: var(--third-color, #4a5568);
              font-weight: 500;
              box-sizing: border-box;
              padding: 15px;
            }
          </style>

          <div class="containerSelectFile hover-container-file">
            <label for="syncExcelActualInput">
               1. Excel Actual
               <span id="nameFileSyncExcelActual" style="margin-top: 8px; font-size: 1.3rem; color: var(--blue-3); text-align: center; font-weight: 600; display: block; min-height: 20px;"></span>
            </label>
            <input type="file" id="syncExcelActualInput" accept=".xlsx, .xls, .xlsm" oninput="displayNameFileSyncExcel('syncExcelActualInput', 'nameFileSyncExcelActual')" style="display:none;"/>
          </div>

          <div class="containerSelectFile hover-container-file">
            <label for="syncExcelBackupInput">
               2. Excel Backup
               <span id="nameFileSyncExcelBackup" style="margin-top: 8px; font-size: 1.3rem; color: var(--blue-3); text-align: center; font-weight: 600; display: block; min-height: 20px;"></span>
            </label>
            <input type="file" id="syncExcelBackupInput" accept=".xlsx, .xls, .xlsm" oninput="displayNameFileSyncExcel('syncExcelBackupInput', 'nameFileSyncExcelBackup')" style="display:none;"/>
          </div>

        </form>
      </div>
    `;
}

function displayNameFileSyncExcel(inputId, spanId) {
    const input = document.getElementById(inputId);
    document.getElementById(spanId).textContent = input.files[0] ? input.files[0].name : "";
    checkSyncFiles();
}

function checkSyncFiles() {
    const actual = document.getElementById("syncExcelActualInput");
    const backup = document.getElementById("syncExcelBackupInput");
    const btn = document.querySelector(".tingle-btn--primary-sync-execute");
    
    if (btn) {
        if (actual && actual.files[0] && backup && backup.files[0]) {
            btn.disabled = false;
            btn.classList.remove("disabled");
        } else {
            btn.disabled = true;
            btn.classList.add("disabled");
        }
    }
}

function getRawCsrfTokenSync() {
    const t = document.createElement('div');
    t.innerHTML = (typeof csrf_token !== 'undefined') ? csrf_token : '';
    const input = t.querySelector('input');
    return input ? input.value : ((typeof csrf_token !== 'undefined') ? csrf_token : '');
}

function newModalSyncExcel() {
    const modal = new tingle.modal({
        footer: true,
        closeMethods: ["overlay", "button", "escape"],
        cssClass: ["modalContainerImport"],
        onClose: function () {
            modal.destroy();
        },
    });

    modal.setContent(renderFormSyncExcel());

    // Asegurarse de que al principio el btn esta disabled
    let btnClasses = ["tingle-btn", "tingle-btn--primary", "tingle-btn--primary-sync-execute", "disabled"];

    modal.addFooterBtn(
        "Sincronizar y Descargar",
        btnClasses.join(" "),
        async function () {
            const fileActual = document.getElementById("syncExcelActualInput").files[0];
            const fileBackup = document.getElementById("syncExcelBackupInput").files[0];
            
            if (!fileActual || !fileBackup) return;

            document.getElementById("wrapperLoader").style.display = "flex";

            const formData = new FormData();
            formData.append("file_actual", fileActual);
            formData.append("file_backup", fileBackup);

            try {
                const resp = await fetch(urlExecuteSyncExcel, {
                    method: "POST",
                    body: formData,
                    headers: { "X-CSRFToken": getRawCsrfTokenSync() },
                });
                
                if (!resp.ok) {
                    try {
                        const text = await resp.json();
                        alert("Error: " + (text.message || "Error al procesar el archivo"));
                    } catch(e) {
                        alert("Error de red al procesar el archivo.");
                    }
                    document.getElementById("wrapperLoader").style.display = "none";
                    return;
                }

                // Check for JSON response (error case handled by backend returning status: false 200 OK)
                const contentType = resp.headers.get("content-type");
                if (contentType && contentType.includes("application/json")) {
                    const data = await resp.json();
                    document.getElementById("wrapperLoader").style.display = "none";
                    if (!data.status) {
                        alert(data.message || "Error al sincronizar");
                    }
                    return;
                }

                // Success case - binary blob
                const updatedCount = resp.headers.get("X-Sync-Count");
                
                const blob = await resp.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                const lastDotIndex = fileActual.name.lastIndexOf('.');
                const baseName = lastDotIndex !== -1 ? fileActual.name.substring(0, lastDotIndex) : fileActual.name;
                a.download = `synced_${baseName}.xlsx`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);

                document.getElementById("wrapperLoader").style.display = "none";
                
                if (updatedCount !== null) {
                    alert(`Sincronización completada. Se actualizaron ${updatedCount} fechas de pago.`);
                } else {
                    alert("Sincronización completada y archivo descargado.");
                }

                modal.close();
                modal.destroy();

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
    // Disable btn until both files are selected
    const primaryBtn = document.querySelector(".tingle-btn--primary-sync-execute");
    if (primaryBtn) {
        primaryBtn.disabled = true;
    }
}
