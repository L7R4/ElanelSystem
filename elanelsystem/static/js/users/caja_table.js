import VanillaTable from "../vanilla_components/vanilla_table_module.js";

const ENDPOINT = "/ventas/movs_pagos/";
const REPORT_PDF_ENDPOINT = "/ventas/pdf/informe/";
const REPORT_XLSX_ENDPOINT = "/ventas/excel/informe/";

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

function updateReportLink({ query, filters }) {
  const a = document.querySelector(".wrapperButtonInforme a");
  if (!a) return;

  const qs = buildQS({
    search: query || "",
    ...(filters || {}),
    // limit: 400,
  });

  a.href = `${REPORT_ENDPOINT}?${qs.toString()}`;
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
          <div class="detail_item"><label>Fecha</label><p class="input-read-only-default">${escapeHtml(data?.fecha)}</p></div>
          <div class="detail_item"><label>Monto unitario</label><p class="input-read-only-default">${escapeHtml(data?.monto_por_chance_formatted ?? "-")}</p></div>
          <div class="detail_item"><label>Monto total</label><p class="input-read-only-default">${escapeHtml(data?.monto_formatted)}</p></div>
          <div class="detail_item"><label>N° Cuota</label><p class="input-read-only-default">${escapeHtml(data?.nro_cuota ?? "-")}</p></div>
          <div class="detail_item"><label>Recibo</label><p class="input-read-only-default">${escapeHtml(data?.nro_recibo ?? "-")}</p></div>
          <div class="detail_item"><label>Método de pago</label><p class="input-read-only-default">${escapeHtml(data?.metodo_pago ?? "-")}</p></div>
          <div class="detail_item"><label>Cobrador</label><p class="input-read-only-default">${escapeHtml(data?.cobrador ?? "-")}</p></div>
          <div class="detail_item"><label>Campaña (pago)</label><p class="input-read-only-default">${escapeHtml(data?.campana_de_pago ?? "-")}</p></div>
          <div class="detail_item"><label>Responsable</label><p class="input-read-only-default">${escapeHtml(data?.responsable ?? "-")}</p></div>
        </div>

        <h2 class="tittleModal sub">Venta</h2>

        <div class="detail_grid"> 
          <div class="detail_item"><label>N° Operación</label><p class="input-read-only-default">${escapeHtml(v?.nro_operacion ?? "-")}</p></div>
          <div class="detail_item"><label>Campaña (venta)</label><p class="input-read-only-default">${escapeHtml(v?.campania ?? "-")}</p></div>
          <div class="detail_item"><label>Agencia</label><p class="input-read-only-default">${escapeHtml(v?.agencia ?? "-")}</p></div>
          <div class="detail_item"><label>Chances</label><p class="input-read-only-default">${escapeHtml(v?.chances ?? "-")}</p></div>

        </div>

        <h2 class="tittleModal sub">Cliente</h2>

        <div class="detail_grid">
          <div class="detail_item"><label>Nombre</label><p class="input-read-only-default">${escapeHtml(c?.nombre ?? "-")}</p></div>
          <div class="detail_item"><label>N° Cliente</label><p class="input-read-only-default">${escapeHtml(c?.nro_cliente ?? "-")}</p></div>
          <div class="detail_item"><label>DNI</label><p class="input-read-only-default">${escapeHtml(c?.dni ?? "-")}</p></div>
        </div>
      </div>
    `;
  }

  // externo
  return `
    <div class="modal_detail">
      <h2 class="tittleModal">${escapeHtml(title)}</h2>

      <div class="detail_grid">
        <div class="detail_item"><label>Fecha</label><p class="input-read-only-default">${escapeHtml(data?.fecha)}</p></div>
        <div class="detail_item"><label>Movimiento</label><p class="input-read-only-default">${escapeHtml(data?.movimiento ?? "-")}</p></div>
        <div class="detail_item"><label>Monto</label><p class="input-read-only-default">${escapeHtml(data?.monto_formatted ?? "-")}</p></div>
        <div class="detail_item"><label>Concepto</label><p class="input-read-only-default">${escapeHtml(data?.concepto ?? "-")}</p></div>
        <div class="detail_item"><label>Método de pago</label><p class="input-read-only-default">${escapeHtml(data?.metodo_pago ?? "-")}</p></div>
        <div class="detail_item"><label>Agencia</label><p class="input-read-only-default">${escapeHtml(data?.agencia ?? "-")}</p></div>
        <div class="detail_item"><label>Ente</label><p class="input-read-only-default">${escapeHtml(data?.ente ?? "-")}</p></div>
        <div class="detail_item"><label>Campaña</label><p class="input-read-only-default">${escapeHtml(data?.campania ?? "-")}</p></div>
      </div>

      <h2 class="tittleModal sub"">Comprobante</h2>

      <div class="detail_grid">
        <div class="detail_item"><label>Tipo ID</label><p class="input-read-only-default">${escapeHtml(data?.tipoIdentificacion ?? "-")}</p></div>
        <div class="detail_item"><label>N° ID</label><p class="input-read-only-default">${escapeHtml(data?.nroIdentificacion ?? "-")}</p></div>
        <div class="detail_item"><label>Tipo Comp.</label><p class="input-read-only-default">${escapeHtml(data?.tipoComprobante ?? "-")}</p></div>
        <div class="detail_item"><label>N° Comp.</label><p class="input-read-only-default">${escapeHtml(data?.nroComprobante ?? "-")}</p></div>
        <div class="detail_item"><label>Denominación</label><p class="input-read-only-default">${escapeHtml(data?.denominacion ?? "-")}</p></div>
        <div class="detail_item"><label>Moneda</label><p class="input-read-only-default">${escapeHtml(data?.tipoMoneda ?? "-")}</p></div>
        <div class="detail_item"><label>Premio</label><p class="input-read-only-default">${data?.premio ? "Sí" : "No"}</p></div>
        <div class="detail_item"><label>Adelanto</label><p class="input-read-only-default">${data?.adelanto ? "Sí" : "No"}</p></div>
        <div class="detail_item"><label>Observaciones</label><p class="input-read-only-default">${escapeHtml(data?.observaciones ?? "-")}</p></div>
      </div>
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
  // syncReportLinks({ query: state.query || "", filters: f || {} });
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
    onOpen: function () {
      buildSingleSelect(
        document.querySelector(
          "#selectWrapperSelectType .containerInputAndOptions",
        ),
        [
          { value: "", label: "Todos" },
          { value: "ingreso", label: "Ingreso" },
          { value: "egreso", label: "Egreso" },
        ],
        { searchable: false, value: f.tipo_mov || "" },
      );

      buildSingleSelect(
        document.querySelector(
          "#selectWrapperSelectOrigen .containerInputAndOptions",
        ),
        [
          { value: "", label: "Todos" },
          { value: "cannon", label: "Solo cannons" },
          { value: "externo", label: "Solo mov. externos" },
        ],
        { searchable: false, value: f.origen || "" },
      );
    },
  });

  modal.setContent(`
    <div class="modal_filter">
      <h2 class="tittleModal">Filtrar caja</h2>

      <div class="detail_grid">
        <div>
          <label style="margin-bottom:6px;font-weight:600;">Fecha</label>
          <input id="flt_fecha" class="input-read-write-default" type="date" value="${escapeHtml(f.fecha || "")}" />
        </div>

        <div>
          <label style="margin-bottom:6px;font-weight:600;">Concepto / Cliente</label>
          <input id="flt_concepto" class="input-read-write-default" type="text" placeholder="Ej: cuota, Juan, factura..." value="${escapeHtml(f.concepto || "")}" />
        </div>

        <div>
          <label style="margin-bottom:6px;font-weight:600;">N° cuota</label>
          <input id="flt_nro_cuota" class="input-read-write-default" type="number" min="0" step="1" placeholder="Ej: 3" value="${escapeHtml(f.nro_cuota || "")}" />
        </div>


        <div id="selectWrapperSelectType" class="wrapperInput wrapperSelectCustom">
            <h3 class="labelInput">Tipo</h3>
            <div class="containerInputAndOptions">
                <img id="tipoComprobanteIconDisplay"class="iconDesplegar" src="${imgNext}" alt="">
                <input type="hidden" name="flt_tipo" id="flt_tipo" value="${escapeHtml(f.tipo_mov || "")}" placeholder="Seleccionar" autocomplete="off">
                <div class="onlySelect pseudo-input-select-wrapper">
                    <h3></h3>
                </div>
                <ul class="list-select-custom options">
                </ul>
            </div>
        </div>
        
        <div id="selectWrapperSelectOrigen" class="wrapperInput wrapperSelectCustom">
            <h3 class="labelInput">Origen</h3>
            <div class="containerInputAndOptions">
                <img id="tipoComprobanteIconDisplay"class="iconDesplegar" src="${imgNext}" alt="">
                <input type="hidden" name="flt_origen" id="flt_origen" value="${escapeHtml(f.origen || "")}" placeholder="Seleccionar" autocomplete="off">
                <div class="onlySelect pseudo-input-select-wrapper">
                    <h3></h3>
                </div>
                <ul class="list-select-custom options">
                </ul>
            </div>
        </div>

        <div>
          <label style="margin-bottom:6px;font-weight:600;">Monto mín.</label>
          <input id="flt_monto_min" class="input-read-write-default" type="number" min="0" step="0.01" placeholder="0" value="${escapeHtml(f.monto_min || "")}" />
        </div>

        <div>
          <label style="margin-bottom:6px;font-weight:600;">Monto máx.</label>
          <input id="flt_monto_max" class="input-read-write-default" type="number" min="0" step="0.01" placeholder="100000" value="${escapeHtml(f.monto_max || "")}" />
        </div>
      </div>
    </div>
  `);

  // buildSingleSelect(
  //   modal.querySelector(
  //     "#selectWrapperMoneda .onlySelect.pseudo-input-select-wrapper",
  //   ),
  // );

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
      const origen = document.getElementById("flt_origen")?.value || "";
      api.setFilter("fecha", fecha);
      api.setFilter("concepto", concepto);
      api.setFilter("nro_cuota", nro_cuota);
      api.setFilter("tipo_mov", tipo);
      api.setFilter("monto_min", monto_min);
      api.setFilter("monto_max", monto_max);
      api.setFilter("origen", origen);

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
        "origen",
      ].forEach((k) => api.setFilter(k, ""));
      api.goToPage(1, { force: true });
      modal.close();
    },
  );

  modal.open();
}

const container = document.getElementById("caja_table");

function syncReportLinks({ query, filters }) {
  const qs = buildQS({
    search: query || "",
    ...(filters || {}),
  }).toString();

  const pdfA =
    document.getElementById("btn_generar_pdf") ||
    document.querySelector(".wrapperButtonInforme #btn_generar_pdf");
  const xlsA =
    document.getElementById("btn_generar_excel") ||
    document.querySelector(".wrapperButtonInforme #btn_generar_excel");

  if (pdfA)
    pdfA.href = qs ? `${REPORT_PDF_ENDPOINT}?${qs}` : REPORT_PDF_ENDPOINT;
  if (xlsA)
    xlsA.href = qs ? `${REPORT_XLSX_ENDPOINT}?${qs}` : REPORT_XLSX_ENDPOINT;
}

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
        <button id="vt_filter" class="button-open-modal button-default-style" type="button"> 
        <img id="filterIcon" class="filterIcon" src="/static/images/icons/filter_icon.svg" alt="">

        Filtrar
        </button>
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
    syncReportLinks({ query, filters });

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
