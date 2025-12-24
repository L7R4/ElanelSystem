// vanilla_table_module.js
// Tabla reusable: búsqueda, paginación, loader, filtros extra, selección múltiple opcional.
// Uso: import VanillaTable from "/static/js/vanilla_table_module.js";
//      new VanillaTable(container, options);

/**
 * @typedef {Object} Column
 * @property {string} id                // identificador único de la columna
 * @property {string} label             // texto del <th>
 * @property {string|function} accessor // "ruta.anidada" o (row)=>any
 * @property {boolean} [html]           // si true, renderiza innerHTML (XSS: solo contenido controlado)
 * @property {boolean} [hidden]         // si true, comienza oculta (sin columnPicker, quedará oculta)
 * @property {string}  [className]      // clases extra para celdas/encabezado
 * @property {function} [onRowClick]    // (row, idx, event, api)=>void — click en una fila
 */

/**
 * @typedef {Object} Options
 * @property {Column[]} columns
 * @property {number}   [pageSize=10]
 * @property {boolean}  [remoteSearch=false]  // si true, el backend filtra/pagina
 * @property {string[]} [searchFields]        // campos para búsqueda local
 * @property {function} [fetchData]           // async ({page,pageSize,query,filters,signal}) => {data,total}
 * @property {function} [mapItem]             // (item)=>item (opcional)
 * @property {function} [renderExtraFilters]  // (el, api)=>void — slot HTML personalizado
 * @property {boolean}  [injectStyles=true]   // inyectar estilos por defecto
 * @property {string}   [emptyText="Sin resultados"]
 * @property {boolean}  [seleccionMultiple=false] // activa columna de selección
 * @property {string|function} [rowId]        // "id" | "cliente.id" | (row,idx)=>any
 * @property {function} [onSelectionChange]   // (ids, rows)=>void
 * @property {boolean}  [columnPicker=false]  // si true, muestra UI para ocultar/mostrar columnas
 */

export default class VanillaTable {
  /** @param {HTMLElement} container @param {Options} options */
  constructor(container, options) {
    if (!container) throw new Error("VanillaTable: container requerido");
    this.root = container;
    this.opt = Object.assign(
      {
        pageSize: 10,
        remoteSearch: false,
        searchFields: [],
        injectStyles: true,
        emptyText: "Sin resultados",
        seleccionMultiple: false,
        columnPicker: false, // por pedido: desactivado por defecto
        pageSizeControl: false // seleccionar cantidad: desactivado por defecto
      },
      options || {}
    );

    if (!Array.isArray(this.opt.columns) || this.opt.columns.length === 0) {
      throw new Error("VanillaTable: 'columns' es obligatorio");
    }

    // Estado
    this.state = {
      page: 1,
      pageSize: this.opt.pageSize,
      total: 0,
      query: "",
      filters: {},
      data: [],
      loading: false,
      visibleCols: new Set(this.opt.columns.filter(c => !c.hidden).map(c => c.id)),
    };

    // Selección persistente (ids como strings)
    this._selection = new Set();
    this._abort = null; // AbortController para fetch en curso

    // Montaje
    this._mount();
    if (this.opt.injectStyles) this._injectStyles();

    // Slot filtros extra
    if (typeof this.opt.renderExtraFilters === "function") {
      this.opt.renderExtraFilters(this.$extra, this._publicAPI());
    }

    // Primera carga
    this.reload();
  }

