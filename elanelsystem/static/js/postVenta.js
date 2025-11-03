/**
 * postVenta.js (ESM)
 * Cargalo así: <script type="module" src="{% static 'js/postVenta.js' %}"></script>
 * Usa helpers de /static/js/async_ui.js (loader + flujo async).
 */
import { createAsyncUI, openActionModal } from "/static/js/async_ui.js";

/* ========= Config ========= */
const API_LIST_URL  = "/ventas/auditorias/api/";
const API_AUD_URL   = "/ventas/auditorias/crear/";

/* ========= Utils ========= */
const $  = (sel, ctx=document) => ctx.querySelector(sel);
const $$ = (sel, ctx=document) => Array.from(ctx.querySelectorAll(sel));
const debounce = (fn, ms=300)=>{ let t; return (...a)=>{ clearTimeout(t); t=setTimeout(()=>fn(...a),ms);} };

/* ========= UI Elements ========= */
const $form      = $("#formFilterVentas") || $(".filters");
const $search    = $("#inputSearch");
const $sucursal  = $("#sucursalInput");   // hidden con ID numérico
const $estado    = $("#inputEstado");     // 'p','r','a','d' o texto equivalente
const $campania  = $("#campaniaInput");

const $list = $(".operationsList");
const $counts = {
  pendientes:   $("#pendientesResumen"),
  realizadas:   $("#realizadasResumen"),
  aprobadas:    $("#aprobadasResumen"),
  desaprobadas: $("#desaprobadasResumen"),
};

// ⬇️ Botón de informe + URL base (sin query)
const $makeInforme = $("#makeInforme");
const REPORT_URL = ($makeInforme?.getAttribute("href") || "/ventas/postventas/informe/").split("?")[0];

/* ========= Loader dentro del UL ========= */
const ui = createAsyncUI({
  mount: $list || document.body, // ⬅️ el loader vive dentro del UL
  texts: { working: "Cargando...", success: "Listo", error: "Error al cargar", canceled: "Cancelado" }
});

/* ========= Helpers de estado ========= */
function deriveStatusClean(auditorias) {
  if (!Array.isArray(auditorias) || auditorias.length === 0) return "pendiente";
  const last = auditorias[auditorias.length - 1];
  return last?.grade ? "aprobada" : "desaprobada";
}
function deriveStatusText(statusClean) {
  if (statusClean === "aprobada") return "Aprobada";
  if (statusClean === "desaprobada") return "Desaprobada";
  return "Pendiente";
}

/* ========= Expand / collapse detalle ========= */
function toggleWrapperDetail(button) {
  const wrapperDetailInfo = button.closest(".atributtes").querySelector(".wrapperDetailInfo");
  if (!wrapperDetailInfo) return;
  const heightDetail = wrapperDetailInfo.scrollHeight;

  const isOpen = wrapperDetailInfo.classList.contains("active");
  if (isOpen) {
    wrapperDetailInfo.style.maxHeight = "0px";
    wrapperDetailInfo.style.height = "0px";
    wrapperDetailInfo.classList.remove("active");
  } else {
    wrapperDetailInfo.style.maxHeight = heightDetail + "px";
    wrapperDetailInfo.style.height = heightDetail + "px";
    wrapperDetailInfo.classList.add("active");
  }

  if (button.firstElementChild) {
    button.firstElementChild.classList.toggle("active", !isOpen);
  }
}
function bindDetailsToggles() {
  $$(".displayDetailInfoButton", $list).forEach(btn => {
    btn.addEventListener("click", () => toggleWrapperDetail(btn));
  });
}

