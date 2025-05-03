document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.commission-checkbox').forEach(cb => {
      cb.addEventListener('change', async function(){
        const ventaId = this.dataset.id;
        const nuevoValor = this.checked;
        const response = await fetchFunction({ id: ventaId, value: nuevoValor },toggleUrl)
        console.log(response)   
        
        if(response.status == true){
            console.log("Todo bien")   
            const row = document.getElementById('row-' + ventaId);
            row.classList.add('table-success');
            setTimeout(() => row.classList.remove('table-success'), 1300);
            
        }else{
            console.log("Error")   
        }
      });
    });
  });


  
//#region Fetch data
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

async function fetchFunction(body, url) {
    try {
        let response = await fetch(url, {
            method: 'POST',
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
//#endregion - - - - - - - - - - - - - - -


  