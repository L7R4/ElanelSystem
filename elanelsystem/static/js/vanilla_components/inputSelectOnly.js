// inputSelectOnly_unified.js
// Unifica:
// - Select custom simple (como vanilla_components/inputSelectOnly_v2.js.js)
// - Select con búsqueda (como inputSelectOnlySearch.js)
// Mantiene la MISMA estructura HTML (hidden + pseudo wrapper + ul.options + icon)

// ================= utils =================
const _norm = (s) =>
  String(s || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");

function _closestContainer(el) {
  return el?.closest?.(".containerInputAndOptions") || null;
}

function _getPartsFromContainer(container) {
  if (!container) return null;

  const wrapper =
    container.closest(".select-search") ||
    container.closest(".wrapperSelectCustom") ||
    container.closest(".wrapperTypeFilter") ||
    container.closest(".inputWrapper") ||
    container.parentElement;

  const icon = container.querySelector(".iconDesplegar");
  const hidden = container.querySelector("input[type='hidden']");
  const pseudo = container.querySelector(".pseudo-input-select-wrapper");
  const list = container.querySelector("ul.options, ul.list-select-custom, ul");

  if (!hidden || !pseudo || !list) return null;

  const isSearch = !!(wrapper && wrapper.classList.contains("select-search"));

  return { wrapper, container, icon, hidden, pseudo, list, isSearch };
}

function _placeholder(hidden) {
  return hidden?.getAttribute("placeholder") || "Seleccionar";
}

function _ensureNoResults(list, text) {
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
}

function _isOpen(list) {
  return list.classList.contains("open");
}

function _open(parts) {
  parts.list.classList.add("open");
  if (parts.icon) parts.icon.classList.add("open");
  if (typeof window.ordersZindexSelects === "function") {
    try {
      window.ordersZindexSelects();
    } catch {}
  }
}

function _close(parts) {
  parts.list.classList.remove("open");
  if (parts.icon) parts.icon.classList.remove("open");
  parts.list
    .querySelectorAll("li.active")
    .forEach((li) => li.classList.remove("active"));
}

function _toggle(parts) {
  if (_isOpen(parts.list)) _close(parts);
  else _open(parts);
}

function _visibleItems(list) {
  return Array.from(list.querySelectorAll("li")).filter(
    (li) =>
      !li.classList.contains("no-results-message") &&
      li.style.display !== "none"
  );
}

function _clearSelection(list) {
  list
    .querySelectorAll("li.selected")
    .forEach((li) => li.classList.remove("selected"));
}

// ================= API registry (opcional) =================
const __registry = new WeakMap();

// ================= core init =================
function initOne(container, preValues = {}) {
  const parts = _getPartsFromContainer(container);
  if (!parts) return null;

  // Evita doble init
  if (parts.container.dataset._inited === "1")
    return __registry.get(parts.hidden) || null;
  parts.container.dataset._inited = "1";

  const { wrapper, hidden, pseudo, list, isSearch } = parts;

  // -------- search input (si corresponde) --------
  let input = pseudo.querySelector("input.editable-product-input");
  let displayH3 = pseudo.querySelector("h3");

  if (isSearch) {
    // Reemplazamos el contenido del pseudo wrapper por un input
    if (!input) {
      pseudo.innerHTML = "";
      input = document.createElement("input");
      input.type = "text";
      input.className = "editable-product-input";
      input.autocomplete = "off";
      input.placeholder = _placeholder(hidden);
      input.setAttribute("aria-autocomplete", "list");
      pseudo.appendChild(input);
    } else {
      input.placeholder = _placeholder(hidden);
    }
  } else {
    // Select normal: asegurar H3
    if (!displayH3) {
      displayH3 = document.createElement("h3");
      pseudo.appendChild(displayH3);
    }
  }

  const noResults = _ensureNoResults(
    list,
    wrapper?.dataset?.noResults || "No se encontraron resultados"
  );

  // -------- set placeholder / preValues --------
  function setPlaceholder() {
    const ph = _placeholder(hidden);
    if (isSearch) {
      if (input) {
        if (!input.value) input.value = "";
        input.placeholder = ph;
      }
    } else {
      if (displayH3) {
        displayH3.textContent = ph;
        displayH3.classList.add("placeholder");
      }
    }
  }

  function setSelectedLabel(label) {
    if (isSearch) {
      if (input) input.value = label || "";
    } else {
      if (displayH3) {
        displayH3.textContent = label || "";
        displayH3.classList.remove("placeholder");
      }
    }
  }

  // PreValues por name (compat v2)
  if (preValues && hidden.name && preValues[hidden.name]) {
    const pv = preValues[hidden.name];
    hidden.value = pv.data || "";
    setSelectedLabel(pv.text || "");
  } else if (hidden.value && String(hidden.value).trim()) {
    // si ya viene value, intentar buscar su LI y setear label
    const v = String(hidden.value).trim();
    const li = list.querySelector(
      `li[data-value="${CSS?.escape ? CSS.escape(v) : v}"]`
    );
    if (li) {
      _clearSelection(list);
      li.classList.add("selected");
      setSelectedLabel(li.textContent.trim());
    } else {
      setPlaceholder();
    }
  } else {
    setPlaceholder();
  }

  // -------- filtros (solo search) --------
  function filter(val) {
    const q = _norm(val);
    let anyVisible = false;

    list.querySelectorAll("li").forEach((li) => {
      if (li.classList.contains("no-results-message")) return;
      const txt = _norm(li.textContent.trim());
      const show = q === "" || txt.includes(q);
      li.style.display = show ? "" : "none";
      if (show) anyVisible = true;
    });

    noResults.style.display = q !== "" && !anyVisible ? "block" : "none";
  }

  // -------- selección --------
  function selectLi(li) {
    if (!li || li.classList.contains("no-results-message")) return;
    if (li.style.display === "none") return;

    const value = li.getAttribute("data-value") || li.textContent.trim();
    const label = li.textContent.trim();

    hidden.value = value;
    _clearSelection(list);
    li.classList.add("selected");
    setSelectedLabel(label);

    hidden.dispatchEvent(new Event("input", { bubbles: true }));
    hidden.dispatchEvent(new Event("change", { bubbles: true }));

    // cerrar al seleccionar
    _close(parts);
  }

  // ================= eventos =================

  // 1) Click en icono: toggle open/close
  const onIconClick = (e) => {
    e.stopPropagation();
    _toggle(parts);
    if (isSearch && input && _isOpen(list)) input.focus();
  };
  if (parts.icon) parts.icon.addEventListener("click", onIconClick);

  // 2) Click en el campo (pseudo wrapper / container):
  // - si search y click fue en input => SOLO abrir (no cerrar por error)
  // - si no => toggle
  const onContainerClick = (e) => {
    // Si clickeo en un LI, no toca acá (lo maneja list click)
    const clickedLi = e.target.closest("li");
    if (clickedLi) return;

    if (isSearch && input && e.target === input) {
      if (!_isOpen(list)) _open(parts);
      return;
    }
    _toggle(parts);
    if (isSearch && input && _isOpen(list)) input.focus();
  };
  parts.container.addEventListener("click", onContainerClick);

  // 3) Click en lista: delegación (sirve si agregás <li> por JS)
  const onListClick = (e) => {
    const li = e.target.closest("li");
    if (!li) return;
    selectLi(li);
  };
  list.addEventListener("click", onListClick);

  // 4) Search input typing + focus
  const onInput = (e) => {
    // al tipear, limpiar hidden y selección
    if (hidden.value) hidden.value = "";
    _clearSelection(list);
    filter(e.target.value);
    if (!_isOpen(list)) _open(parts);
  };

  const onInputFocus = () => {
    _open(parts);
  };

  const onInputKeyDown = (e) => {
    const vis = _visibleItems(list);
    if (!vis.length) return;

    const idx = vis.findIndex((li) => li.classList.contains("active"));

    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (idx >= 0) vis[idx].classList.remove("active");
      const next = idx < vis.length - 1 ? idx + 1 : 0;
      vis[next].classList.add("active");
      vis[next].scrollIntoView({ block: "nearest" });
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (idx >= 0) vis[idx].classList.remove("active");
      const prev = idx > 0 ? idx - 1 : vis.length - 1;
      vis[prev].classList.add("active");
      vis[prev].scrollIntoView({ block: "nearest" });
    } else if (e.key === "Enter") {
      e.preventDefault();
      const pick = idx >= 0 ? vis[idx] : vis.length === 1 ? vis[0] : null;
      if (pick) selectLi(pick);
    } else if (e.key === "Escape") {
      _close(parts);
    }
  };

  if (isSearch && input) {
    input.addEventListener("input", onInput);
    input.addEventListener("focus", onInputFocus);
    input.addEventListener("keydown", onInputKeyDown);
  }

  // 5) Click fuera: cierra
  const onDocClick = (e) => {
    if (!parts.container.contains(e.target)) _close(parts);
  };
  document.addEventListener("click", onDocClick);

  // ================= API pública =================
  const api = {
    elements: { ...parts, input },
    open: () => _open(parts),
    close: () => _close(parts),
    toggle: () => _toggle(parts),
    clear: () => {
      hidden.value = "";
      _clearSelection(list);
      if (isSearch && input) {
        input.value = "";
        filter("");
      } else {
        setPlaceholder();
      }
      hidden.dispatchEvent(new Event("input", { bubbles: true }));
      hidden.dispatchEvent(new Event("change", { bubbles: true }));
    },
    setValue: (value) => {
      const v = String(value ?? "");
      const sel = `li[data-value="${CSS?.escape ? CSS.escape(v) : v}"]`;
      const li = list.querySelector(sel);
      if (li) selectLi(li);
    },
    setValueAndLabel: (
      value,
      label,
      { fire = true, markSelected = true } = {}
    ) => {
      hidden.value = value ?? "";
      setSelectedLabel(label ?? "");

      if (markSelected) {
        _clearSelection(list);
        const v = String(value ?? "");
        const li = list.querySelector(
          `li[data-value="${CSS?.escape ? CSS.escape(v) : v}"]`
        );
        if (li) li.classList.add("selected");
      }
      if (fire) {
        hidden.dispatchEvent(new Event("input", { bubbles: true }));
        hidden.dispatchEvent(new Event("change", { bubbles: true }));
      }
    },
    destroy: () => {
      if (parts.icon) parts.icon.removeEventListener("click", onIconClick);
      parts.container.removeEventListener("click", onContainerClick);
      list.removeEventListener("click", onListClick);
      document.removeEventListener("click", onDocClick);

      if (isSearch && input) {
        input.removeEventListener("input", onInput);
        input.removeEventListener("focus", onInputFocus);
        input.removeEventListener("keydown", onInputKeyDown);
      }

      parts.container.dataset._inited = "0";
      __registry.delete(hidden);
      if (hidden.__customSelectApi) delete hidden.__customSelectApi;
    },
  };

  __registry.set(hidden, api);
  hidden.__customSelectApi = api; // atajo

  return api;
}