/* ========= Render ========= */
function renderItem(v) {
  const auditorias = Array.isArray(v.auditorias) ? v.auditorias : [];
  const hasAud = auditorias.length > 0;

  // statusClean + text con fallback si el backend no manda statusClean
  const statusClean = v.statusClean || deriveStatusClean(auditorias);
  const statusText  = v.statusText  || deriveStatusText(statusClean);

  // botón cambia según exista auditoría
  const btnLabel = hasAud ? "Editar" : "Auditar";
  const btnId    = hasAud ? "editarButton" : "auditarButton";

  const audHist = hasAud ? `
    <div class="containerHistorialAuditorias">
      ${auditorias.map((a, i, arr) => `
        <div class="infoCheckWrapper">
          <div class="wrapperComentarios"><p>${a.comentarios ?? "Vacio"}</p></div>
          <div class="wrapperFechaHora"><p>${a.fecha_hora ?? ""}</p></div>
          <div class="wrapperGrade"><p>${a.grade ? "Aprobada" : "Desaprobada"}</p></div>
          ${i === arr.length - 1 ? '<div class="wrapperUltimo"><p>Último</p></div>' : ""}
        </div>
      `).join("")}
    </div>
  ` : "";

  return `
    <li class="operationItem">
      <div class="ventaWrapper" id="v${v.id}">
        <div class="statusWrapperShortInfo ${statusClean}">
          <div class="iconStatus ${statusClean}"></div>
          <p>${statusText}</p>
        </div>

        <div class="atributtes">
          <button type="button" class="displayDetailInfoButton">
            <img src="${window.imgNext}" alt="" />
          </button>

          <div class="wrapperShortInfo">
            <div class="wrapperInfoAtributte"><h4>Cliente</h4><h1>${v.nombre ?? ""}</h1></div>
            <div class="wrapperInfoAtributte"><h4>DNI</h4><h1>${v.dni ?? ""}</h1></div>
            <div class="wrapperInfoAtributte"><h4>Nro Orden</h4><h1>${v.nro_operacion ?? ""}</h1></div>
            <div class="wrapperInfoAtributte"><h4>Fecha de inscripcion</h4><h1>${v.fecha ?? ""}</h1></div>
            <div class="wrapperInfoAtributte"><h4>Telefono</h4><h1>${v.tel ?? ""}</h1></div>
            <div class="wrapperInfoAtributte"><h4>CP</h4><h1>${v.cod_postal ?? ""}</h1></div>
          </div>

          <div class="wrapperDetailInfo">
            <div class="wrapperInfoAtributte"><h4>Localidad</h4><h1>${v.loc ?? ""}</h1></div>
            <div class="wrapperInfoAtributte"><h4>Provincia</h4><h1>${v.prov ?? ""}</h1></div>
            <div class="wrapperInfoAtributte"><h4>Direccion</h4><h1>${v.domic ?? ""}</h1></div>
            <div class="wrapperInfoAtributte"><h4>Vendedor</h4><h1>${v.vendedor ?? ""}</h1></div>
            <div class="wrapperInfoAtributte"><h4>Supervisor</h4><h1>${v.supervisor ?? ""}</h1></div>
            <div class="wrapperInfoAtributte"><h4>Campaña</h4><h1>${v.campania ?? ""}</h1></div>
            ${audHist}
          </div>

          <div class="statusWrapper">
            <div class="buttonsWrapper">
              <button id="${btnId}" class="add-button-default" onclick="modalForm('v${v.id}')">${btnLabel}</button>
            </div>
          </div>
        </div>
      </div>
    </li>
  `;
}

/* >>> Render de lista preservando el loader dentro del UL <<< */
function renderList(results = []) {
  if (!$list) return;

  // 1) Borrar SOLO <li>, dejando el loader u otros hijos
  $list.querySelectorAll(":scope > li").forEach(li => li.remove());

  // 2) Insertar items
  if (results.length) {
    const html = results.map(renderItem).join("");
    $list.insertAdjacentHTML("beforeend", html);
  } else {
    $list.insertAdjacentHTML("beforeend", `
      <li class="operationItem"><div class="ventaWrapper"><div class="vt-empty">Sin resultados</div></div></li>
    `);
  }

  // 3) Reenganchar toggles
  bindDetailsToggles();
}

function renderCounts(counts) {
  if (!counts) return;
  if ($counts.pendientes)   $counts.pendientes.textContent   = counts.pendientes ?? counts.cant_auditorias_pendientes ?? 0;
  if ($counts.realizadas)   $counts.realizadas.textContent   = counts.realizadas ?? counts.cant_auditorias_realizadas ?? 0;
  if ($counts.aprobadas)    $counts.aprobadas.textContent    = counts.aprobadas ?? counts.cant_auditorias_aprobadas ?? 0;
  if ($counts.desaprobadas) $counts.desaprobadas.textContent = counts.desaprobadas ?? counts.cant_auditorias_desaprobadas ?? 0;
}

/* ========= Parámetros actuales (reuso en fetch y en link de PDF) ========= */
let page = 1, page_size = 20;

function getCurrentParams() {
  return {
    page,
    page_size,
    search:     ($search?.value || "").trim(),
    campania:   ($campania?.value || "").trim(),
    estado:     ($estado?.value || "").trim(),
    sucursal_id:($sucursal?.value || "").trim(),
  };
}

