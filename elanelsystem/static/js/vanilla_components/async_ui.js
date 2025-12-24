/* ========= loader mínimo reutilizable ========= */
export function makeInlineLoader(target, { text = "Procesando..." } = {}) {
  if (!target) throw new Error("makeInlineLoader: target requerido");
  const wrap = document.createElement("div");
  wrap.className = "inline-loader inline-loader--hidden";
  wrap.innerHTML = `
    <div class="inline-loader__spinner" aria-hidden="true"></div>
    <span class="inline-loader__text"></span>
  `;
  const txt = wrap.querySelector(".inline-loader__text");
  target.appendChild(wrap);

  return {
    el: wrap,
    show(msg = text) {
      wrap.classList.remove("inline-loader--hidden","inline-loader--success","inline-loader--error");
      wrap.querySelector(".inline-loader__spinner").style.display = "";
      txt.textContent = msg;
    },
    success(msg = "¡Listo!") {
      wrap.classList.remove("inline-loader--hidden","inline-loader--error");
      wrap.classList.add("inline-loader--success");
      wrap.querySelector(".inline-loader__spinner").style.display = "none";
      txt.textContent = msg;
    },
    error(msg = "Ocurrió un error") {
      wrap.classList.remove("inline-loader--hidden","inline-loader--success");
      wrap.classList.add("inline-loader--error");
      wrap.querySelector(".inline-loader__spinner").style.display = "none";
      txt.textContent = msg;
    },
    reset() {
      wrap.classList.add("inline-loader--hidden");
      wrap.classList.remove("inline-loader--success","inline-loader--error");
      wrap.querySelector(".inline-loader__spinner").style.display = "";
      txt.textContent = text;
    },
    destroy() { wrap.remove(); }
  };
}

/* ========= utils ========= */
function getCookie(name) {
  const m = document.cookie.match(new RegExp('(?:^|; )' + name.replace(/([$?*|{}\]\\^])/g,'\\$1') + '=([^;]*)'));
  return m ? decodeURIComponent(m[1]) : null;
}
function buildUrlWithParams(url, params) {
  if (!params) return url;
  const usp = params instanceof URLSearchParams ? params : new URLSearchParams(params);
  const sep = url.includes('?') ? '&' : '?';
  return usp.toString() ? url + sep + usp.toString() : url;
}

/* ========= fetch genérico con abort, CSRF y autodetección ========= */
export async function apiFetch(url, {
  method = 'GET',
  data,             // objeto, FormData, URLSearchParams, string, Blob...
  params,           // objeto o URLSearchParams para querystring
  headers = {},
  signal,
  csrf = true,      // agrega X-CSRFToken en métodos no-GET (Django)
  credentials = 'same-origin', // envía cookies same-origin
} = {}) {
  const m = method.toUpperCase();
  const isGetLike = (m === 'GET' || m === 'HEAD');
  const finalUrl = buildUrlWithParams(url, params);

  const init = {
    method: m,
    credentials,
    headers: { 'X-Requested-With': 'XMLHttpRequest', ...headers },
    signal
  };

  // Cuerpo
  if (!isGetLike && data !== undefined && data !== null) {
    const isFormKind = (data instanceof FormData) || (data instanceof URLSearchParams) || (data instanceof Blob);
    if (isFormKind) {
      init.body = data; // no seteamos Content-Type, el navegador lo hace
    } else if (typeof data === 'object') {
      init.headers['Content-Type'] = init.headers['Content-Type'] || 'application/json';
      init.body = init.headers['Content-Type'].includes('application/json') ? JSON.stringify(data) : data;
    } else {
      // string u otros
      init.body = data;
    }
  }

  // CSRF para Django: métodos que modifican
  if (csrf && !isGetLike) {
    const token = getCookie('csrftoken') || getCookie('csrfmiddlewaretoken');
    if (token && !init.headers['X-CSRFToken']) {
      init.headers['X-CSRFToken'] = token;
    }
  }

  const res = await fetch(finalUrl, init);
  const ct = res.headers.get('content-type') || '';

  let payload;
  if (ct.includes('application/json')) {
    payload = await res.json().catch(() => null);
  } else if (ct.startsWith('text/')) {
    payload = await res.text();
  } else {
    payload = await res.blob();
  }

  if (!res.ok) {
    const err = new Error(`HTTP ${res.status} ${res.statusText}`);
    err.status = res.status;
    err.statusText = res.statusText;
    err.url = finalUrl;
    err.payload = payload;
    throw err;
  }

  return payload;
}

