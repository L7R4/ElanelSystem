// calendarSingle-input.js (ESM)
export function initInputCalendar(selector, options = {}) {
  const VC = window.VanillaCalendarPro;
  if (!VC?.Calendar) throw new Error('VanillaCalendarPro no está cargado');

  const inputEl = document.querySelector(selector);
  if (!inputEl) return null;

  // --- Config contenedor scrolleable (por defecto: el form) ---
  const scrollContainer =
    (typeof options.scrollContainer === 'string'
      ? document.querySelector(options.scrollContainer)
      : options.scrollContainer) ||
    inputEl.closest('#form_create_sale') ||
    inputEl.closest('form') ||
    document.body;

  const pad2 = (n) => String(n).padStart(2, '0');
  const isoFromDate = (d) => `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}`;
  const formatToInput =
    options.formatToInput ||
    ((iso) => {
      if (!iso) return '';
      const [y, m, d] = iso.split('-');
      return `${pad2(d)}/${pad2(m)}/${y}`; // dd/MM/yyyy
    });

  const todayISO = isoFromDate(new Date());
  const disableFuture = !!options.disableFuture;
  const disablePast = !!options.disablePast;

  // --- Helpers de popup ---
  const getPopupEl = () => {
    const list = document.querySelectorAll('.vc');
    return list.length ? list[list.length - 1] : null;
  };

  const mountPopupInsideContainer = (popup) => {
    if (!popup || !scrollContainer) return;
    if (popup.parentElement !== scrollContainer) {
      scrollContainer.appendChild(popup);
    }
    popup.style.position = 'absolute';
  };

  const positionPopupUnderInput = () => {
    const popup = getPopupEl();
    if (!popup || !scrollContainer || !inputEl) return;

    const iRect = inputEl.getBoundingClientRect();
    const cRect = scrollContainer.getBoundingClientRect();

    const offsetY = options.offsetY ?? 6;
    const left = iRect.left - cRect.left + scrollContainer.scrollLeft;
    const top = iRect.top - cRect.top + scrollContainer.scrollTop + inputEl.offsetHeight + offsetY;

    popup.style.left = `${left}px`;
    popup.style.top = `${top}px`;
    if (options.popupMinWidth) popup.style.minWidth = `${options.popupMinWidth}px`;
  };

  // --- Deshabilitar fechas (DOM) ---
  const applyDateDisablers = () => {
    const popup = getPopupEl();
    if (!popup) return;

    // La lib pinta cada día con data-vc-date="YYYY-MM-DD"
    const cells = popup.querySelectorAll('[data-vc-date]');
    cells.forEach((cell) => {
      const iso = cell.getAttribute('data-vc-date');
      let disabled = false;
      if (disableFuture && iso > todayISO) disabled = true;
      if (disablePast && iso < todayISO) disabled = true;

      if (disabled) {
        cell.classList.add('is-disabled');
        cell.setAttribute('aria-disabled', 'true');
        cell.tabIndex = -1;
        cell.style.pointerEvents = 'none';
      } else {
        cell.classList.remove('is-disabled');
        cell.removeAttribute('aria-disabled');
        cell.style.pointerEvents = '';
      }
    });
  };

  let observer = null;
  const observePopup = (popup) => {
    if (!popup) return;
    if (observer) observer.disconnect();
    observer = new MutationObserver(() => {
      // Cada vez que cambia el mes o se re-renderiza, re-aplico
      applyDateDisablers();
      positionPopupUnderInput();
    });
    observer.observe(popup, { childList: true, subtree: true });
  };

  const schedulePositioning = () => {
    requestAnimationFrame(() => {
      const popup = getPopupEl();
      if (!popup) return;
      mountPopupInsideContainer(popup);
      positionPopupUnderInput();
      applyDateDisablers();
      observePopup(popup);
    });
  };

  const cal = new VC.Calendar(selector, {
    inputMode: true,
    positionToInput: options.positionToInput ?? 'auto',
    firstWeekday: options.firstWeekday ?? 1,
    locale: options.locale ?? 'es-AR',

    onChangeToInput(self) {
      let iso = self.context?.selectedDates?.[0] || '';

      // Barrera lógica por si algo se escapa
      if ((disableFuture && iso > todayISO) || (disablePast && iso < todayISO)) {
        iso = '';
        self.selectedDates = [];
        self.update({ dates: true });
      }

      inputEl.value = formatToInput(iso);
      options.calendar?.onChangeToInput?.(self);
      positionPopupUnderInput();
      applyDateDisablers();
    },

    onClickDate(self) {
      const iso = self.context?.selectedDates?.[0] || '';

      // Barrera lógica
      if ((disableFuture && iso > todayISO) || (disablePast && iso < todayISO)) {
        // cancelar selección visual
        self.selectedDates = [];
        self.update({ dates: true });
        applyDateDisablers();
        return;
      }

      inputEl.value = formatToInput(iso);
      if (options.autoClose !== false) self.hide();
      options.onSelect?.(iso, inputEl, self);
      options.calendar?.onClickDate?.(self);
    },

    layouts: {
      default: `
        <div class="\${self.styles.header}" data-vc="header" role="toolbar" aria-label="\${self.labels.navigation}">
          <#ArrowPrev [month] />
          <div class="\${self.styles.headerContent}" data-vc-header="content">
            <#Month /><#Year />
          </div>
          <#ArrowNext [month] />
        </div>

        <div class="buttonsCustom" style="display:flex;gap:.5rem;justify-content:flex-end;">
          <button type="button" class="vc-btn button-default-style" data-vc-btn="today">${options.todayLabel ?? 'Hoy'}</button>
          <button type="button" class="vc-btn button-default-style" data-vc-btn="clear">${options.clearLabel ?? 'Limpiar'}</button>
        </div>

        <div class="\${self.styles.wrapper}" data-vc="wrapper">
          <#WeekNumbers />
          <div class="\${self.styles.content}" data-vc="content">
            <#Week />
            <#Dates />
            <#DateRangeTooltip />
          </div>
        </div>
        <#ControlTime />
      `,
    },

    onInit(self) {
      const hookOpen = () => schedulePositioning();
      inputEl.addEventListener('focus', hookOpen);
      inputEl.addEventListener('click', hookOpen);

      const onScroll = () => positionPopupUnderInput();
      const onResize = () => positionPopupUnderInput();
      scrollContainer.addEventListener('scroll', onScroll, { passive: true });
      window.addEventListener('resize', onResize);

      // Botones Hoy / Limpiar
      document.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-vc-btn]');
        if (!btn || !btn.closest('.vc')) return;

        if (btn.dataset.vcBtn === 'today') {
          const now = new Date();
          const iso = isoFromDate(now);

          // Si "hoy" está bloqueado por disablePast/disableFuture, no hacemos nada
          if (
            (disableFuture && iso > todayISO) ||
            (disablePast && iso < todayISO)
          ) return;

          self.selectedDates = [iso];
          self.selectedYear = now.getFullYear();
          self.selectedMonth = now.getMonth() + 1;
          inputEl.value = formatToInput(iso);
          self.update({ dates: true, month: true, year: true });
          if (options.autoClose !== false) self.hide();
          options.onSelect?.(iso, inputEl, self);
        }

        if (btn.dataset.vcBtn === 'clear') {
          self.selectedDates = [];
          inputEl.value = '';
          self.update({ dates: true });
          if (options.autoClose !== false) self.hide();
          options.onClear?.(inputEl, self);
        }
      });

      schedulePositioning();
      options.calendar?.onInit?.(self);
    },

    ...options.calendar,
  });

  cal.init();
  return cal;
}