function syncReportLink() {
  if (!$makeInforme) return;
  const p = getCurrentParams();
  const qs = new URLSearchParams();
  // Solo agregamos si hay valor
  if (p.search)      qs.set("search", p.search);
  if (p.campania)    qs.set("campania", p.campania);
  if (p.estado)      qs.set("estado", p.estado);
  if (p.sucursal_id) qs.set("sucursal_id", p.sucursal_id);

  const href = qs.toString() ? `${REPORT_URL}?${qs}` : REPORT_URL;
  $makeInforme.setAttribute("href", href);
}

/* ========= Fetch ========= */
async function fetchAuditorias() {
  const params = getCurrentParams();

  // Mantener el botón de informe sincronizado con lo que se ve
  syncReportLink();

  const { ok, result } = await ui.exec(async ({ signal }) => {
    const url = new URL(API_LIST_URL, window.location.origin);
    Object.entries(params).forEach(([k, v]) => {
      if (v !== "" && v !== null && v !== undefined) url.searchParams.set(k, v);
    });
    const res = await fetch(url.toString(), {
      method: "GET",
      credentials: "include",
      headers: { "Accept": "application/json" },
      signal
    });
    const payload = await res.json().catch(() => ({}));
    if (!res.ok) return { ok: false, message: (payload?.message || "Error al cargar") };
    return payload;
  }, { autoSuccessDelay: 200 });

  if (!ok) return;

  const results = result.results || result.ventas || [];
  const counts  = result.counts   || result.resumen || null;

  renderList(results);
  renderCounts(counts);
}

/* ========= Modal Auditoría ========= */
function renderFormAuditoria(venta_id, gname, uid, preset) {
  const approveId = `aprobarI-${uid}`;
  const denyId    = `desaprobarI-${uid}`;

  const checkedA = preset === true  ? 'checked' : '';
  const checkedD = preset === false ? 'checked' : '';

  return `
    <form method="POST" class="containerModularForm" id="containerModularForm">
      ${window.CSRF_TOKEN || ""}
      <input type="hidden" name="idVenta" id="idVenta" value="${venta_id}" readonly>
      <h2>Selecciona el estado de la auditoria</h2>

      <div class="wrapperButtonsGrade">
        <div class="buttonsWrapper">
          <input type="radio" class="aprobarI" name="${gname}" id="${approveId}" value="a" ${checkedA}>
          <label for="${approveId}" class="labelInputGrade aprobarLabel">Aprobar</label>

          <input type="radio" class="desaprobarI" name="${gname}" id="${denyId}" value="d" ${checkedD}>
          <label for="${denyId}" class="labelInputGrade desaprobarLabel">Desaprobar</label>
        </div>
      </div>

      <div class="wrapperFormComentario">
        <div class="wrapperInputComent">
          <label for="comentarioInput">Comentario</label>
          <textarea class="input-read-write-default" name="comentarioInput" id="comentarioInput" cols="30" rows="10"></textarea>
        </div>
      </div>

      <div data-status style="margin-top:.5rem;"></div>
    </form>`;
}

// 2) modalForm: generamos uid, mantenemos gname y preseleccionamos según estado actual
window.modalForm = function modalForm(ventaDomId) {
  const venta_id = String(ventaDomId).startsWith("v") ? String(ventaDomId).slice(1) : String(ventaDomId);

  // uid único por modal
  const uid   = `aud-${venta_id}-${Math.random().toString(36).slice(2,8)}`;
  const gname = `grade-${uid}`;

  // preselección (opcional): leemos el estado actual de la card
  const cls = document.getElementById("v"+venta_id)
              ?.querySelector(".statusWrapperShortInfo")?.className || "";
  const preset = cls.includes("aprobada") ? true : cls.includes("desaprobada") ? false : undefined;

  openActionModal({
    modalOpts: {
      cssClass: ['modalContainerAuditar'],
      closeMethods: ['button','overlay'],
    },

    buildContent: () => renderFormAuditoria(venta_id, gname, uid, preset),

    validate: (root) => {
      const ok = !!root.querySelector(`input[name="${gname}"]:checked`);
      const mount = root.querySelector('[data-status]');
      if (!ok && mount) mount.textContent = "Elegí aprobar o desaprobar para habilitar Guardar";
      if (ok && mount) mount.textContent = "";
      return ok;
    },

    run: async ({ signal, root }) => {
      const grade = root.querySelector(`input[name="${gname}"]:checked`)?.value;
      const comentarios = root.querySelector("#comentarioInput")?.value || "";

      const res = await fetch(API_AUD_URL || window.location.pathname, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json",
          "X-CSRFToken": getCookie('csrftoken') || ''
        },
        body: JSON.stringify({ venta_id, grade, comentarios }),
        signal
      });

      const payload = await res.json().catch(() => ({ status:false, message:"Error de red" }));
      if (!res.ok || payload.status === false) {
        return { ok:false, message: payload.message || "No se pudo registrar la auditoría" };
      }

      refreshVenta(payload);
      const ventaEl = document.getElementById("v"+venta_id);
      const btn = ventaEl?.querySelector('.displayDetailInfoButton');
      if (btn) toggleWrapperDetail(btn);

      return { ok:true, message: payload.message || "Guardado" };
    },

    buttons: { confirm:"Guardar", cancel:"Cancelar" },
    texts: { working:"Guardando...", success:"Listo", error:"Error", canceled:"Cancelado" },
    statusSelector: "[data-status]"
  }).then((out) => {
    if (out?.ok) {
      fetchAuditorias();
      // luego de refrescar, actualizamos también el link del PDF
      syncReportLink();
    }
  });
};