  // ===================== API Pública =====================
  _publicAPI() {
    return {
      reload: () => this.reload(),
      setFilter: (k, v) => {
        if (v === undefined || v === null || v === "") delete this.state.filters[k];
        else this.state.filters[k] = v;
      },
      getState: () => ({ ...this.state }),
      goToPage: (p, opts) => this._goToPage(p, opts),
      showColumn: (id) => this._toggleColumn(id, true),
      hideColumn: (id) => this._toggleColumn(id, false),
      setQuery: (q) => { this.state.query = q || ""; },

      // Selección
      getSelected: () => {
        const ids = Array.from(this._selection);
        const rows = this.state.data.filter((row, idx) =>
          this._selection.has(this._rowIdToString(this._getRowId(row, idx)))
        );
        return { ids, rows };
      },
      clearSelection: () => {
        this._selection.clear();
        this._renderRows();
        this._syncHeaderSelectAll();
        this._emitSelection();
      },
      selectAllCurrentPage: () => {
        this.state.data.forEach((row, idx) => {
          const id = this._rowIdToString(this._getRowId(row, idx));
          this._selection.add(id);
        });
        this._renderRows();
        this._syncHeaderSelectAll();
        this._emitSelection();
      },
      deselectAllCurrentPage: () => {
        this.state.data.forEach((row, idx) => {
          const id = this._rowIdToString(this._getRowId(row, idx));
          this._selection.delete(id);
        });
        this._renderRows();
        this._syncHeaderSelectAll();
        this._emitSelection();
      },
    };
  }

  // ===================== Montaje =====================
  _mount() {
    this.root.classList.add("vt-wrapper");
    const pageSizeUI = this.opt.pageSizeControl
    ? `<select class="vt-page-size" aria-label="Filas por página">
        <option value="10">10</option>
        <option value="25">25</option>
        <option value="50">50</option>
        <option value="100">100</option>
      </select>`
    : "";

    const columnsUI = this.opt.columnPicker
      ? `
      <div class="vt-columns">
        <button class="vt-columns-btn" type="button" aria-haspopup="true" aria-expanded="false">Columnas ▾</button>
        <div class="vt-columns-menu" role="menu" hidden></div>
      </div>`
      : "";

    this.root.innerHTML = `
      <div class="vt-toolbar">
        <div class="vt-left">
          <div class="vt-search-wrap">
            <input class="input-read-write-default vt-search" type="search" placeholder="Buscar..." aria-label="Buscar" />
          </div>
          ${columnsUI}
        </div>
        <div class="vt-right">
          <div class="vt-extra"></div>
        </div>
      </div>

      <div class="vt-table-wrap">
        <table class="vt-table" role="table">
          <thead><tr></tr></thead>
          <tbody></tbody>
        </table>
        <div class="vt-loader">
          <div class="vt-spinner" aria-hidden="true"></div>
          <div class="vt-loading-text">Cargando...</div>
        </div>
      </div>

      <div class="vt-pagination" role="navigation" aria-label="Paginación">
        <button class="vt-prev" type="button">◀</button>
        <span class="vt-page-info"></span>
        <button class="vt-next" type="button">▶</button>
        ${pageSizeUI}
      </div>
    `;

    // Refs
    this.$theadRow = this.root.querySelector("thead tr");
    this.$tbody = this.root.querySelector("tbody");
    this.$search = this.root.querySelector(".vt-search");
    this.$loader = this.root.querySelector(".vt-loader");
    this.$pageInfo = this.root.querySelector(".vt-page-info");
    this.$prev = this.root.querySelector(".vt-prev");
    this.$next = this.root.querySelector(".vt-next");
    this.$pageSize = this.root.querySelector(".vt-page-size");
    this.$extra = this.root.querySelector(".vt-extra");

    // Column picker refs (si existe)
    this.$columnsWrap = this.root.querySelector(".vt-columns") || null;
    this.$menu = this.root.querySelector(".vt-columns-menu") || null;
    this.$btnMenu = this.root.querySelector(".vt-columns-btn") || null;
    

    // Listeners base
    this.$search.addEventListener("input", this._debounce(() => {
        this.state.query = this.$search.value.trim();
        this._goToPage(1, { force: true });   // ← forzar reload aunque ya estés en page 1
    }, 300));

    this.$prev.addEventListener("click", () => this._goToPage(this.state.page - 1));
    this.$next.addEventListener("click", () => this._goToPage(this.state.page + 1));

    if (this.$pageSize) {
      this.$pageSize.value = String(this.state.pageSize);
      this.$pageSize.addEventListener("change", () => {
        this.state.pageSize = parseInt(this.$pageSize.value, 10) || 10;
        this._goToPage(1, { force: true });
      });
    }

    // Selección por fila (delegado)
    this.$tbody.addEventListener("change", (e) => {
      const target = e.target;
      if (target && target.classList.contains("vt-row-select")) {
        const id = target.getAttribute("data-id");
        if (target.checked) this._selection.add(id);
        else this._selection.delete(id);
        this._syncHeaderSelectAll();
        this._emitSelection();
      }
    });

    // Column picker (opcional)
    if (this.opt.columnPicker && this.$btnMenu && this.$menu) {
      this.$btnMenu.addEventListener("click", () => this._toggleMenu());
      document.addEventListener("click", (e) => {
        if (!this.$menu.contains(e.target) && !this.$btnMenu.contains(e.target)) {
          this._closeMenu();
        }
      });
    }

    this._renderColumns();
    if (this.opt.columnPicker) this._renderMenu();
  }

