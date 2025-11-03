/**
 * Crea un “abridor de modal” reusable con Tingle.
 *
 * @param {Object} modalOpts  Opciones Tingle (footer forzado en true).
 * @param {Object} config
 *  - buildContent(ctx) => string HTML del contenido del modal.
 *  - init?(root, ctx) => void | cleanup fn. Se llama tras setContent; útil para bindear eventos puntuales.
 *  - validate?(root, ctx) => boolean. Habilita/deshabilita Confirmar (true = habilitar).
 *  - run({ root, signal, ctx, setStatus, confirmBtn, closeBtn }) => Promise<{ ok:boolean, message?:string, redirect?:string }>
 *  - texts?: { working?, success?, error?, canceled? }
 *  - buttons?: { confirm?, cancel? }
 *  - statusSelector?: string  (selector donde montar el loader; si no existe se crea un <div data-status>)
 *  - autoCloseOnSuccess?: boolean (default true)
 *  - closeDelayMs?: number     (default 400)
 *
 * @returns (ctx) => Promise<{ result?:any, ok?:boolean, canceled?:boolean, error?:any }>
 */
function withTingleAction(modalOpts = {}, config) {
  const {
    buildContent,
    init,
    validate,
    run,
    texts = {},
    buttons = {},
    statusSelector,
    autoCloseOnSuccess = true,
    closeDelayMs = 400,
  } = config;

  if (typeof buildContent !== 'function') {
    throw new Error('withTingleAction: buildContent(ctx) es obligatorio y debe retornar HTML.');
  }
  if (typeof run !== 'function') {
    throw new Error('withTingleAction: run(...) es obligatorio.');
  }

  // Devuelve un abridor de modal
  return function open(ctx = {}) {
    return new Promise((resolve) => {
      let controller = null;
      let inFlight = false;
      let willDestroy = false;
      let cleanupInit = null;

      const modal = new tingle.modal({
        // forzamos footer true, el resto lo mergeamos
        footer: true,
        closeMethods: ['button', 'overlay'],
        cssClass: [],
        ...modalOpts,
        onClose: () => {
          // abortar si hay algo en curso
          if (inFlight && controller && !controller.signal.aborted) controller.abort();
          willDestroy = true; // destruimos cuando termine la transición
          // si el usuario cerró manualmente y no hubo resultado, resolvemos como cancelado
          if (!inFlight) resolve({ canceled: true });
          if (typeof modalOpts.onClose === 'function') {
            try { modalOpts.onClose(); } catch {}
          }
        }
      });

      // Contenido
      const html = buildContent(ctx);
      modal.setContent(html);

      // Botones
      const confirmLabel = buttons.confirm || 'Confirmar';
      const cancelLabel  = buttons.cancel  || 'Cerrar';

      const btnConfirm = modal.addFooterBtn(
        confirmLabel,
        'tingle-btn tingle-btn--primary add-button-default tgl-action-confirm',
        onConfirm
      );
      const btnCancel = modal.addFooterBtn(
        cancelLabel,
        'tingle-btn tingle-btn--default button-default-style tgl-action-cancel',
        onCancel
      );

      // Destrucción segura post-cierre (evita errores de classList en tingle)
      modal.modal.addEventListener('transitionend', () => {
        const isClosed = !modal.modal.classList.contains('tingle-modal--visible');
        if (willDestroy && isClosed) {
          try { if (typeof cleanupInit === 'function') cleanupInit(); } catch {}
          modal.destroy();
        }
      });

      // Scope al modal actual
      const root = modal.modalBoxContent || modal.modal;

      // Status mount / loader
      let statusMount = statusSelector ? root.querySelector(statusSelector) : root.querySelector('[data-status]');
      if (!statusMount) {
        statusMount = document.createElement('div');
        statusMount.setAttribute('data-status', '');
        statusMount.style.marginTop = '.75rem';
        // lo insertamos al final del primer form, o al final del contenido
        const form = root.querySelector('form');
        (form || root).appendChild(statusMount);
      }
      const loader = makeInlineLoader(statusMount, { text: texts.working || 'Procesando...' });

      // Estado inicial del botón Confirmar
      function updateConfirm() {
        const valid = typeof validate === 'function' ? !!validate(root, ctx) : true;
        btnConfirm.disabled = inFlight || !valid;
      }
      btnConfirm.disabled = true; // por defecto

      // Bind input/change para validar (delegado)
      root.addEventListener('input', updateConfirm);
      root.addEventListener('change', updateConfirm);

      // Hook de inicialización opcional (ej: listeners específicos)
      if (typeof init === 'function') {
        cleanupInit = init(root, ctx) || null;
      }

      // Abrir modal
      modal.open();
      // validar al abrir (por si hay valores precargados)
      setTimeout(updateConfirm, 0);

      async function onConfirm() {
        if (inFlight) return;
        inFlight = true;
        updateConfirm();
        btnCancel.disabled = true;
        loader.reset();
        loader.show(texts.working || 'Procesando...');

        controller = new AbortController();

        // helpers para el run
        const setStatus = {
          working: (msg) => loader.show(msg || texts.working || 'Procesando...'),
          success: (msg) => loader.success(msg || texts.success || 'Listo'),
          error:   (msg) => loader.error(msg || texts.error   || 'Ocurrió un error'),
          canceled:(msg) => loader.error(msg || texts.canceled|| 'Operación cancelada'),
        };

        try {
          const result = await run({
            root,
            signal: controller.signal,
            ctx,
            setStatus,
            confirmBtn: btnConfirm,
            closeBtn: btnCancel,
          });

          if (!result || result.ok === false) {
            setStatus.error(result?.message);
            inFlight = false;
            btnCancel.disabled = false;
            updateConfirm();
            // No cerramos; dejamos que el usuario reintente
            return;
          }

          setStatus.success(result?.message);
          inFlight = false;

          // cerrar opcionalmente
          if (autoCloseOnSuccess) {
            setTimeout(() => modal.close(), closeDelayMs);
          }
          // resolvemos con el resultado de la acción
          resolve({ ok: true, result });

        } catch (err) {
          if (err?.name === 'AbortError') {
            setStatus.canceled();
            setTimeout(() => modal.close(), 300);
            resolve({ canceled: true });
          } else {
            setStatus.error(texts.error || 'Error de red. Intenta nuevamente.');
            inFlight = false;
            btnCancel.disabled = false;
            updateConfirm();
            resolve({ ok: false, error: err });
          }
        }
      }

      function onCancel() {
        if (inFlight && controller && !controller.signal.aborted) {
          controller.abort(); // el catch mostrará “cancelado” y cerrará
        } else {
          modal.close();
        }
      }
    });
  };
}
