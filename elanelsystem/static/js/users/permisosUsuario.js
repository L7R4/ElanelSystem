let itemsPermisos = document.querySelectorAll("#itemsPermisos > ul > input")
let guardarPermisosUsuario = document.getElementById("guardarPermisosUsuario")
let successMessage = document.querySelector(".wrapperMessageSuccess")

// FUNCTION FETCH - - - - - - - - -
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
async function fetchCRUD(body, url) {
    try {
        let response = await fetch(url, {
            method: "POST",
            body: JSON.stringify(body),
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
            }
        })
        if (!response.ok) {
            throw new Error("Error")
        }
        const data = await response.json();
        return data;
    } catch (error) {
    }
}
// - - - - - - - - - - - - - - - - -

// Resaltar visualmente el permiso al tildar/destildar
itemsPermisos.forEach(element => {
    element.addEventListener("change", () => {
        element.checked ? element.nextElementSibling.classList.add("perActive") : element.nextElementSibling.classList.remove("perActive");
    })
});

function updatePermisosUsuario() {
    let checkboxes = document.querySelectorAll('#itemsPermisos > ul > input[type="checkbox"]:checked:not(:disabled)');
    let permisosSeleccionados = Array.from(checkboxes).map(checkbox => checkbox.value);

    let body = {
        "permisos": permisosSeleccionados,
    }

    fetchCRUD(body, updatePermisosUsuarioURL).then(data => {
        successMessage.classList.add("active")
        setTimeout(() => {
            successMessage.classList.remove("active")
        }, 3000)

        // Invalida cache de permisos del cliente y refresca el gating si existe
        try { sessionStorage.removeItem("perm-cache-v1"); } catch (_) { }
        if (window.PERM_GATE && typeof PERM_GATE.refresh === "function") {
            PERM_GATE.refresh();
        }
    })
}

guardarPermisosUsuario.addEventListener("click", () => {
    updatePermisosUsuario();
})
