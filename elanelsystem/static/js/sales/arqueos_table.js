// static/js/sales/arqueos_table.js
import VanillaTable from "/static/js/vanilla_components/vanilla_table_module.js";

const money = (v) => {
  const n = Number(v || 0);
  return new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "ARS",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(Number.isFinite(n) ? n : 0);
};

function buildPdfUrl(row) {
  // ✅ si tu JSON trae pdf_url (recomendado)
  if (row?.pdf_url) return row.pdf_url;

  // fallback: reemplaza /0/ por /pk/
  const base = String(window.urlPDFBase || "");
  return base.replace("/0/", `/${row.pk}/`);
}

let cache = null;

async function fetchAllArqueos(signal) {
  if (cache) return cache;

  const res = await fetch(window.urlOldArqueos, {
    signal,
    credentials: "include",
    headers: {
      Accept: "application/json",
      "X-Requested-With": "XMLHttpRequest",
    },
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}. ${text.slice(0, 140)}`);
  }

  const j = await res.json();
  cache = Array.isArray(j) ? j : j?.data || j?.results || [];
  return cache;
}

new VanillaTable(document.getElementById("arqueos_table"), {
  columns: [
    { id: "sucursal", label: "Agencia", accessor: "sucursal" },
    { id: "fecha", label: "Fecha", accessor: "fecha" },
    { id: "admin", label: "Admin", accessor: "admin" },
    { id: "responsable", label: "Responsable", accessor: "responsable" },
    {
      id: "totalPlanilla",
      label: "Total Planilla",
      accessor: (row) => money(row.totalPlanilla),
      className: "vt-right",
    },
    // opcional: columna “PDF” para dejarlo explícito
    {
      id: "pdf",
      label: "PDF",
      html: true,
      accessor: (row) => {
        const url = buildPdfUrl(row);
        return `<a href="${url}" target="_blank" rel="noopener">Abrir</a>`;
      },
      className: "vt-center",
    },
  ],
  pageSize: 20,
  remoteSearch: false, // ✅ búsqueda/paginación local
  columnPicker: false,
  pageSizeControl: false,
  seleccionMultiple: false,
  rowId: "pk",
  searchFields: ["sucursal", "fecha", "admin", "responsable"],

  onRowClick(row) {
    const url = buildPdfUrl(row);
    window.open(url, "_blank", "noopener");
  },

  renderExtraFilters(el, api) {
    el.innerHTML = `
      <div id="selectWrapperAgencia" class="wrapperTypeFilter wrapperSelectCustom inputWrapper">
        <h3 class="labelInput">Agencia</h3>
        <div class="containerInputAndOptions">
          <img class="iconDesplegar" src="${window.imgNext}" alt="">
          <input type="hidden" name="agencia_id" id="agenciaIdInput" placeholder="Seleccionar" autocomplete="off" readonly>
          <div class="onlySelect pseudo-input-select-wrapper"><h3></h3></div>
          <ul class="list-select-custom options" id="agenciasList">
            ${(window.sucursalesDisponibles || [])
              .map(
                (a) => `
              <li data-value="${a.id}">${a.pseudonimo}</li>
            `,
              )
              .join("")}
          </ul>
        </div>
      </div>

    `;

    // Inicializa tu select custom sobre el DOM recién inyectado
    // (tu módulo auto-bootstrapea en DOMContentLoaded, pero acá lo agregamos dinámico)
    if (typeof window.initCustomSingleSelects === "function") {
      window.initCustomSingleSelects();
    } else if (typeof window.initSingleSelect === "function") {
      window.initSingleSelect(el.querySelector("#selectWrapperAgencia"));
    }

    const hidden = el.querySelector("#agenciaIdInput");
    // const btnClean = el.querySelector("#btnCleanArqueosFilters");

    hidden.addEventListener("input", async () => {
      api.setFilter("agencia_id", hidden.value);
      api.goToPage(1, { force: true });
    });

    // btnClean.addEventListener("click", () => {
    //   // limpia el select
    //   if (typeof window.clearSelect === "function") {
    //     window.clearSelect(
    //       el.querySelector("#selectWrapperAgencia .containerInputAndOptions"),
    //     );
    //   } else {
    //     hidden.value = "";
    //   }
    //   api.setFilter("agencia_id", "");
    //   api.setQuery("");
    //   api.goToPage(1, { force: true });
    // });
  },

  async fetchData({ filters, signal }) {
    const all = await fetchAllArqueos(signal);

    let data = all;

    // Filtro por agencia (si tu JSON trae agencia_id)
    if (filters?.agencia_id) {
      const id = String(filters.agencia_id);
      data = data.filter((x) => String(x.agencia_id || "") === id);
    }

    return { data, total: data.length };
  },
});
