//#region Funcion del formulario FETCH
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function formFETCH(form, url) {
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
            },
            body: JSON.stringify(form)
        })
        if (!res.ok) {
            throw new Error("Error")
        }
        const data = await res.json()
        return data;
    } catch (error) {
    }
}
//#endregion  

const url = window.location.pathname

function updateQuery(prev, params) {
    const u = new URL(prev, window.location.origin);
    Object.entries(params).forEach(([k, v]) => {
        if (v === undefined || v === null || v === '') u.searchParams.delete(k);
        else u.searchParams.set(k, v);
    });
    return u.pathname + u.search; // ruta relativa
}

const grid = new gridjs.Grid({
    columns: ["Nombre completo", "DNI", "Teléfono", "Sucursal", "Localidad", "Provincia"],
    fixedHeader: true,
    resizable: true,
    search: {
        server: {
            url: (prev, keyword) => updateQuery(prev, { search: keyword, page: 1 }) // resetea a pág. 1
        }
    },
    pagination: {
        limit: 30,
        server: {
            // Grid.js usa page 0-based; Paginator es 1-based ⇒ page + 1
            url: (prev, page, limit) => updateQuery(prev, { page: page + 1, page_size: limit })
        }
    },
    server: {
        url,
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        handle: (res) => {
            if (res.ok) return res.json();
            return res.text().then(t => { throw new Error(`[${res.status}] ${t.slice(0, 200)}`); });
        },
        then: (data) => data.customers.map(c => [
            c.nombre, c.dni, c.tel, c.sucursal, c.loc, c.prov
        ]),
        total: (data) => data.total // Grid.js usa esto para armar la paginación
    },
    language: gridjs.l10n.esES
});

grid.render(document.getElementById("customers_table"));