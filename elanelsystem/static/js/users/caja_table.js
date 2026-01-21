import VanillaTable from "../vanilla_components/vanilla_table_module.js";

const ENDPOINT = "/ventas/movs_pagos/";

function escapeHtml(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function buildQS(params) {
  const qs = new URLSearchParams();
  Object.entries(params || {}).forEach(([k, v]) => {
    if (v === undefined || v === null || v === "") return;
    qs.set(k, String(v));
  });
  return qs;
}

async function fetchJSON(url, { signal } = {}) {
  const res = await fetch(url, {
    method: "GET",
    credentials: "same-origin",
    headers: { Accept: "application/json" },
    signal,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status} ${res.statusText} - ${text}`);
  }
  return res.json();
}

function updateResumen(summary) {
  const tbody = document.querySelector(".resum_table tbody");
  if (!tbody) return;
  if (!Array.isArray(summary)) {
    tbody.innerHTML = "";
    return;
  }

  tbody.innerHTML = summary
    .map((row) => {
      const isTotal = String(row.metodo_pago || "").toLowerCase() === "total";
      return `
        <tr ${isTotal ? 'style="font-weight:700"' : ""}>
          <td>${escapeHtml(row.metodo_pago ?? "")}</td>
          <td>${escapeHtml(row.neto ?? "-")}</td>
        </tr>
      `;
    })
    .join("\n");
}

function renderDetail(kind, data) {
  const title = kind === "pago" ? "Detalle de pago" : "Detalle de movimiento";

  if (kind === "pago") {
    const v = data?.venta || {};
    const c = v?.cliente || {};
    return `
      <div class="modal_detail">
        <h2 class="tittleModal">${escapeHtml(title)}</h2>

        <div class="detail_grid">
          <div><strong>Fecha:</strong> ${escapeHtml(data?.fecha)}</div>
          <div><strong>Monto:</strong> ${escapeHtml(data?.monto_formatted)}</div>
          <div><strong>N° Cuota:</strong> ${escapeHtml(data?.nro_cuota ?? "-")}</div>
          <div><strong>Recibo:</strong> ${escapeHtml(data?.nro_recibo ?? "-")}</div>
          <div><strong>Método de pago:</strong> ${escapeHtml(data?.metodo_pago ?? "-")}</div>
          <div><strong>Cobrador:</strong> ${escapeHtml(data?.cobrador ?? "-")}</div>
          <div><strong>Campaña (pago):</strong> ${escapeHtml(data?.campana_de_pago ?? "-")}</div>
          <div><strong>Responsable:</strong> ${escapeHtml(data?.responsable ?? "-")}</div>
        </div>

        <hr />
        <h3 style="margin: 0 0 10px 0;">Venta</h3>

        <div class="detail_grid">
          <div><strong>N° Operación:</strong> ${escapeHtml(v?.nro_operacion ?? "-")}</div>
          <div><strong>Campaña (venta):</strong> ${escapeHtml(v?.campania ?? "-")}</div>
          <div><strong>Agencia:</strong> ${escapeHtml(v?.agencia ?? "-")}</div>
        </div>

        <hr />
        <h3 style="margin: 0 0 10px 0;">Cliente</h3>

        <div class="detail_grid">
          <div><strong>Nombre:</strong> ${escapeHtml(c?.nombre ?? "-")}</div>
          <div><strong>N° Cliente:</strong> ${escapeHtml(c?.nro_cliente ?? "-")}</div>
          <div><strong>DNI:</strong> ${escapeHtml(c?.dni ?? "-")}</div>
        </div>
      </div>
    `;
  }

  // externo
  return `
    <div class="modal_detail">
      <h2 class="tittleModal">${escapeHtml(title)}</h2>

      <div class="detail_grid">
        <div><strong>Fecha:</strong> ${escapeHtml(data?.fecha)}</div>
        <div><strong>Movimiento:</strong> ${escapeHtml(data?.movimiento ?? "-")}</div>
        <div><strong>Monto:</strong> ${escapeHtml(data?.monto_formatted ?? "-")}</div>
        <div><strong>Concepto:</strong> ${escapeHtml(data?.concepto ?? "-")}</div>
        <div><strong>Método de pago:</strong> ${escapeHtml(data?.metodo_pago ?? "-")}</div>
        <div><strong>Agencia:</strong> ${escapeHtml(data?.agencia ?? "-")}</div>
        <div><strong>Ente:</strong> ${escapeHtml(data?.ente ?? "-")}</div>
        <div><strong>Campaña:</strong> ${escapeHtml(data?.campania ?? "-")}</div>
      </div>

      <hr />
      <h3 style="margin: 0 0 10px 0;">Comprobante</h3>

      <div class="detail_grid">
        <div><strong>Tipo ID:</strong> ${escapeHtml(data?.tipoIdentificacion ?? "-")}</div>
        <div><strong>N° ID:</strong> ${escapeHtml(data?.nroIdentificacion ?? "-")}</div>
        <div><strong>Tipo Comp.:</strong> ${escapeHtml(data?.tipoComprobante ?? "-")}</div>
        <div><strong>N° Comp.:</strong> ${escapeHtml(data?.nroComprobante ?? "-")}</div>
        <div><strong>Denominación:</strong> ${escapeHtml(data?.denominacion ?? "-")}</div>
        <div><strong>Moneda:</strong> ${escapeHtml(data?.tipoMoneda ?? "-")}</div>
        <div><strong>Premio:</strong> ${data?.premio ? "Sí" : "No"}</div>
        <div><strong>Adelanto:</strong> ${data?.adelanto ? "Sí" : "No"}</div>
      </div>

      <hr />
      <h3 style="margin: 0 0 10px 0;">Observaciones</h3>
      <div>${escapeHtml(data?.observaciones ?? "-")}</div>
    </div>
  `;
}

async function openDetailModal(row, { signal } = {}) {
  const kind = row?.kind;
  const pk = row?.pk;
  if (!kind || !pk) return;

  const url = `${ENDPOINT}${encodeURIComponent(kind)}/${encodeURIComponent(pk)}/`;
  const data = await fetchJSON(url, { signal });

  const modal = new tingle.modal({
    footer: true,
    closeMethods: ["button", "escape"],
    cssClass: ["modalContainerFilter"],
    onClose: function () {
      modal.destroy();
    },
  });

  modal.setContent(renderDetail(data?.kind, data?.data));
  modal.addFooterBtn(
    "Cerrar",
    "tingle-btn tingle-btn--default button-default-style",
    function () {
      modal.close();
    },
  );
  modal.open();
}

function openFiltersModal(api) {
  const state = api.getState?.() || { filters: {} };
  const f = state.filters || {};

  const modal = new tingle.modal({
    footer: true,
    closeMethods: ["button", "escape"],
    cssClass: ["modalContainerFilter"],
    onClose: function () {
      modal.destroy();
    },
  });

  modal.setContent(`
    <div class="modal_filter">
      <h2 class="tittleModal">Filtrar movimientos</h2>

      <div class="detail_grid">
        <label>
          <div style="margin-bottom:6px;font-weight:600;">Fecha</div>
          <input id="flt_fecha" class="input-read-write-default" type="date" value="${escapeHtml(f.fecha || "")}" />
        </label>

        <label>
          <div style="margin-bottom:6px;font-weight:600;">Concepto / Cliente</div>
          <input id="flt_concepto" class="input-read-write-default" type="text" placeholder="Ej: cuota, Juan, factura..." value="${escapeHtml(f.concepto || "")}" />
        </label>

        <label>
          <div style="margin-bottom:6px;font-weight:600;">N° cuota</div>
          <input id="flt_nro_cuota" class="input-read-write-default" type="number" min="1" step="1" placeholder="Ej: 3" value="${escapeHtml(f.nro_cuota || "")}" />
        </label>

        <label>
          <div style="margin-bottom:6px;font-weight:600;">Tipo</div>
          <select id="flt_tipo" class="input-read-write-default">
            <option value="" ${!f.tipo_mov ? "selected" : ""}>Todos</option>
            <option value="ingreso" ${f.tipo_mov === "ingreso" ? "selected" : ""}>Ingreso</option>
            <option value="egreso" ${f.tipo_mov === "egreso" ? "selected" : ""}>Egreso</option>
          </select>
        </label>

        <label>
          <div style="margin-bottom:6px;font-weight:600;">Monto mín.</div>
          <input id="flt_monto_min" class="input-read-write-default" type="number" min="0" step="0.01" placeholder="0" value="${escapeHtml(f.monto_min || "")}" />
        </label>

        <label>
          <div style="margin-bottom:6px;font-weight:600;">Monto máx.</div>
          <input id="flt_monto_max" class="input-read-write-default" type="number" min="0" step="0.01" placeholder="100000" value="${escapeHtml(f.monto_max || "")}" />
        </label>
      </div>
      <p style="margin-top:10px;opacity:.7;">Tip: la búsqueda de arriba también filtra (cliente / concepto / comprobante).</p>
    </div>
  `);

  modal.addFooterBtn(
    "Aplicar",
    "tingle-btn tingle-btn--primary add-button-default",
    function () {
      const fecha = document.getElementById("flt_fecha")?.value || "";
      const concepto = document.getElementById("flt_concepto")?.value || "";
      const nro_cuota = document.getElementById("flt_nro_cuota")?.value || "";
      const tipo = document.getElementById("flt_tipo")?.value || "";
      const monto_min = document.getElementById("flt_monto_min")?.value || "";
      const monto_max = document.getElementById("flt_monto_max")?.value || "";

      api.setFilter("fecha", fecha);
      api.setFilter("concepto", concepto);
      api.setFilter("nro_cuota", nro_cuota);
      api.setFilter("tipo_mov", tipo);
      api.setFilter("monto_min", monto_min);
      api.setFilter("monto_max", monto_max);

      api.goToPage(1, { force: true });
      modal.close();
    },
  );

  modal.addFooterBtn(
    "Limpiar",
    "tingle-btn tingle-btn--default button-default-style",
    function () {
      [
        "fecha",
        "concepto",
        "nro_cuota",
        "tipo_mov",
        "monto_min",
        "monto_max",
      ].forEach((k) => api.setFilter(k, ""));
      api.goToPage(1, { force: true });
      modal.close();
    },
  );

  modal.open();
}

const container = document.getElementById("caja_table");

const table = new VanillaTable(container, {
  remoteSearch: true,
  pageSize: 20,
  rowId: "id",
  columns: [
    { id: "fecha", label: "Fecha", accessor: "fecha" },
    { id: "concepto", label: "Concepto", accessor: "concepto" },
    { id: "nro_cuota", label: "N° Cuota", accessor: "nro_cuota" },
    { id: "ingreso", label: "Ingreso", accessor: "ingreso" },
    { id: "egreso", label: "Egreso", accessor: "egreso" },
  ],

  renderExtraFilters: (el, api) => {
    el.innerHTML = `
      <div class="vt-header-actions">
        <button id="vt_filter" class="button-open-modal button-default-style" type="button">Filtrar</button>
        <button id="vt_new_ing" class="button-open-modal add-button-default" type="button">Nuevo ingreso</button>
        <button id="vt_new_egr" class="button-open-modal delete-button-default" type="button">Nuevo egreso</button>
      </div>
    `;

    el.querySelector("#vt_filter")?.addEventListener("click", () =>
      openFiltersModal(api),
    );

    // Disparamos eventos para que otros scripts (createNewMov.js) puedan engancharse
    el.querySelector("#vt_new_ing")?.addEventListener("click", () => {
      document.dispatchEvent(
        new CustomEvent("caja:new-ingreso", { bubbles: true }),
      );
    });
    el.querySelector("#vt_new_egr")?.addEventListener("click", () => {
      document.dispatchEvent(
        new CustomEvent("caja:new-egreso", { bubbles: true }),
      );
    });
  },

  fetchData: async ({ page, pageSize, query, filters, signal }) => {
    const qs = buildQS({
      page,
      page_size: pageSize,
      search: query || "",
      ...(filters || {}),
    });

    const url = `${ENDPOINT}?${qs.toString()}`;
    const data = await fetchJSON(url, { signal });

    updateResumen(data?.summary);
    return {
      data: Array.isArray(data?.results) ? data.results : [],
      total: Number(data?.count || 0),
    };
  },

  // Modal de detalle al click en fila
  onRowClick: async (row, idx, event, api) => {
    // Evitar abrir modal si el usuario está seleccionando texto
    const sel = window.getSelection?.();
    if (sel && String(sel).length > 0) return;
    await openDetailModal(row);
  },
});

// Permite que otros scripts refresquen la tabla sin acoplarse a la instancia
window.addEventListener("caja:reload", () => {
  try {
    table.reload();
  } catch {
    // noop
  }
});

export default table;
