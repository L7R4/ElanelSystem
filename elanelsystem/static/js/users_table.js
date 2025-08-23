const url = window.location.pathname;

function updateQuery(prev, params) {
  const u = new URL(prev, window.location.origin);
  Object.entries(params).forEach(([k, v]) => {
    if (v === undefined || v === null || v === "") u.searchParams.delete(k);
    else u.searchParams.set(k, v);
  });
  return u.pathname + u.search;
}

const grid = new gridjs.Grid({
  columns: [
    "Nombre",
    "DNI",
    "Correo",
    "Sucursal",
    "Teléfono",
    "Rango",
  ],
  fixedHeader: true,
  resizable: true,
  search: {
    server: {
      url: (prev, keyword) => updateQuery(prev, { search: keyword, page: 1 }),
    },
  },
  pagination: {
    limit: 30,
    server: {
      url: (prev, page, limit) =>
        updateQuery(prev, { page: page + 1, page_size: limit }),
    },
  },
  server: {
    url,
    headers: {
      Accept: "application/json",
      "X-Requested-With": "XMLHttpRequest",
    },
    handle: (res) => {
      if (res.ok) return res.json();
      return res.text().then((t) => {
        throw new Error(`[${res.status}] ${t.slice(0, 200)}`);
      });
    },
    then: (data) =>
      data.users.map((u) => [
        u.nombre,
        u.dni,
        u.email,
        u.sucursales.join(", "),
        u.tel,
        u.rango,
      ]),
    total: (data) => data.total,
  },
  language: gridjs.l10n.esES,
  style: {
    table: {
      "font-family": "'Raleway', sans-serif",
      "font-size": "1.4rem",
    },
    th: {
      "background-color": "var(--blue-3)",
      color: "white",
      border: "none",
      "text-align": "center",
    },
    td: {
      "text-align": "center",
      border: "none",
    },
  },
});

grid.render(document.getElementById("users_table"));