/* ========= núcleo UI async reutilizable (loader + abort) ========= */
export function createAsyncUI({
  mount,
  texts = { working: "Procesando...", success: "Listo", error: "Ocurrió un error", canceled: "Operación cancelada" }
} = {}) {
  if (!mount) throw new Error("createAsyncUI: mount requerido");
  const loader = makeInlineLoader(mount, { text: texts.working });

  let controller = null;
  let inFlight = false;

  function setButtons(buttons, disabled) {
    if (!buttons) return;
    const { confirmBtn, closeBtn } = buttons;
    if (confirmBtn) confirmBtn.disabled = !!disabled;
    if (closeBtn)   closeBtn.disabled   = !!disabled;
  }

  async function exec(runFn, {
    buttons,
    autoSuccessDelay = 400,
    closeOnSuccess = false,
    onSuccessClose
  } = {}) {
    if (inFlight) return { skipped: true };
    inFlight = true;
    setButtons(buttons, true);
    loader.reset(); loader.show(texts.working);

    controller = new AbortController();

    const setStatus = {
      working: (msg) => loader.show(msg || texts.working),
      success: (msg) => loader.success(msg || texts.success),
      error:   (msg) => loader.error(msg || texts.error),
      canceled:(msg) => loader.error(msg || texts.canceled),
    };

    try {
      const result = await runFn({ signal: controller.signal, setStatus });

      if (result && result.ok === false) {
        setStatus.error(result.message);
        inFlight = false; setButtons(buttons, false);
        return { ok:false, result };
      }

      setStatus.success(result?.message);
      inFlight = false;

      if (closeOnSuccess && typeof onSuccessClose === "function") {
        setTimeout(onSuccessClose, autoSuccessDelay);
      } else {
        setButtons(buttons, false);
      }
      return { ok:true, result };

    } catch (err) {
      if (err?.name === 'AbortError') {
        setStatus.canceled();
        inFlight = false;
        return { canceled:true };
      }
      setStatus.error();
      inFlight = false; setButtons(buttons, false);
      return { ok:false, error: err };
    }
  }

  function abort() {
    if (inFlight && controller && !controller.signal.aborted) controller.abort();
  }
  function isRunning() { return inFlight; }

  return { exec, abort, isRunning, loader };
}

/* ========= wrapper opcional: Tingle + createAsyncUI ========= */
export function openActionModal({
  modalOpts = {},
  buildContent,
  validate,
  run,
  ctx = {},
  texts = { working:"Procesando...", success:"Listo", error:"Ocurrió un error", canceled:"Operación cancelada" },
  buttons = { confirm:"Confirmar", cancel:"Cerrar" },
  statusSelector
} = {}) {
  return new Promise((resolve) => {
    let willDestroy = false;
    let ui;

    const modal = new tingle.modal({
      footer: true,
      closeMethods: ['button','overlay'],
      cssClass: [],
      ...modalOpts,
      onClose: () => {
        if (ui && ui.isRunning()) ui.abort();
        willDestroy = true;
        if (!ui || !ui.isRunning()) resolve({ canceled:true });
        if (typeof modalOpts.onClose === 'function') { try { modalOpts.onClose(); } catch {} }
      }
    });

    modal.setContent(buildContent(ctx));

    const btnConfirm = modal.addFooterBtn(buttons.confirm || "Confirmar",
      "tingle-btn tingle-btn--primary add-button-default", onConfirm);
    const btnClose   = modal.addFooterBtn(buttons.cancel  || "Cerrar",
      "tingle-btn tingle-btn--default button-default-style", onClose);

    modal.modal.addEventListener('transitionend', () => {
      const isClosed = !modal.modal.classList.contains('tingle-modal--visible');
      if (willDestroy && isClosed) modal.destroy();
    });

    const root = modal.modalBoxContent || modal.modal;

    let mount = statusSelector ? root.querySelector(statusSelector) : root.querySelector('[data-status]');
    if (!mount) {
      mount = document.createElement('div');
      mount.setAttribute('data-status',''); mount.style.marginTop = '.75rem';
      const form = root.querySelector('form'); (form || root).appendChild(mount);
    }

    ui = createAsyncUI({ mount, texts });

    function updateConfirm() {
      const valid = typeof validate === 'function' ? !!validate(root, ctx) : true;
      btnConfirm.disabled = ui.isRunning() || !valid;
    }
    btnConfirm.disabled = true;
    root.addEventListener('input', updateConfirm);
    root.addEventListener('change', updateConfirm);

    modal.open();
    setTimeout(updateConfirm, 0);

    async function onConfirm() {
      const res = await ui.exec(
        ({ signal, setStatus }) => run({ root, signal, setStatus, ctx }),
        { buttons: { confirmBtn: btnConfirm, closeBtn: btnClose },
          closeOnSuccess: true, onSuccessClose: () => modal.close() }
      );
      if (res?.ok) resolve(res);
    }

    function onClose() {
      if (ui && ui.isRunning()) {
        ui.abort();
        setTimeout(() => modal.close(), 300);
      } else {
        modal.close();
      }
    }
  });
}