// ================= init all =================
function initAll(preValues = {}, root = document) {
  const apis = [];
  root.querySelectorAll(".containerInputAndOptions").forEach((container) => {
    const parts = _getPartsFromContainer(container);
    if (!parts) return;
    // Solo los que tienen pseudo wrapper "onlySelect"
    if (!container.querySelector(".onlySelect.pseudo-input-select-wrapper"))
      return;
    const api = initOne(container, preValues);
    if (api) apis.push(api);
  });
  if (typeof window.ordersZindexSelects === "function") {
    try {
      window.ordersZindexSelects();
    } catch {}
  }
  return apis;
}

// ================= compat con tu v2 (globals) =================
function setPlaceholder(displayText, hiddenInput) {
  const ph = _placeholder(hiddenInput);
  if (!displayText || !hiddenInput) return;
  displayText.textContent = ph;
  displayText.classList.add("placeholder");
}

function clearInputs(inputs, scope = document) {
  // Limpia inputs específicos
  (inputs || []).forEach((i) => {
    try {
      i.value = "";
    } catch {}
  });

  // Limpia selects dentro del scope
  scope.querySelectorAll(".containerInputAndOptions").forEach((container) => {
    const parts = _getPartsFromContainer(container);
    if (!parts) return;

    // si está inicializado, usar su API
    const api = __registry.get(parts.hidden) || parts.hidden.__customSelectApi;
    if (api) {
      api.clear();
      return;
    }

    // fallback simple
    parts.hidden.value = "";
    _clearSelection(parts.list);
    const h3 = parts.pseudo.querySelector("h3");
    if (h3) setPlaceholder(h3, parts.hidden);
  });
}

