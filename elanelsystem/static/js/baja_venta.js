import { createAsyncUI, apiFetch } from './async_ui.js';

// Si tu página ya tiene inputs visibles con valores iniciales, los usamos como "semilla"
function readInitialValuesFromPage() {
  return {
    ventaId:   (typeof venta_id !== "undefined" && venta_id) || document.getElementById("venta_id")?.value || "",
    motivo:    document.getElementById("motivo")?.value?.trim() || "",
    desc:      document.getElementById("bajaObservacion")?.value?.trim() || "",
    porcentaje:document.getElementById("porcentage")?.value || ""  // puede venir vacío
  };
}

// Construye el HTML del modal completo
function buildBajaForm({ init }) {
  const { motivo = "", desc = "", porcentaje = "" } = init || {};
  return `
    <div class="modalBajaVenta__content">
      <h2>Dar de baja la venta</h2>

      <form id="formBajaVenta" class="form-baja">
        <div class="field">
          <label for="baja_motivo">Motivo</label>
          <input id="baja_motivo" class="input-read-write-default" type="text" placeholder="Motivo" value="${motivo}">
        </div>

        <div class="field">
          <label for="baja_desc">Descripción (opcional)</label>
          <textarea id="baja_desc" class="input-read-write-default" placeholder="Describe brevemente">${desc}</textarea>
        </div>

        <div class="field">
          <label for="baja_pct">Porcentaje a devolver</label>
          <div class="row">
            <input id="baja_pct" class="input-read-write-default" type="number" min="0" max="100" step="0.01"
                   value="${porcentaje}" readonly>
            <button type="button" id="editPctBtn" class="button-default-style">Editar</button>
          </div>
        </div>

        <!-- Bloque de contraseña (aparece solo si el usuario quiere editar %) -->
        <div id="passArea" class="pass-area" hidden>
          <label for="passInput">Contraseña</label>
          <input id="passInput" type="password" class="input-read-write-default" placeholder="Contraseña" autocomplete="current-password">

          <div class="pass-actions">
            <button type="button" id="validatePassBtn" class="add-button-default">Validar</button>
            <button type="button" id="cancelPassBtn" class="button-default-style">Cancelar</button>
          </div>

          <!-- Loader/estado de la validación -->
          <div data-pass-status></div>
        </div>

        <!-- Loader/estado principal (confirmar baja) -->
        <div data-status></div>
      </form>
    </div>
  `;
}

