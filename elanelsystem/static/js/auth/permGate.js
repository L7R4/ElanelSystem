// elanelsystem/static/js/auth/permGate.js
(() => {
  const CACHE_KEY = "perm-cache-v1";
  let ctx = null;

  function normalize(d) {
    // Guardamos permisos en Set para consultas O(1)
    const perms = new Set(d?.perms || []);
    return { ...d, perms };
  }

  async function fetchMe() {
    if (ctx) return ctx;
    try {
      const cached = sessionStorage.getItem(CACHE_KEY);
      if (cached) {
        ctx = normalize(JSON.parse(cached));
        return ctx;
      }
    } catch (_) {}

    const r = await fetch("/usuario/api/me/", {
        credentials: "same-origin",
        headers: { "X-Requested-With": "XMLHttpRequest" },
        cache: "no-store",
    });
    if (r.status === 401 || r.status === 403) {
        try { sessionStorage.removeItem("perm-cache-v1"); } catch(_) {}
        try { localStorage.setItem("perm-broadcast", "logout:" + Date.now()); } catch(_) {}
        throw new Error("Unauthorized");
    }
    const data = await r.json();
    ctx = normalize(data);
    try { sessionStorage.setItem(CACHE_KEY, JSON.stringify(data)); } catch (_) {}
    return ctx;
  }

  function can(perm) {
    return !!(ctx && ctx.perms.has(perm));
  }
  function canAny(list) {
    return (list || []).some(p => can(p));
  }
  function canAll(list) {
    return (list || []).every(p => can(p));
  }

  // Aplica directivas a elementos presentes (o nuevos)
  function applyDirectives(root = document) {
    const nodes = root.querySelectorAll("[data-perm],[data-any-perm],[data-all-perm]");
    nodes.forEach(el => {
      const single = el.getAttribute("data-perm");
      const any = (el.getAttribute("data-any-perm") || "").split(",").map(s => s.trim()).filter(Boolean);
      const all = (el.getAttribute("data-all-perm") || "").split(",").map(s => s.trim()).filter(Boolean);

      let ok = true;
      if (single) ok = can(single);
      if (any.length) ok = canAny(any);
      if (all.length) ok = canAll(all);

      // Oculta si no tiene permiso (no lo elimina para evitar saltos de layout)
      el.hidden = !ok;
      el.toggleAttribute("data-perm-denied", !ok);
    });
  }

  async function init() {
    try {
      await fetchMe();
      applyDirectives();
      // Escuchar nuevos nodos (componentes creados por JS)
      const mo = new MutationObserver(muts => {
        muts.forEach(m => {
          m.addedNodes && m.addedNodes.forEach(n => {
            if (n.nodeType === 1) applyDirectives(n);
          });
        });
      });
      mo.observe(document.documentElement, { childList: true, subtree: true });
      document.dispatchEvent(new CustomEvent("perm:ready", { detail: { ctx } }));
    } catch (e) {
      console.warn("permGate init failed", e);
    }
  }

  // Helpers para tu código JS
  function ensurePerm(perm, fn) { if (can(perm)) fn?.(); }
  function ensureAll(perms, fn) { if (canAll(perms)) fn?.(); }
  function ensureAny(perms, fn) { if (canAny(perms)) fn?.(); }

  window.PERM_GATE = { init, can, canAny, canAll, ensurePerm, ensureAll, ensureAny, get context(){ return ctx; }, refresh: () => { sessionStorage.removeItem(CACHE_KEY); ctx = null; return init(); } };
})();