/* ========= Helpers ========= */
function getCookie(name) {
  const m = document.cookie.match(new RegExp('(?:^|; )' + name.replace(/([$?*|{}\]\\^])/g,'\\$1') + '=([^;]*)'));
  return m ? decodeURIComponent(m[1]) : null;
}

function refreshVenta(ventaUpdated) {
  const ventaElement = document.getElementById(`v${ventaUpdated["ventaUpdated_id"]}`);
  if (!ventaElement) return;

  const auditorias_updated = Array.isArray(ventaUpdated.auditorias) ? ventaUpdated.auditorias : [];
  const statusClean_updated = ventaUpdated.statusClean || deriveStatusClean(auditorias_updated);
  const statusText_updated  = ventaUpdated.statusText  || deriveStatusText(statusClean_updated);

  // auditorías
  let cont = ventaElement.querySelector(".containerHistorialAuditorias");
  if (!cont) {
    ventaElement.querySelector(".wrapperDetailInfo")
      ?.insertAdjacentHTML("beforeend", `<div class="containerHistorialAuditorias"></div>`);
    cont = ventaElement.querySelector(".containerHistorialAuditorias");
  }
  cont.innerHTML = auditorias_updated.map((e, i, arr) => `
    <div class="infoCheckWrapper">
      <div class="wrapperComentarios"><p>${e.comentarios ?? "Vacio"}</p></div>
      <div class="wrapperFechaHora"><p>${e.fecha_hora ?? ""}</p></div>
      <div class="wrapperGrade">${e["grade"] ? '<p>Aprobada</p>' : '<p>Desaprobada</p>'}</div>
      ${i === arr.length - 1 ? '<div class="wrapperUltimo"><p>Último</p></div>' : ""}
    </div>
  `).join("");

  // status (actualiza clase + texto)
  const shortInfo = ventaElement.querySelector(".statusWrapperShortInfo");
  if (shortInfo) {
    shortInfo.className = `statusWrapperShortInfo ${statusClean_updated}`;
    const icon = shortInfo.querySelector(".iconStatus");
    if (icon) icon.className = `iconStatus ${statusClean_updated}`;
    const p = shortInfo.querySelector("p");
    if (p) p.textContent = statusText_updated;
    else shortInfo.insertAdjacentHTML("beforeend", `<p>${statusText_updated}</p>`);
  }

  // botón -> Editar
  const btns = ventaElement.querySelector(".buttonsWrapper");
  if (btns) btns.innerHTML = `<button class="editarButton" onclick="modalForm('v${ventaUpdated["ventaUpdated_id"]}')">Editar</button>`;
}

/* ========= Bind filtros ========= */
function bindFilters() {
  // prevenir submit real
  if ($form) $form.addEventListener("submit", (e)=>{ e.preventDefault(); page=1; fetchAuditorias(); });

  if ($search)  $search.addEventListener("input", debounce(()=>{
    page = 1; fetchAuditorias(); syncReportLink();
  }, 300));

  [$sucursal, $estado, $campania].forEach(el=>{
    if (!el) return;
    el.addEventListener("input",  ()=>{ page = 1; fetchAuditorias(); syncReportLink(); });
    el.addEventListener("change", ()=>{ page = 1; fetchAuditorias(); syncReportLink(); });
  });
}

/* ========= Init ========= */
function init() {
  bindFilters();
  // primer render + primer sync del link de informe
  fetchAuditorias();
  syncReportLink();
}
document.addEventListener("DOMContentLoaded", init);
