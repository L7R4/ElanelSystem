// input_search_operation.js
// Filtrado en vivo (300ms) por nro_operacion o producto.
// Usa loader de async_ui.js montado en .operations (centrado).

(async function () {
  /* ====== util ====== */
  const $ = (s, c = document) => c.querySelector(s);
  const debounce = (fn, ms = 300) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };

  // Cargamos el módulo del loader de forma dinámica (sin cambiar <script type>)
  const { createAsyncUI } = await import("/static/js/async_ui.js");

  /* ====== refs ====== */
  const $opInput   = $("#operation");
  const $prodInput = $("#productoInput");     // readonly (custom select)
  const $prodList  = $("#contenedorProducto"); // <ul> de opciones (custom select)
  const $opsWrap   = $(".operations");
  const $list      = $(".operationsList");
  const $btnSearch = $("#submitSearchVenta"); // lo ocultamos

  if ($btnSearch) $btnSearch.style.display = "none";

  // Montamos loader en el contenedor de operaciones (queda centrado allí)
  const ui = createAsyncUI({
    mount: $opsWrap || document.body,
    texts: { working: "Filtrando...", success: "Listo", error: "Error", canceled: "Cancelado" }
  });

  /* ====== helpers ====== */
  function getCookie(name) {
    const m = document.cookie.match(new RegExp('(?:^|; )' + name.replace(/([$?*|{}\\^])/, '\\$1') + '=([^;]*)'));
    return m ? decodeURIComponent(m[1]) : null;
  }

  function estadoToClass(estado = "") {
    const s = String(estado).toLowerCase();
    if (s.includes("activo")) return "activo";
    if (s.includes("baja")) return "baja";
    if (s.includes("adjudicada")) return "adjudicada";
    if (s.includes("suspendida")) return "suspendida";
    return "";
  }

  function htmlVenta(venta) {
    const ordenesHtml = (venta.nro_ordenes || []).map(n => `<h3>${n}</h3>`).join("");
    const cls = estadoToClass(venta.estado);

    return `
      <li class="operationItem">
        <div class="nameStatus">
          <img class="iconProducto" src="/static/images/icons/moto_icon.svg" alt="">
          <h1>${venta.producto ?? ""}</h1>
          <div class="iconStatus ${cls}"></div>
          <h3>${venta.estado ?? ""}</h3>
        </div>

        <div class="attributes">
          <div class="information">
            <h2>Importe</h2><h3>$${venta.importe ?? 0}</h3>
          </div>
          <div class="information">
            <h2>Fecha Inscripcion</h2><h3>${(venta.fecha_inscripcion || "").slice(0,10)}</h3>
          </div>
          <div class="information">
            <h2>N° Operacion</h2><h3>${venta.nro_operacion ?? ""}</h3>
          </div>
          <div class="information">
            <h2>Cuotas pagadas</h2><h3>${venta.cuotas_pagadas ?? 0}</h3>
          </div>
          <div class="information">
            <h2>N° Orden/es</h2>
            <div class="ordenesWrapper">${ordenesHtml}</div>
          </div>
        </div>

        <div class="iconsAttributes">
          <!-- No tenemos el id de la venta en la respuesta; si lo agregás, podés armar el href real -->
          <a href="#" class="buttonMore" aria-disabled="true">
            <div><h3>Ver mas</h3><img src="/static/images/icons/nextSinBackground.png" alt=""></div>
          </a>
        </div>
      </li>`;
  }

  function renderVentas(ventas = []) {
    if (!$list) return;
    if (!ventas.length) {
      $list.innerHTML = `<li class="operationItem"><div class="vt-empty">Sin resultados</div></li>`;
      return;
    }
    $list.innerHTML = ventas.map(htmlVenta).join("");
  }

  function ensureResetLink() {
    if ($("#resetFiltros")) return;
    const a = document.createElement("a");
    a.id = "resetFiltros";
    a.textContent = "Limpiar filtros";
    a.href = window.location.pathname;
    a.addEventListener("click", (ev) => {
      ev.preventDefault();
      // restauro inputs y recargo para volver al listado inicial renderizado por el server
      if ($opInput)   $opInput.value = "";
      if ($prodInput) $prodInput.value = "";
      window.location.reload();
    });

    // lo insertamos al lado del form; si no está, al final de .filters
    const $form = $("#formFilterVentas") || $(".filters") || document.body;
    $form.insertAdjacentElement("beforeend", a);
  }

  /* ====== core: filtrar ====== */
  async function doFilter() {
    const nro_operacion = ($opInput?.value || "").trim();
    const producto      = ($prodInput?.value || "").trim();

    // Si no hay filtros, no hago request (mantengo pantalla actual)
    if (!nro_operacion && !producto) return;

    const { ok, result } = await ui.exec(async ({ signal }) => {
      const res = await fetch(window.location.pathname, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json",
          "X-CSRFToken": getCookie("csrftoken") || ""
        },
        body: JSON.stringify({
          // mando solo lo que hay; tu view ignora claves ausentes
          ...(nro_operacion ? { nro_operacion } : {}),
          ...(producto      ? { producto }      : {}),
        }),
        signal
      });

      const payload = await res.json().catch(() => ({ status: false, message: "Error de red" }));
      if (!res.ok || payload.status === false) {
        return { ok: false, message: payload.message || "No se pudo filtrar" };
      }
      return payload; // {status:true, ventas:[...] }
    }, { autoSuccessDelay: 150 });

    if (!ok) return;

    renderVentas(result.ventas || []);
    ensureResetLink();
  }

  const triggerFilter = debounce(doFilter, 300);

  /* ====== eventos ====== */
  // N° operación: filtra luego de 300ms sin teclear
  $opInput && $opInput.addEventListener("input", triggerFilter);

  // Producto (select custom): cuando cambia/selecciona, filtramos
  // 1) si tu script inputsSelectsOnly dispara "input" o "change" sobre el input readonly:
  $prodInput && $prodInput.addEventListener("input", triggerFilter);
  $prodInput && $prodInput.addEventListener("change", triggerFilter);

  // 2) respaldo: si el select custom solo marca el <li>, lo capturamos y actualizamos el input
  $prodList && $prodList.addEventListener("click", (e) => {
    const li = e.target.closest("li[data-value]");
    if (!li) return;
    if ($prodInput) $prodInput.value = li.getAttribute("data-value") || "";
    // algunos select custom cierran con un pequeño delay; esperamos 0ms para asegurar valor
    setTimeout(triggerFilter, 0);
  });
})();