  // ===================== Column Picker (opcional) =====================
  _toggleMenu(open) {
    if (!this.opt.columnPicker || !this.$menu || !this.$btnMenu) return;
    const willOpen = open ?? this.$menu.hasAttribute("hidden");
    if (willOpen) {
      this.$menu.removeAttribute("hidden");
      this.$btnMenu.setAttribute("aria-expanded", "true");
    } else {
      this._closeMenu();
    }
  }

  _closeMenu() {
    if (!this.opt.columnPicker || !this.$menu || !this.$btnMenu) return;
    this.$menu.setAttribute("hidden", "");
    this.$btnMenu.setAttribute("aria-expanded", "false");
  }

  _renderMenu() {
    if (!this.opt.columnPicker || !this.$menu) return;

    const all = this.opt.columns.map(col => {
      const checked = this.state.visibleCols.has(col.id) ? "checked" : "";
      return `<label class="vt-col-item"><input type="checkbox" data-col="${col.id}" ${checked}/> ${col.label}</label>`;
    }).join("");

    this.$menu.innerHTML = `
      <div class="vt-col-actions">
        <button type="button" class="vt-col-all">Todas</button>
        <button type="button" class="vt-col-none">Ninguna</button>
      </div>
      ${all}
    `;

    this.$menu.querySelectorAll("input[type=checkbox]").forEach(chk => {
      chk.addEventListener("change", (e) => {
        const id = e.target.getAttribute("data-col");
        if (e.target.checked) this.state.visibleCols.add(id); else this.state.visibleCols.delete(id);
        this._renderColumns();
        this._renderRows();
      });
    });

    this.$menu.querySelector(".vt-col-all").addEventListener("click", () => {
      this.opt.columns.forEach(c => this.state.visibleCols.add(c.id));
      this._renderColumns(); this._renderRows();
    });
    this.$menu.querySelector(".vt-col-none").addEventListener("click", () => {
      this.state.visibleCols.clear();
      this._renderColumns(); this._renderRows();
    });
  }

  // ===================== Render =====================
  _isSelectionEnabled() { return !!this.opt.seleccionMultiple; }

  _renderColumns() {
    const visible = this.opt.columns.filter(c => this.state.visibleCols.has(c.id));
    let header = "";

    // checkbox master (si selección)
    if (this._isSelectionEnabled()) {
      header += `<th class="vt-select-col"><input type="checkbox" class="vt-select-all" aria-label="Seleccionar todo"/></th>`;
    }

    header += visible.map(c => `<th class="${c.className || ""}">${c.label}</th>`).join("");
    this.$theadRow.innerHTML = header;

    // bind master checkbox
    const master = this.$theadRow.querySelector(".vt-select-all");
    if (master) {
      master.addEventListener("change", () => {
        const checks = this.$tbody.querySelectorAll(".vt-row-select");
        checks.forEach((chk) => {
          chk.checked = master.checked;
          const id = chk.getAttribute("data-id");
          if (master.checked) this._selection.add(id);
          else this._selection.delete(id);
        });
        this._syncHeaderSelectAll();
        this._emitSelection();
      });
    }
  }

