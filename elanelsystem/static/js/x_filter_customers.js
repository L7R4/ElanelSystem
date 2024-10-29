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


function buttonSubmitFilterHTML() {
    return `<button type="button" id="submitFilter" class="add-button-default">Filtrar</button>`
}