// Abre el modal completo
export function openBajaVentaModal() {
  const init = readInitialValuesFromPage();

  let uiMain;   // UI async para confirmar baja
  let uiPass;   // UI async para validar contraseña
  let willDestroy = false;

  const modal = new tingle.modal({
    footer: true,
    closeMethods: ['button','overlay'],
    cssClass: ['modalBajaVenta'],
    onClose: () => {
      // Abortá cualquier request activa
      if (uiMain?.isRunning()) uiMain.abort();
      if (uiPass?.isRunning()) uiPass.abort();
      willDestroy = true;
    }
  });

  modal.setContent(buildBajaForm({ init }));

  // Footer
  const btnConfirm = modal.addFooterBtn("Confirmar", "tingle-btn tingle-btn--primary add-button-default", onConfirm);
  const btnClose   = modal.addFooterBtn("Cancelar",  "tingle-btn tingle-btn--default button-default-style", onClose);

  // Destruir recién cuando termina la transición
  modal.modal.addEventListener('transitionend', () => {
    const isClosed = !modal.modal.classList.contains('tingle-modal--visible');
    if (willDestroy && isClosed) modal.destroy();
  });

  // Elementos del modal (scope)
  const root      = modal.modalBoxContent || modal.modal;
  const form      = root.querySelector("#formBajaVenta");
  const inpMotivo = root.querySelector("#baja_motivo");
  const inpDesc   = root.querySelector("#baja_desc");
  const inpPct    = root.querySelector("#baja_pct");
  const editPct   = root.querySelector("#editPctBtn");

  const passArea  = root.querySelector("#passArea");
  const inpPass   = root.querySelector("#passInput");
  const btnVal    = root.querySelector("#validatePassBtn");
  const btnCancel = root.querySelector("#cancelPassBtn");

  // Loader/estado principal
  const mountMain = root.querySelector("[data-status]");
  uiMain = createAsyncUI({
    mount: mountMain,
    texts: { working: "Procesando baja...", success: "Baja realizada", error: "No se pudo procesar la baja", canceled: "Cancelado" }
  });

  // Loader/estado para validar contraseña (inline)
  const mountPass = root.querySelector("[data-pass-status]");
  uiPass = createAsyncUI({
    mount: mountPass,
    texts: { working: "Verificando...", success: "Contraseña correcta", error: "Contraseña incorrecta", canceled: "Cancelado" }
  });

  // Mostrar el bloque de contraseña al querer editar
  editPct.addEventListener('click', () => {
    passArea.hidden = false;
    inpPass.focus();
  });

  // Validar contraseña → habilitar edición de porcentaje
  btnVal.addEventListener('click', async () => {
    const pwd = inpPass.value.trim();
    if (!pwd) return;

    await uiPass.exec(
      async ({ signal }) => {
        const resp = await apiFetch("/usuario/administracion/requestkey/", {
          method: 'POST',
          data: { pass: pwd, motivo: 'baja' },
          signal
        });
        if (!resp?.status) return { ok:false, message: resp?.message || 'Contraseña incorrecta' };
        return { ok:true, message:'Contraseña correcta' };
      },
      { buttons: null } // no hay botones de footer que deshabilitar acá
    ).then(res => {
      if (res?.ok) {
        // Habilitar edición del porcentaje y ocultar el bloque de pass
        inpPct.readOnly = false;
        inpPct.classList.add('enable'); // mantiene tu convención visual
        passArea.hidden = true;
        inpPass.value = "";
      }
    });
  });

  // Cancelar edición de contraseña
  btnCancel.addEventListener('click', () => {
    // no habilitamos porcentaje, solo ocultamos y limpiamos
    inpPass.value = "";
    passArea.hidden = true;
  });

  // Habilitar/Deshabilitar Confirmar según validación mínima (motivo requerido)
  function updateConfirmDisabled() {
    const valid = !!inpMotivo.value.trim();
    btnConfirm.disabled = uiMain.isRunning() || !valid;
  }
  root.addEventListener('input', updateConfirmDisabled);
  root.addEventListener('change', updateConfirmDisabled);
  updateConfirmDisabled();

  modal.open();

  // Confirmar baja (con loader/abort)
  async function onConfirm() {
    const ventaId = init.ventaId;
    const body = {
      porcentage:        inpPct.value.trim(),     // el backend decide si usa este valor según session flag
      motivo:            inpMotivo.value.trim(),
      motivoDescripcion: inpDesc.value.trim()
    };

    await uiMain.exec(
      async ({ signal }) => {
        const resp = await apiFetch(`/ventas/detalle_venta/${ventaId}/dar_baja/`, {
          method: 'POST',
          data: body,
          signal
        });
        if (!resp?.status) return { ok:false, message: resp?.message || "No se pudo realizar la baja" };
        return { ok:true, message:"Baja realizada", urlPDF: resp.urlPDF, urlUser: resp.urlUser };
      },
      {
        buttons: { confirmBtn: btnConfirm, closeBtn: btnClose },
        closeOnSuccess: true,
        onSuccessClose: () => {
          // Abrimos el PDF y redirigimos
          try { if (uiMain?.loader && uiMain?.loader.el) {} } catch {}
          // Pequeño delay para que el usuario vea "ok"
          setTimeout(() => {
            // abrir PDF si viene
            try { modal.close(); } catch {}
          }, 0);
        }
      }
    ).then(res => {
      if (res?.ok) {
        // Después de cerrar el modal:
        try { if (res.result?.urlPDF) window.open(res.result.urlPDF, "_blank"); } catch {}
        if (res.result?.urlUser) window.location.href = res.result.urlUser;
      }
    });
  }

  function onClose() {
    if (uiMain?.isRunning() || uiPass?.isRunning()) {
      uiMain?.abort();
      uiPass?.abort();
      setTimeout(() => modal.close(), 300);
    } else {
      modal.close();
    }
  }
}

// ========== Enlazar el botón principal "Dar baja" ==========
const buttonBaja = document.getElementById("bajaBtn");
buttonBaja?.addEventListener("click", openBajaVentaModal);

// (Opcional) Si querés exponer la función globalmente:
// window.openBajaVentaModal = openBajaVentaModal;