// ================= public globals =================
window.initCustomSingleSelects = function (preValues = {}) {
  return initAll(preValues, document);
};

// Alias para tu caso "search"
window.initSelectSearchAll = function () {
  return initAll({}, document);
};

window.setSelectSearch = function (
  target,
  { value, label, fire = true, markSelected = true } = {}
) {
  const hidden =
    typeof target === "string" ? document.querySelector(target) : target;
  if (!hidden) return false;

  const api = __registry.get(hidden) || hidden.__customSelectApi;
  if (!api) {
    const container = _closestContainer(hidden);
    const newApi = initOne(container, {});
    if (!newApi) return false;
    if (label == null) newApi.setValue(value);
    else newApi.setValueAndLabel(value, label, { fire, markSelected });
    return true;
  }

  if (label == null) api.setValue(value);
  else api.setValueAndLabel(value, label, { fire, markSelected });
  return true;
};

window.clearInputs = clearInputs;
window.setPlaceholder = setPlaceholder;

// ================= auto-init =================
(function bootstrap() {
  const run = () => initAll({}, document);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();

// ================= init manual por JS =================

// initSingleSelect(selectWrapper, preValues)
// - selectWrapper: el .onlySelect.pseudo-input-select-wrapper (o un selector)
// - preValues: igual que antes (por hidden.name)
window.initSingleSelect = function (selectWrapper, preValues = {}) {
  const el =
    typeof selectWrapper === "string"
      ? document.querySelector(selectWrapper)
      : selectWrapper;

  if (!el) return null;

  // En tu HTML el selectWrapper vive dentro del containerInputAndOptions
  const container = el.classList?.contains("containerInputAndOptions")
    ? el
    : el.closest(".containerInputAndOptions");

  if (!container) return null;

  return initOne(container, preValues); // usa el core unificado (normal o search según .select-search)
};

// initCustomSingleSelects(preValues) ya existe, pero por compat lo dejamos explícito
window.initCustomSingleSelects = function (preValues = {}) {
  return initAll(preValues, document);
};

// ====== COMO INICIALIZAR MANUALMENTE LOS SELECTS CON JS ======
// 1) Insertás el bloque HTML al DOM (tu estructura igual)
// 2) Inicializás solo ese select:
// const selectWrapper = document.querySelector(
//   "#selectWrapperSelectCobrador .onlySelect.pseudo-input-select-wrapper"
// );
// initSingleSelect(selectWrapper);

// O si agregaste varios de golpe:
// initCustomSingleSelects(); // inicializa los nuevos (los ya inicializados no se tocan)
