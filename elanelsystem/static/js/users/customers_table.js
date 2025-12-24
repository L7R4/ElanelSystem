import VanillaTable from "../vanilla_components/vanilla_table_module.js";

const table = new VanillaTable(document.getElementById("customers_table"), {
  columns: [
    { id: "nro_cliente", label: "Nro Cliente", accessor: "nro_cliente" },
    { id: "nombre", label: "Nombre", accessor: "nombre" },
    { id: "dni", label: "DNI", accessor: "dni" },
    { id: "prov", label: "Provincia", accessor: "prov" },
    { id: "loc", label: "Localidad", accessor: "loc" },
    { id: "tel", label: "Teléfono", accessor: "tel" },
  ],
  pageSize: 20,
  remoteSearch: true,
  columnPicker: false,
  pageSizeControl: false, // 👈 oculta el selector de cantidad por página
  seleccionMultiple: false,
  rowId: "id",

  // Inyectamos tu select custom en el header (lado derecho)
  renderExtraFilters(el, api) {
    el.innerHTML = `
      <div data-perm="users.view_cliente" id="selectWrapperAgencia" class="wrapperInput wrapperSelectCustom">
          <h3 class="labelInput">Agencia</h3>
          <div class="containerInputAndOptions">
              <img id="tipoMonedaIconDisplay" class="iconDesplegar" src="${imgNext}" alt="">
              <input type="hidden" name="agencia" id="agenciaInput" placeholder ="Seleccionar" autocomplete="off">
              
              <div class="onlySelect pseudo-input-select-wrapper">
                  <h3></h3>
              </div>
              <ul class="list-select-custom options">
                  ${sucursalesDisponibles
                    .map(
                      (sd) => `
                      <li data-value="${sd.id}">${sd.pseudonimo}</li>
                  `
                    )
                    .join("")}
              </ul>
          </div>
      </div>
    `;

    const input = el.querySelector("#selectWrapperAgencia .onlySelect");
    // initSingleSelect(input);

    const hidden = el.querySelector("#agenciaInput");
    hidden.addEventListener("input", () => {
      console.log("as");
      api.setFilter("sucursal_id", hidden.value);
      api.goToPage(1, { force: true });
    });
  },

  onRowClick(row, _, e) {
    const clientId = row.id ?? row.nro_cliente ?? row.cliente_id;
    if (!clientId) return;
    const href = `/cliente/${clientId}/operaciones/`;
    if (e.ctrlKey || e.metaKey) window.open(href, "_blank");
    else window.location.href = href;
  },

  async fetchData({ page, pageSize, query, filters, signal }) {
    const qs = new URLSearchParams({ page, page_size: pageSize });
    if (query) qs.set("search", query); // tu view usa 'search'
    if (filters?.sucursal_id) qs.set("sucursal_id", filters.sucursal_id); // 👈 enviamos filtro

    const url = `/cliente/lista_clientes/?${qs.toString()}`;
    const res = await fetch(url, {
      signal,
      credentials: "include",
      headers: { Accept: "application/json" },
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(
        `HTTP ${res.status} ${res.statusText}. Body: ${text.slice(0, 120)}`
      );
    }
    const ct = res.headers.get("content-type") || "";
    if (!ct.includes("application/json")) {
      const text = await res.text();
      throw new Error(
        `Esperaba JSON pero recibí ${ct}. Respuesta: ${text.slice(0, 120)}`
      );
    }

    const j = await res.json();
    return {
      data: j.results ?? j.data ?? j ?? [],
      total: j.total ?? j.count ?? 0,
    };
  },
});
