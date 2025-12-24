// operation.js
// Filtrado en vivo con overlay (blur) sobre el WRAPPER de la lista.
// Reutiliza createAsyncUI. Sin “Listo” en éxito; mensajes solo en loading/error/sin resultados.
// N° operación filtra por “contiene” (cliente con caché). Si inputs vacíos, pide todo al back.

(async function () {
  /* ====== utils ====== */
  const $ = (s, c = document) => c.querySelector(s);
  const debounce = (fn, ms = 300) => {
    let t;
    return (...a) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...a), ms);
    };
  };

  const iconSaleMap = {
    living: "/static/images/icons/icon_combo_living.svg",
    dormitorio: "/static/images/icons/icon_combo_dormitorio.svg",
    hogar: "/static/images/icons/icon_combo_home.svg",
    cocina: "/static/images/icons/icon_combo_cocina.svg",
    tecnologia: "/static/images/icons/icon_combo_tech.svg",
    solucion: "/static/images/icons/icon_solucion_dineraria.svg",
  };
  const DEFAULT_ICON = "/static/images/icons/icon_moto.svg";

  // normaliza: minúsculas, sin acentos/diacríticos, colapsa espacios
  function normalizeKey(s = "") {
    return String(s)
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "") // quita tildes
      .replace(/\s+/g, " ") // colapsa
      .trim();
  }

  function getIconForProduct(rawName = "") {
    const name = normalizeKey(rawName);
    // probamos todas las claves; si alguna aparece en el nombre, devolvemos su icono
    for (const key of Object.keys(iconSaleMap)) {
      if (name.includes(key)) return iconSaleMap[key];
    }
    return DEFAULT_ICON;
  }

  const { createAsyncUI } = await import(
    "/static/js/vanilla_components/async_ui.js"
  );

  /* ====== refs ====== */
  const $list = $(".operationsList"); // <ul>
  const $wrap =
    document.querySelector(".operationsWrapper") || $list?.parentElement; // wrapper del UL
  const $opInput = $("#operation"); // N° operación
  const $prodInput = $("#productoInput"); // valor select custom
  const $prodList = $("#contenedorProducto"); // lista visual select custom
  const $btnSearch = $("#submitSearchVenta"); // ocultar si existe
  if ($btnSearch) $btnSearch.style.display = "none";

  // Overlay se posiciona sobre WRAPPER
  if ($wrap && getComputedStyle($wrap).position === "static") {
    $wrap.style.position = "relative";
  }

  /* ====== overlay (en WRAPPER) ====== */
  const overlay = document.createElement("div");
  overlay.className = "async-overlay hidden";
  overlay.innerHTML = `
    <div class="async-panel">
      <div class="async-ui-slot"></div>
      <div class="msg"></div>
    </div>
  `;
  const $msg = overlay.querySelector(".msg");
  const $uiSlot = overlay.querySelector(".async-ui-slot");
  $wrap?.appendChild(overlay);

  function showOverlay(text = "Cargando…") {
    $msg.textContent = text || "";
    overlay.classList.remove("hidden");
  }
  function hideOverlay() {
    overlay.classList.add("hidden");
  }
  function flashOverlay(text = "No existen resultados", ms = 1300) {
    showOverlay(text);
    setTimeout(hideOverlay, ms);
  }

  // Spinner de async_ui en el slot. Sin textos para no duplicar “Cargando…”.
  const ui = createAsyncUI({
    mount: $uiSlot,
    texts: { working: "", success: "", error: "", canceled: "" },
  });

  /* ====== helpers ====== */
  function getCookie(name) {
    const m = document.cookie.match(
      new RegExp(
        "(?:^|; )" + name.replace(/([$?*|{}\\^])/, "\\$1") + "=([^;]*)"
      )
    );
    return m ? decodeURIComponent(m[1]) : null;
  }
  const getIn = (obj, path, def = undefined) => {
    try {
      return (
        path
          .split(".")
          .reduce((a, k) => (a && a[k] != null ? a[k] : undefined), obj) ?? def
      );
    } catch {
      return def;
    }
  };

  /* ====== normalización + plantilla ====== */
  function normalizeVenta(v) {
    return {
      ...v,
      _productoNombre: getIn(v, "producto.nombre", v.producto ?? ""),
      _nroOpStr: String(v.nro_operacion ?? ""),
    };
  }

  function htmlVenta(venta) {
    const productoNombre = venta._productoNombre;
    const adjudicado = getIn(venta, "adjudicado", null);
    const deBaja = getIn(venta, "deBaja", null);
    const suspendida = !!venta.suspendida;

    const detailHref = venta.detail_url || "#";
    const disabled = !venta.detail_url;

    let statusBlock = "";
    if (adjudicado?.status) {
      statusBlock = `
        <div class="iconStatus adjudicada"></div>
        <h3>Adjudicado por ${adjudicado.tipo ?? ""}</h3>
      `;
    } else if (deBaja?.status) {
      statusBlock = `
        <div class="badgeStatus baja">
          <div class="iconStatus baja"></div>
          <h3>De baja por ${deBaja.motivo ?? ""}</h3>
        </div>
        ${
          deBaja.motivo === "cliente" && deBaja.pdf_url
            ? `<a href="${deBaja.pdf_url}" target="_blank" id="downloadPDF">Descargar PDF</a>`
            : ""
        }
        ${
          deBaja.motivo === "plan recupero" &&
          (deBaja.nuevo_plan_url || deBaja.nuevaVentaPK)
            ? `<a href="${
                deBaja.nuevo_plan_url || `/sales/${deBaja.nuevaVentaPK}/`
              }" target="_blank" id="downloadPDF">Ver nuevo plan</a>`
            : ""
        }
      `;
    } else if (suspendida) {
      statusBlock = `
        <div class="badgeStatus suspendida">
          <div class="iconStatus suspendida"></div>
          <h3>Suspendido</h3>
        </div>
      `;
    } else {
      statusBlock = `
        <div class="badgeStatus activo">
          <div class="iconStatus activo"></div>
          <h3>Activo</h3>
        </div>
      `;
    }

    let ordenesHtml = "";
    const contratos = Array.isArray(venta.cantidadContratos)
      ? venta.cantidadContratos
      : null;
    if (contratos?.length) {
      ordenesHtml = contratos
        .map((c) => {
          const esAdj = !!(
            adjudicado?.status &&
            String(c.nro_contrato) === String(adjudicado.contratoAdjudicado)
          );
          return `<h3${esAdj ? ' class="adjudicadoTag"' : ""}>${
            c.nro_orden
          }</h3>`;
        })
        .join("");
    } else {
      const nums = Array.isArray(venta.nro_ordenes) ? venta.nro_ordenes : [];
      ordenesHtml = nums.map((n) => `<h3>${n}</h3>`).join("");
    }

    const importe = Math.round(Number(venta.importe) || 0).toLocaleString(
      "es-AR"
    );
    const fecha = (venta.fecha_inscripcion || venta.fecha || "").slice(0, 10);
    const nroOp = venta.nro_operacion ?? "";
    const iconSrc = getIconForProduct(
      productoNombre || venta.tipo_producto || ""
    );
    return `
      <li class="operationItem">
        <div class="nameStatus">
          <img class="iconProducto" src="${iconSrc}" alt="">
          <h1>${productoNombre}</h1>
          ${statusBlock}
        </div>

        <div class="attributes">
          <div class="information"><h2>Importe</h2><h3>$${importe}</h3></div>
          <div class="information"><h2>Fecha Inscripcion</h2><h3>${fecha}</h3></div>
          <div class="information"><h2>N° Operacion</h2><h3>${nroOp}</h3></div>
          <div class="information"><h2>Cuotas pagadas</h2><h3>${
            venta.cuotas_pagadas ?? 0
          }</h3></div>
          <div class="information">
            <h2>N° Orden/es</h2>
            <div class="ordenesWrapper">${ordenesHtml}</div>
          </div>
        </div>

        <div class="iconsAttributes">
          <a
            href="${detailHref}"
            class="buttonMore${disabled ? " is-disabled" : ""}"
            ${disabled ? 'aria-disabled="true"' : 'aria-disabled="false"'}
            ${disabled ? "" : 'rel="noopener noreferrer"'}
          >
            <div><h3>Ver mas</h3><img src="/static/images/icons/nextSinBackground.png" alt=""></div>
          </a>
        </div>
      </li>
    `;
  }

  function renderEmptyLI(message) {
    $list.innerHTML = `
      <li class="operationItem">
        <div class="vt-empty" style="width:100%;text-align:center;padding:2rem 1rem;">
          <h3>${message}</h3>
        </div>
      </li>`;
  }

  function renderVentas(ventas = []) {
    if (!$list) return;
    if (!ventas.length) {
      $list.innerHTML = "";
      return;
    }
    $list.innerHTML = ventas.map(htmlVenta).join("");
  }

  /* ====== API (no-store) ====== */
  async function fetchVentas(filters) {
    const res = await fetch(window.location.pathname, {
      method: "POST",
      credentials: "include",
      cache: "no-store", // evita caches del fetch
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        "X-CSRFToken": getCookie("csrftoken") || "",
        "Cache-Control": "no-store, no-cache, must-revalidate",
        Pragma: "no-cache",
      },
      body: JSON.stringify(filters),
    });
    let payload;
    try {
      payload = await res.json();
    } catch (e) {
      console.error("Error parseando JSON de ventas:", e);
      payload = { status: false, message: "Error de red / JSON inválido" };
    }

    if (!res.ok || payload.status === false) {
      console.error("fetchVentas falló:", {
        status: res.status,
        url: res.url,
        payload,
      });
    }

    return { ok: res.ok && payload.status !== false, payload };
  }

  /* ====== caché y filtrado cliente ====== */
  let allVentasCache = null; // array de ventas normalizadas

  function applyClientFilter(base, { nro_operacion, producto }) {
    let out = base;
    if (nro_operacion) {
      const q = String(nro_operacion).trim();
      out = out.filter((v) => v._nroOpStr.includes(q));
    }
    if (producto) {
      const qp = String(producto).trim().toLowerCase();
      out = out.filter(
        (v) =>
          v._productoNombre.toLowerCase() === qp ||
          v._productoNombre.toLowerCase().includes(qp)
      );
    }
    return out;
  }

  function emptyMessage({ nro_operacion, producto }) {
    if (nro_operacion && !producto)
      return `No se encontró ninguna venta con N° Operación "${nro_operacion}"`;
    if (!nro_operacion && producto)
      return `No se encontró ninguna venta para el producto "${producto}"`;
    if (nro_operacion && producto)
      return `No se encontró ninguna venta con N° "${nro_operacion}" para "${producto}"`;
    return "No existen resultados";
  }

  /* ====== core ====== */
  async function runFilter() {
    const nro_operacion = ($opInput?.value || "").trim();
    const producto = ($prodInput?.value || "").trim();

    // Búsqueda parcial por nro_operacion en cliente (con caché)
    if (nro_operacion) {
      if (!allVentasCache) {
        showOverlay("Cargando…");
        const { ok, payload } = await fetchVentas({});
        if (!ok) {
          renderVentas([]);
          showOverlay("Filtro fallido");
          return;
        }
        allVentasCache = (payload.ventas || []).map(normalizeVenta);
        hideOverlay();
      }
      const filtered = applyClientFilter(allVentasCache, {
        nro_operacion,
        producto,
      });
      if (filtered.length === 0) {
        renderVentas([]);
        renderEmptyLI(emptyMessage({ nro_operacion, producto }));
        return;
      }
      renderVentas(filtered);
      return;
    }

    // Si no hay nro_operacion (solo producto o vacío), vamos al back
    showOverlay("Cargando…");
    const { ok, result } = await ui.exec(
      async () => {
        const { ok, payload } = await fetchVentas({
          ...(producto ? { producto } : {}),
        });
        if (!ok)
          return { ok: false, message: payload.message || "Filtro fallido" };
        return payload;
      },
      { autoSuccessDelay: 0 }
    );

    if (!ok) {
      renderVentas([]);
      showOverlay("Filtro fallido");
      return;
    }

    const ventas = (result.ventas || []).map(normalizeVenta);

    // Respuesta completa → refresco cache
    if (!producto) {
      allVentasCache = [...ventas];
    }
    if (producto && !allVentasCache) {
      allVentasCache = [...ventas];
    }

    renderVentas(ventas);
    if (ventas.length === 0) {
      renderEmptyLI(emptyMessage({ nro_operacion, producto }));
      flashOverlay("No existen resultados");
    } else {
      hideOverlay();
    }
  }

  const triggerFilter = debounce(runFilter, 300);

  /* ====== reset/refresh para bfcache y eventos del navegador ====== */
  function resetState() {
    allVentasCache = null;
    if ($list) $list.innerHTML = "";
  }
  const hardRefresh = debounce(async () => {
    resetState();
    showOverlay("Cargando…");
    await runFilter();
  }, 0);

  // Al volver con la flechita (bfcache)
  window.addEventListener("pageshow", (e) => {
    if (e.persisted) hardRefresh();
  });

  // Al recuperar visibilidad (Safari/iOS/otros)
  let _didVisibilityRefresh = false;
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible" && !_didVisibilityRefresh) {
      _didVisibilityRefresh = true;
      hardRefresh();
      setTimeout(() => (_didVisibilityRefresh = false), 1500);
    }
  });

  // Historial
  window.addEventListener("popstate", () => {
    hardRefresh();
  });

  // Al volver el foco a la pestaña
  // window.addEventListener("focus", () => {
  //   hardRefresh();
  // });

  /* ====== eventos UI ====== */
  if ($opInput) $opInput.addEventListener("input", triggerFilter);
  if ($prodInput) $prodInput.addEventListener("input", triggerFilter);
  if ($prodInput) $prodInput.addEventListener("change", triggerFilter);

  // Respaldo para select custom basado en <li data-value>
  if ($prodList) {
    $prodList.addEventListener("click", (e) => {
      const li = e.target.closest("li[data-value]");
      if (!li) return;
      if ($prodInput) $prodInput.value = li.getAttribute("data-value") || "";
      setTimeout(triggerFilter, 0);
    });
  }
  async function initVentas() {
    try {
      await runFilter();

      // Por si querés asegurar caché llena cuando el filtro está vacío
      if (!allVentasCache) {
        const { ok, payload } = await fetchVentas({});
        if (ok) {
          allVentasCache = (payload.ventas || []).map(normalizeVenta);
        }
      }
    } catch (err) {
      console.error("Error inicial cargando ventas:", err);
      renderEmptyLI("No se pudieron cargar las ventas. Recargá la página.");
    }
  }

  // Si el DOM todavía se está cargando, nos enganchamos al DOMContentLoaded en document.
  // Si ya está listo (script al final del body, bfcache, etc.), ejecutamos directamente.
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initVentas);
  } else {
    initVentas();
  }
})();