  _renderRows() {
    const visible = this.opt.columns.filter(c => this.state.visibleCols.has(c.id));
    const extraCols = this._isSelectionEnabled() ? 1 : 0;

    if (!this.state.loading && this.state.data.length === 0) {
      this.$tbody.innerHTML = `<tr><td class="vt-empty" colspan="${(visible.length || 1) + extraCols}">${this.opt.emptyText}</td></tr>`;
      return;
    }

    const rows = this.state.data.map((row, idx) => {
      let cells = "";

      if (this._isSelectionEnabled()) {
        const rawId = this._getRowId(row, idx);
        const id = this._rowIdToString(rawId);
        const checked = this._selection.has(id) ? "checked" : "";
        const idAttr = String(id).replaceAll('"', "&quot;");
        cells += `<td class="vt-select-col"><input type="checkbox" class="vt-row-select" data-id="${idAttr}" ${checked}></td>`;
      }

      cells += visible.map(col => {
        const v = this._getValue(row, col.accessor);
        if (col.html) return `<td class="${col.className || ""}">${v ?? ""}</td>`;
        return `<td class="${col.className || ""}">${this._escape(String(v ?? ""))}</td>`;
      }).join("");

      // data-idx para recuperar la fila
      return `<tr data-idx="${idx}">${cells}</tr>`;
    }).join("");

    this.$tbody.innerHTML = rows;

    // sincronizar master
    this._syncHeaderSelectAll();

    // ====== NUEVO: click delegado sobre tbody ======
    // Evita duplicar handlers: remueve uno anterior si existiera
    if (this._rowClickHandler) {
      this.$tbody.removeEventListener("click", this._rowClickHandler, true);
    }
    this._rowClickHandler = (e) => {
      // Ignorar clicks en elementos interactivos
      if (e.target.closest('a, button, input, label, textarea, select')) return;

      // Si está habilitada la selección y se clickeó la celda del checkbox, no disparar
      if (e.target.closest('.vt-select-col')) return;

      // Buscar el <tr> más cercano con data-idx
      const tr = e.target.closest('tr[data-idx]');
      if (!tr) return;

      const idx = Number(tr.getAttribute('data-idx'));
      if (Number.isNaN(idx)) return;

      const row = this.state.data[idx];
      if (!row) return;

      if (typeof this.opt.onRowClick === "function") {
        this.opt.onRowClick(row, idx, e, this._publicAPI());
      }
    };
    this.$tbody.addEventListener("click", this._rowClickHandler, true);
  }

  _updatePaginationUI() {
    const max = Math.max(1, Math.ceil(this.state.total / this.state.pageSize));
    this.$prev.disabled = this.state.page <= 1;
    this.$next.disabled = this.state.page >= max;

    const start = this.state.total === 0 ? 0 : (this.state.page - 1) * this.state.pageSize + 1;
    const end = Math.min(this.state.page * this.state.pageSize, this.state.total);
    this.$pageInfo.textContent = `${start}-${end} de ${this.state.total}`;
  }

