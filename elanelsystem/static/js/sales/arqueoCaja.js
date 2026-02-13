const BILLETES = [20000, 10000, 2000, 1000, 500, 200, 100, 50, 20, 10];
const SALDO_ENDPOINT = window.ARQUEO_SALDO_ENDPOINT;

function toNumber(v) {
  const s = String(v ?? "")
    .replace(/[^\d,.-]/g, "") // deja dígitos y separadores
    .replace(/\./g, "") // saca miles (AR usa .)
    .replace(",", "."); // coma -> punto
  const n = Number(s);
  return Number.isFinite(n) ? n : 0;
}

function money(v) {
  return new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "ARS",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(toNumber(v));
}

function moneyNum(v) {
  return new Intl.NumberFormat("es-AR", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(toNumber(v));
}

function recalcPlanilla() {
  let total = 0;

  document.querySelectorAll(".detalleItems .item").forEach((item) => {
    const denomEl = item.querySelector(".monedaValue");
    const inputEl = item.querySelector("input[type='number']");
    const importeEl = item.querySelector(".importeValue");

    const denom = toNumber(denomEl?.textContent);
    const cant = toNumber(inputEl?.value);

    const imp = denom * cant;
    total += imp;

    if (importeEl) importeEl.textContent = moneyNum(imp);
  });

  document.getElementById("totalPlanillaEfectivo").textContent = money(total);
  document.getElementById("totalPlanillaEfectivoInput").value = String(total);

  const saldo = toNumber(document.getElementById("saldoSegunCajaInput").value);
  const diff = total - saldo;

  document.getElementById("diferenciaText").textContent = money(diff);
  document.getElementById("diferenciaInput").value = String(diff);
}

function setSaldoDiario(saldo) {
  const val = toNumber(saldo);
  document.getElementById("saldoSegunCaja").textContent = money(val);
  document.getElementById("saldoSegunCajaInput").value = String(val);
  recalcPlanilla();
}

async function fetchSaldo({ agenciaId, fecha }) {
  const qs = new URLSearchParams();
  qs.set("agencia_id", String(agenciaId));
  if (fecha) qs.set("fecha", String(fecha));

  const res = await fetch(`${SALDO_ENDPOINT}?${qs.toString()}`, {
    method: "GET",
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok || !data?.success) {
    throw new Error(data?.error || "No se pudo obtener el saldo.");
  }
  return data;
}

function setupAgenciaSelect() {
  const hidden = document.getElementById("id_agencia");
  const list = document.getElementById("contenedorSucursal");
  const container = document.querySelector(
    "#sucursalWrapper .containerInputAndOptions",
  );
  if (!hidden || !list || !container) return;

  function getFechaUI() {
    const items = document.querySelectorAll(".subtittleWrapper ul li.data");
    for (const li of items) {
      const lbl = li.querySelector("label")?.textContent?.trim()?.toLowerCase();
      if (lbl === "fecha")
        return li.querySelector("p")?.textContent?.trim() || "";
    }
    return "";
  }

  async function refreshSaldoForSelected() {
    const id = hidden.value?.trim();
    if (!id) return;
    try {
      const fecha = getFechaUI();
      const r = await fetchSaldo({ agenciaId: id, fecha });
      setSaldoDiario(r.saldo);
    } catch (e) {
      console.error(e);
      setSaldoDiario(0);
    }
  }

  const preId = hidden.value?.trim();
  if (preId) {
    const li = list.querySelector(`li[data-value="${CSS.escape(preId)}"]`);
    if (li && typeof window.setSelectValue === "function") {
      window.setSelectValue(
        container,
        { value: preId, label: li.textContent.trim() },
        { fire: false, markSelected: true },
      );
    }
  }

  // ✅ Cuando el select cambie (porque el módulo dispara change/input), buscamos saldo
  hidden.addEventListener("change", () => {
    refreshSaldoForSelected();
  });

  // Inicial: setear saldo mostrado y luego, si hay agencia, refetch saldo real
  const initialSaldoText =
    document.getElementById("saldoSegunCaja")?.textContent ?? "0";
  setSaldoDiario(initialSaldoText);
  refreshSaldoForSelected();
}

function setupBilletes() {
  BILLETES.forEach((b) => {
    const inp = document.getElementById(`p${b}`);
    if (!inp) return;
    inp.addEventListener("input", recalcPlanilla);
  });
}

function getCSRFToken() {
  const el = document.querySelector("input[name='csrfmiddlewaretoken']");
  return el ? el.value : "";
}

function setupSubmit() {
  const btn = document.getElementById("confirmArqueoCaja");
  const form = document.getElementById("formArqueoCaja");
  if (!btn || !form) return;

  btn.addEventListener("click", async () => {
    recalcPlanilla();
    btn.disabled = true;

    try {
      const fd = new FormData(form);

      const res = await fetch(
        form.getAttribute("action") || window.location.pathname,
        {
          method: "POST",
          credentials: "same-origin",
          headers: {
            "X-CSRFToken": getCSRFToken(),
            "X-Requested-With": "XMLHttpRequest",
          },
          body: fd,
        },
      );

      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data?.success) {
        throw new Error(data?.error || "No se pudo guardar el arqueo.");
      }

      window.open(data.urlPDF, "_blank");
      window.location.href = data.urlCaja;
    } catch (e) {
      console.error(e);
      alert(e.message || "Error");
    } finally {
      btn.disabled = false;
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  setupAgenciaSelect();
  setupBilletes();
  recalcPlanilla();
  setupSubmit();
});
