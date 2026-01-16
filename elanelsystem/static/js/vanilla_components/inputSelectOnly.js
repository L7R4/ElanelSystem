// inputSelectOnly.js — módulo unificado y “drop-in”
// Estructura soportada (tu HTML actual):
// .containerInputAndOptions
//   ├─ <img.iconDesplegar>
//   ├─ <input type="hidden" name="...">
//   ├─ <div class="onlySelect pseudo-input-select-wrapper"><h3></h3></div>
//   └─ <ul class="list-select-custom options"><li data-value="...">Texto</li>...</ul>
//
// Opcional (para búsqueda): agregá la clase .select-search al wrapper padre del select
// (el bloque que hoy tiene .wrapperInput.wrapperSelectCustom). El módulo inyecta un <input> de búsqueda
// dentro del pseudo wrapper sin romper tu estructura.

(function () {
  "use strict";

  // ===== Utils
  const norm = (s) =>
    String(s || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");

  const cssEscape = (v) => {
    try {
      return CSS && CSS.escape ? CSS.escape(String(v)) : String(v);
    } catch {
      return String(v);
    }
  };

  const placeholderOf = (hidden) =>
    hidden?.getAttribute("placeholder") || "Seleccionar";

  const ensureNoResults = (list, text) => {
    let li = list.querySelector("li.no-results-message");
    if (!li) {
      li = document.createElement("li");
      li.className = "no-results-message";
      li.style.pointerEvents = "none";
      list.appendChild(li);
    }
    li.textContent = text || "No se encontraron resultados";
    li.style.display = "none";
    return li;
  };

  const clearSelection = (list) => {
    list
      .querySelectorAll("li.selected")
      .forEach((li) => li.classList.remove("selected"));
  };

  const getPartsFromContainer = (container) => {
    if (!container) return null;
    const wrapper =
      container.closest(".wrapperSelectCustom") || container.parentElement;
    const icon = container.querySelector(".iconDesplegar");
    const hidden = container.querySelector('input[type="hidden"]');
    const pseudo = container.querySelector(
      ".onlySelect.pseudo-input-select-wrapper"
    );
    const list =
      container.querySelector("ul.options, ul.list-select-custom, ul") || null;

    if (!hidden || !pseudo || !list) return null;

    const isSearch = !!(wrapper && wrapper.classList.contains("select-search"));
    return { wrapper, container, icon, hidden, pseudo, list, isSearch };
  };

  const isOpen = (list) => list.classList.contains("open");
  const openList = (parts) => {
    parts.list.classList.add("open");
    parts.icon && parts.icon.classList.add("open");
    try {
      if (typeof window.ordersZindexSelects === "function")
        window.ordersZindexSelects();
    } catch {}
  };
  const closeList = (parts) => {
    parts.list.classList.remove("open");
    parts.icon && parts.icon.classList.remove("open");
    parts.list
      .querySelectorAll("li.active")
      .forEach((li) => li.classList.remove("active"));
  };
  const toggleList = (parts) =>
    isOpen(parts.list) ? closeList(parts) : openList(parts);

  // ===== API builder por instancia
  function buildAPI(parts, display, searchInput) {
    const { list, hidden } = parts;

    const setSelectedLabel = (label) => {
      if (!label) {
        if (searchInput) {
          searchInput.value = "";
          searchInput.placeholder = placeholderOf(hidden);
        } else if (display) {
          display.textContent = placeholderOf(hidden);
          display.classList.add("placeholder");
        }
        return;
      }
      if (searchInput) searchInput.value = label;
      else if (display) {
        display.textContent = label;
        display.classList.remove("placeholder");
      }
    };

    const setValueAndLabel = (
      value,
      label,
      { fire = true, markSelected = true } = {}
    ) => {
      hidden.value = value == null ? "" : String(value);
      setSelectedLabel(label || "");

      if (markSelected) {
        clearSelection(list);
        const v = String(value ?? "");
        const li = list.querySelector(`li[data-value="${cssEscape(v)}"]`);
        if (li) li.classList.add("selected");
      }
      if (fire) {
        hidden.dispatchEvent(new Event("input", { bubbles: true }));
        hidden.dispatchEvent(new Event("change", { bubbles: true }));
      }
    };

    const setValue = (value, opts = {}) => {
      if (value == null || value === "") {
        // clear
        clearSelection(list);
        hidden.value = "";
        setSelectedLabel("");
        return;
      }
      const v = String(value);
      const li = list.querySelector(`li[data-value="${cssEscape(v)}"]`);
      if (li) {
        li.classList.add("selected");
        setSelectedLabel(li.textContent.trim());
        hidden.value = v;
        if (opts.fire) {
          hidden.dispatchEvent(new Event("input", { bubbles: true }));
          hidden.dispatchEvent(new Event("change", { bubbles: true }));
        }
      } else {
        // no existe el li: dejamos el hidden y label tal cual
        hidden.value = v;
        setSelectedLabel("");
      }
    };

    const getValue = () => ({
      value: hidden.value,
      label: searchInput
        ? searchInput.value
        : display?.textContent?.trim() || "",
    });

    const clear = () => {
      clearSelection(list);
      hidden.value = "";
      setSelectedLabel("");
      closeList(parts);
    };

    const setOptions = (options = []) => {
      // options: [{value, label}] | ['text','text2']
      list.innerHTML = "";
      const frag = document.createDocumentFragment();
      options.forEach((opt) => {
        const val =
          typeof opt === "object"
            ? String(opt.value ?? opt.label ?? "")
            : String(opt);
        const lab =
          typeof opt === "object"
            ? String(opt.label ?? opt.value ?? "")
            : String(opt);
        const li = document.createElement("li");
        li.setAttribute("data-value", val);
        li.textContent = lab;
        frag.appendChild(li);
      });
      frag.appendChild(ensureNoResults(list));
      list.appendChild(frag);
      clear(); // al cambiar opciones, limpiamos selección
    };

    return {
      setValue,
      setValueAndLabel,
      getValue,
      clear,
      setOptions,
      setSelectedLabel,
    };
  }

  // ===== Init una instancia
  function initOne(container, preValues = {}) {
    if (!container || container.dataset._selectOneInit === "1") return null;
    const parts = getPartsFromContainer(container);
    if (!parts) return null;
    container.dataset._selectOneInit = "1";

    const { wrapper, hidden, pseudo, list, icon, isSearch } = parts;

    let displayH3 = pseudo.querySelector("h3") || null;
    let searchInput = null;

    if (isSearch) {
      searchInput = pseudo.querySelector("input[type=text]");
      if (!searchInput) {
        searchInput = document.createElement("input");
        searchInput.type = "text";
        searchInput.autocomplete = "off";
        searchInput.className = "editable-product-input"; // tu clase
        searchInput.placeholder = placeholderOf(hidden);
        searchInput.setAttribute("aria-autocomplete", "list");
        pseudo.appendChild(searchInput);
      } else {
        searchInput.placeholder = placeholderOf(hidden);
      }
    } else {
      if (!displayH3) {
        displayH3 = document.createElement("h3");
        pseudo.appendChild(displayH3);
      }
    }

    const api = buildAPI(parts, displayH3, searchInput);

    // Estado inicial (preselección)
    const pre = preValues?.[hidden.name];
    if (pre && typeof pre === "object" && ("value" in pre || "label" in pre)) {
      api.setValueAndLabel(pre.value ?? "", pre.label ?? "", {
        fire: false,
        markSelected: true,
      });
    } else if (typeof pre === "string" || typeof pre === "number") {
      api.setValue(String(pre), { fire: false });
    } else if (hidden.value && String(hidden.value).trim()) {
      const v = String(hidden.value).trim();
      const li = list.querySelector(`li[data-value="${cssEscape(v)}"]`);
      if (li) {
        clearSelection(list);
        li.classList.add("selected");
        api.setSelectedLabel(li.textContent.trim());
      } else {
        api.setSelectedLabel("");
      }
    } else {
      api.setSelectedLabel("");
    }

    // Filtro (solo modo search)
    const noResults = ensureNoResults(list);
    const applyFilter = (q) => {
      const query = norm(q);
      let any = false;
      list.querySelectorAll("li").forEach((li) => {
        if (li.classList.contains("no-results-message")) return;
        const txt = norm(li.textContent.trim());
        const hit = query === "" || txt.includes(query);
        li.style.display = hit ? "" : "none";
        if (hit) any = true;
      });
      noResults.style.display = query !== "" && !any ? "block" : "none";
    };

    // Selección + toggle (si vuelvo a hacer click en el mismo, des-selecciona)
    const selectLi = (li) => {
      if (
        !li ||
        li.classList.contains("no-results-message") ||
        li.style.display === "none"
      )
        return;
      const val = li.getAttribute("data-value") || li.textContent.trim();
      const lab = li.textContent.trim();

      if (li.classList.contains("selected")) {
        // Toggle: estaba seleccionado → limpiar
        api.clear();
        return;
      }

      clearSelection(list);
      li.classList.add("selected");
      api.setValueAndLabel(val, lab, { fire: true, markSelected: false }); // ya marcamos arriba
      closeList(parts);
    };

    // Eventos
    const onIconClick = (e) => {
      e.stopPropagation();
      toggleList(parts);
      if (isSearch && searchInput && isOpen(list)) searchInput.focus();
    };
    icon && icon.addEventListener("click", onIconClick);

    const onContainerClick = (e) => {
      if (isSearch && searchInput && e.target === searchInput) {
        if (!isOpen(list)) openList(parts);
        return;
      }
      toggleList(parts);
      if (isSearch && searchInput && isOpen(list)) searchInput.focus();
    };
    parts.container.addEventListener("click", onContainerClick);

    const onListClick = (e) => {
      const li = e.target.closest("li");
      if (!li) return;
      selectLi(li);
    };
    list.addEventListener("click", onListClick);

    if (isSearch && searchInput) {
      const onInput = (e) => {
        if (hidden.value) hidden.value = "";
        clearSelection(list);
        applyFilter(e.target.value);
      };
      const onFocus = () => {
        applyFilter(searchInput.value);
        openList(parts);
      };
      const onKeyDown = (e) => {
        // Enter = si hay un li visible activo, seleccionar; si no, el primero visible
        if (e.key === "Enter") {
          e.preventDefault();
          let li = list.querySelector(
            "li.active:not(.no-results-message):not([style*='display: none'])"
          );
          if (!li)
            li = Array.from(list.querySelectorAll("li")).find(
              (x) =>
                x.style.display !== "none" &&
                !x.classList.contains("no-results-message")
            );
          if (li) selectLi(li);
        }
        // Escape = cerrar
        if (e.key === "Escape") {
          closeList(parts);
        }
        // Flechas = mover active
        if (e.key === "ArrowDown" || e.key === "ArrowUp") {
          e.preventDefault();
          const visibles = Array.from(list.querySelectorAll("li")).filter(
            (x) =>
              !x.classList.contains("no-results-message") &&
              x.style.display !== "none"
          );
          if (!visibles.length) return;
          let idx = visibles.findIndex((x) => x.classList.contains("active"));
          if (idx === -1) idx = 0;
          else
            idx =
              e.key === "ArrowDown"
                ? Math.min(idx + 1, visibles.length - 1)
                : Math.max(idx - 1, 0);
          list
            .querySelectorAll("li.active")
            .forEach((x) => x.classList.remove("active"));
          visibles[idx].classList.add("active");
          visibles[idx].scrollIntoView({ block: "nearest" });
        }
      };
      searchInput.addEventListener("input", onInput);
      searchInput.addEventListener("focus", onFocus);
      searchInput.addEventListener("keydown", onKeyDown);
    }

    // Cerrar al click fuera
    const onDocClick = (e) => {
      if (!parts.container.contains(e.target)) closeList(parts);
    };
    document.addEventListener("click", onDocClick);

    // Devolver API pública por instancia
    return api;
  }

  // ===== Init masivo
  function initAll(preValues = {}, root = document) {
    const apis = [];
    root.querySelectorAll(".containerInputAndOptions").forEach((container) => {
      // Solo si existe el pseudo wrapper de tu estructura
      if (!container.querySelector(".onlySelect.pseudo-input-select-wrapper"))
        return;
      const api = initOne(container, preValues);
      if (api) apis.push(api);
    });
    try {
      if (typeof window.ordersZindexSelects === "function")
        window.ordersZindexSelects();
    } catch {}
    return apis;
  }

  // ===== Helpers públicos (“comodines”)
  function findContainer(elOrSelector) {
    const el =
      typeof elOrSelector === "string"
        ? document.querySelector(elOrSelector)
        : elOrSelector;
    if (!el) return null;
    return el.classList?.contains("containerInputAndOptions")
      ? el
      : el.closest(".containerInputAndOptions");
  }

  // set value by {value,label} o solo value
  window.setSelectValue = function (
    elOrSelector,
    valueOrObj,
    opts = { fire: true, markSelected: true }
  ) {
    const container = findContainer(elOrSelector);
    if (!container) return false;
    const { hidden, pseudo, list } = getPartsFromContainer(container) || {};
    if (!hidden) return false;

    const h3 = pseudo?.querySelector("h3");
    const input = pseudo?.querySelector("input[type=text]");
    const api = buildAPI({ hidden, list, container }, h3, input);

    if (valueOrObj == null || valueOrObj === "") {
      api.clear();
      return true;
    }
    if (typeof valueOrObj === "object") {
      api.setValueAndLabel(valueOrObj.value, valueOrObj.label, opts);
    } else {
      api.setValue(String(valueOrObj), opts);
    }
    return true;
  };

  window.getSelectValue = function (elOrSelector) {
    const container = findContainer(elOrSelector);
    if (!container) return { value: "", label: "" };
    const { hidden, pseudo, list } = getPartsFromContainer(container) || {};
    const h3 = pseudo?.querySelector("h3");
    const input = pseudo?.querySelector("input[type=text]");
    const api = buildAPI({ hidden, list, container }, h3, input);
    return api.getValue();
  };

  window.clearSelect = function (elOrSelector) {
    const container = findContainer(elOrSelector);
    if (!container) return false;
    const { hidden, pseudo, list } = getPartsFromContainer(container) || {};
    const h3 = pseudo?.querySelector("h3");
    const input = pseudo?.querySelector("input[type=text]");
    const api = buildAPI({ hidden, list, container }, h3, input);
    api.clear();
    return true;
  };

  window.setSelectOptions = function (elOrSelector, options = []) {
    const container = findContainer(elOrSelector);
    if (!container) return false;
    const parts = getPartsFromContainer(container);
    if (!parts) return false;
    const { hidden, pseudo, list } = parts;
    const h3 = pseudo?.querySelector("h3");
    const input = pseudo?.querySelector("input[type=text]");
    const api = buildAPI(parts, h3, input);
    api.setOptions(options);
    return true;
  };

  // Crea (si hace falta) el <ul> y carga opciones, luego inicializa.
  // options: [{value, label}] | ['A','B',...]
  // opts: { value, label, searchable: boolean, placeholder: string }
  window.buildSingleSelect = function (elOrSelector, options = [], opts = {}) {
    const el =
      typeof elOrSelector === "string"
        ? document.querySelector(elOrSelector)
        : elOrSelector;
    if (!el) return null;

    // En tu estructura, el "pseudo" vive dentro del container
    const container = el.classList?.contains("containerInputAndOptions")
      ? el
      : el.closest(".containerInputAndOptions");
    if (!container) return null;

    // Aseguramos UL
    let list =
      container.querySelector("ul.options, ul.list-select-custom, ul") || null;
    if (!list) {
      list = document.createElement("ul");
      list.className = "list-select-custom options";
      container.appendChild(list);
    }

    // Aseguramos pseudo wrapper (ya existe en tu HTML)
    if (!container.querySelector(".onlySelect.pseudo-input-select-wrapper")) {
      const pseudo = document.createElement("div");
      pseudo.className = "onlySelect pseudo-input-select-wrapper";
      pseudo.appendChild(document.createElement("h3"));
      const hidden = container.querySelector('input[type="hidden"]');
      hidden && container.insertBefore(pseudo, list);
    }

    // Modo búsqueda agregando clase al wrapper externo
    if (opts.searchable) {
      const outer = container.closest(".wrapperSelectCustom");
      if (outer) outer.classList.add("select-search");
    }

    // placeholder
    const hidden = container.querySelector('input[type="hidden"]');
    if (hidden && opts.placeholder)
      hidden.setAttribute("placeholder", String(opts.placeholder));

    // Cargamos opciones
    window.setSelectOptions(container, options);

    // Init
    const api = initOne(container, {});
    if (api && (opts.value != null || opts.label != null)) {
      if (opts.label != null)
        api.setValueAndLabel(opts.value ?? "", opts.label ?? "", {
          fire: false,
          markSelected: true,
        });
      else api.setValue(String(opts.value ?? ""), { fire: false });
    }
    return api;
  };

  // Init masivo (escanea el DOM)
  window.initCustomSingleSelects = function (preValues = {}) {
    return initAll(preValues, document);
  };

  // Init 1 (si sólo querés un select recién insertado)
  window.initSingleSelect = function (
    selectWrapperOrContainer,
    preValues = {}
  ) {
    const el =
      typeof selectWrapperOrContainer === "string"
        ? document.querySelector(selectWrapperOrContainer)
        : selectWrapperOrContainer;

    if (!el) return null;

    const container = el.classList?.contains("containerInputAndOptions")
      ? el
      : el.closest(".containerInputAndOptions");

    if (!container) return null;
    return initOne(container, preValues);
  };

  // Bootstrap automático
  (function bootstrap() {
    const run = () => initAll({}, document);
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", run, { once: true });
    } else {
      run();
    }
  })();

  window.clearInputs = function clearInputs(requiredFields, scope, opts) {
    const options = Object.assign({ fire: true }, opts || {});
    const root = scope && scope.nodeType === 1 ? scope : document;

    // 1) Resolver el conjunto de elementos a limpiar
    let items = [];
    if (typeof requiredFields === "string") {
      items = Array.from(root.querySelectorAll(requiredFields));
    } else if (
      requiredFields &&
      typeof requiredFields.length === "number" &&
      requiredFields.length > 0
    ) {
      items = Array.from(requiredFields);
    } else {
      // Fallback: limpiar inputs típicos del form (excluye csrf y .notForm)
      items = Array.from(
        root.querySelectorAll(
          "input[type='hidden']:not(.notForm):not([name='csrfmiddlewaretoken'])," +
            "input[type='text']:not(.notForm):not([name='csrfmiddlewaretoken'])," +
            "input[type='number']:not(.notForm):not([name='csrfmiddlewaretoken'])"
        )
      );
    }

    // 2) Limpiar cada input
    items.forEach((el) => {
      if (!(el instanceof HTMLElement)) return;

      // a) Si es hidden y pertenece a un select custom, uso la API del módulo
      if (el.tagName === "INPUT" && el.type === "hidden") {
        const container = el.closest(".containerInputAndOptions");
        if (container) {
          if (typeof window.clearSelect === "function") {
            window.clearSelect(container); // quita .selected, cierra lista, restaura placeholder
          } else {
            // Fallback por si la API no está disponible
            el.value = "";
            const pseudo = container.querySelector(
              ".onlySelect.pseudo-input-select-wrapper"
            );
            const h3 = pseudo ? pseudo.querySelector("h3") : null;
            if (h3) {
              const ph = el.getAttribute("placeholder") || "Seleccionar";
              h3.textContent = ph;
              h3.classList.add("placeholder");
            }
            container
              .querySelectorAll("ul li.selected")
              .forEach((li) => li.classList.remove("selected"));
          }
          if (options.fire) {
            el.dispatchEvent(new Event("input", { bubbles: true }));
            el.dispatchEvent(new Event("change", { bubbles: true }));
          }
          return;
        }
      }

      // b) Inputs de texto / número comunes
      if (
        el.tagName === "INPUT" &&
        (el.type === "text" || el.type === "number" || el.type === "hidden")
      ) {
        el.value = "";
        if (options.fire) {
          el.dispatchEvent(new Event("input", { bubbles: true }));
          el.dispatchEvent(new Event("change", { bubbles: true }));
        }
      }
    });

    // 3) Extra: si el select está en modo búsqueda, vaciar el input de búsqueda y ocultar "no results"
    root.querySelectorAll(".containerInputAndOptions").forEach((container) => {
      const wrapper = container.closest(".wrapperSelectCustom");
      const isSearch = wrapper && wrapper.classList.contains("select-search");
      if (!isSearch) return;

      const searchInput = container.querySelector(
        ".onlySelect.pseudo-input-select-wrapper input[type='text']"
      );
      if (searchInput) {
        searchInput.value = "";
        if (options.fire) {
          searchInput.dispatchEvent(new Event("input", { bubbles: true }));
          searchInput.dispatchEvent(new Event("change", { bubbles: true }));
        }
      }

      const noRes = container.querySelector(
        "ul.list-select-custom li.no-results-message"
      );
      if (noRes) noRes.style.display = "none";
    });
  };
})();