  // ===================== Utilidades =====================
  _escape(str) {
    return str
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  _getValue(row, accessor) {
    try {
      if (typeof accessor === "function") return accessor(row);
      if (typeof accessor === "string" && accessor) {
        const parts = accessor.split(".");
        let cur = row;
        for (const p of parts) cur = cur?.[p];
        return cur;
      }
      return row;
    } catch { return ""; }
  }

  _getRowId(row, idx) {
    try {
      if (typeof this.opt.rowId === "function") return this.opt.rowId(row, idx);
      if (typeof this.opt.rowId === "string" && this.opt.rowId) {
        return this._getValue(row, this.opt.rowId);
      }
      if (row && Object.prototype.hasOwnProperty.call(row, "id")) return row.id;
      return `__idx_${(this.state.page - 1) * this.state.pageSize + idx}`;
    } catch {
      return `__idx_${(this.state.page - 1) * this.state.pageSize + idx}`;
    }
  }

  _rowIdToString(id) { return id != null ? String(id) : ""; }

  _syncHeaderSelectAll() {
    if (!this._isSelectionEnabled()) return;
    const master = this.$theadRow.querySelector(".vt-select-all");
    if (!master) return;

    const checks = Array.from(this.$tbody.querySelectorAll(".vt-row-select"));
    const total = checks.length;
    const selectedOnPage = checks.filter(chk => chk.checked).length;

    master.indeterminate = selectedOnPage > 0 && selectedOnPage < total;
    master.checked = total > 0 && selectedOnPage === total;
  }

  _emitSelection() {
    if (typeof this.opt.onSelectionChange === "function") {
      const { ids, rows } = this._publicAPI().getSelected();
      this.opt.onSelectionChange(ids, rows);
    }
  }

  _debounce(fn, ms) {
    let t;
    return (...args) => {
      clearTimeout(t);
      t = setTimeout(() => fn.apply(this, args), ms);
    };
  }

  _showLoader(show) {
    this.state.loading = !!show;
    if (this.$loader) this.$loader.style.display = show ? "flex" : "none";
  }

  _toggleColumn(id, show) {
    if (show) this.state.visibleCols.add(id); else this.state.visibleCols.delete(id);
    this._renderColumns();
    this._renderRows();
    if (this.opt.columnPicker) this._renderMenu();
  }

  // ===================== Ciclo de datos =====================
  _goToPage(p, { force = false } = {}) {
    const max = Math.max(1, Math.ceil(this.state.total / this.state.pageSize));
    const newP = Math.min(Math.max(1, p), max);
    if (!force && newP === this.state.page && this.state.total !== 0) return;
    this.state.page = newP;
    this.reload();
    }

  async reload() {
    this._showLoader(true);

    if (this._abort) this._abort.abort();
    this._abort = new AbortController();

    try {
      let data = [];
      let total = 0;

      if (typeof this.opt.fetchData === "function") {
        const { page, pageSize, query, filters } = this.state;
        const result = await this.opt.fetchData({ page, pageSize, query, filters, signal: this._abort.signal });
        data = Array.isArray(result?.data) ? result.data : [];
        total = Number(result?.total || data.length || 0);
      } else {
        // fallback: data embebida en el contenedor
        const raw = this.root.getAttribute("data-items");
        const arr = raw ? JSON.parse(raw) : [];
        data = Array.isArray(arr) ? arr : [];
        total = data.length;
      }

      if (typeof this.opt.mapItem === "function") {
        data = data.map(this.opt.mapItem);
      }

      // Búsqueda local (si no es remota)
      if (!this.opt.remoteSearch && this.state.query) {
        const q = this.state.query.toLowerCase();
        const fields = this.opt.searchFields?.length ? this.opt.searchFields : this.opt.columns.map(c => c.id);
        data = data.filter(row =>
          fields.some(fid => String(this._getValue(row, fid) ?? "").toLowerCase().includes(q))
        );
        total = data.length;
      }

      // Paginación local si el backend no pagina/filtra
      if (!(typeof this.opt.fetchData === "function" && this.opt.remoteSearch)) {
        const start = (this.state.page - 1) * this.state.pageSize;
        data = data.slice(start, start + this.state.pageSize);
      }

      this.state.data = data;
      this.state.total = total;

      this._updatePaginationUI();
      this._renderRows();
    } catch (err) {
      if (err?.name !== "AbortError") {
        console.error("VanillaTable reload error:", err);
        const extraCols = this._isSelectionEnabled() ? 1 : 0;
        this.$tbody.innerHTML = `<tr><td class="vt-empty" colspan="${this.opt.columns.length + extraCols}">Error cargando datos</td></tr>`;
      }
    } finally {
      this._showLoader(false);
    }
  }

  // ===================== Estilos =====================
  _injectStyles() {
    if (document.getElementById("vt-styles")) return;
    const css = ``;
    const style = document.createElement("style");
    style.id = "vt-styles";
    style.textContent = css;
    document.head.appendChild(style);
  }
}
