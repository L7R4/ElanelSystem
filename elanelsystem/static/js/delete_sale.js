// delete_ventas.js (ESM)
import { openActionModal, apiFetch } from './async_ui.js';

// ====== UI ======
function buildDeleteContent() {
  return `
    <div class="modalDeleteVenta__content">
      <form id="formDeleteSale">
        <h1>¿Estás seguro que quieres eliminar este contrato?</h1>
        <div class="inputClaveWrapper">
          <p>Ingrese el <strong>N° de operación</strong> para confirmar</p>
          <input
            name="nro_operacion_delete"
            class="input-read-write-default"
            type="text"
            id="input_confirm_delete"
            autocomplete="off"
            inputmode="numeric"
            pattern="[0-9]*"
          >
        </div>
        <div data-status style="margin-top:.75rem;"></div>
      </form>
    </div>`;
}

// habilita Confirmar solo si hay algo escrito (puedes endurecer la validación si quieres dígitos estrictos)
function validateDelete(root) {
  const val = root.querySelector('#input_confirm_delete')?.value.trim() || '';
  return val.length > 0; // o: return /^\d+$/.test(val);
}

// llamado real al backend
async function runDelete({ root, signal }) {
  const nro = root.querySelector('#input_confirm_delete').value.trim();

  const resp = await apiFetch(deleteSaleUrl, {   // `deleteSaleUrl` expuesto globalmente por tu template
    method: 'POST',
    data: { nro_operacion_delete: nro },
    signal
  });

  if (!resp || resp.status !== true) {
    return { ok: false, message: resp?.message || 'No se pudo eliminar la venta' };
  }

  // devolvemos el redirect para usarlo al resolver el modal
  return { ok: true, message: 'Eliminado con éxito', urlRedirect: resp.urlRedirect };
}

// API pública para abrir el modal
export function openModalDeleteVenta() {
  return openActionModal({
    modalOpts: { cssClass: ['modalDeleteVenta'], closeMethods: ['button','overlay'] },
    buildContent: () => buildDeleteContent(),
    validate:      validateDelete,
    run:           runDelete,
    texts: {
      working:  'Eliminando venta...',
      success:  'Venta eliminada',
      error:    'Error de red. Intenta nuevamente.',
      canceled: 'Operación cancelada'
    },
    buttons: { confirm: 'Confirmar', cancel: 'Cerrar' },
    // statusSelector: '[data-status]' // opcional (por defecto auto-detecta data-status)
  }).then(res => {
    if (res?.ok && res.result?.urlRedirect) {
      // pequeño delay para que se vea el estado "success" antes de irse
      setTimeout(() => { window.location.href = res.result.urlRedirect; }, 400);
    }
    return res;
  });
}

// si quieres poder llamarlo desde HTML inline:
window.openModalDeleteVenta = openModalDeleteVenta;
