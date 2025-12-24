let familiarCount = 1;



function agregarFamiliar() {
  const allFamiliarDivs = document.querySelectorAll('.familiar');
  stringForHTML =`
  <div class ="familiar">
  
    <div class="wrapperFamiliarInput">
      <input type="text" class="input-read-write-default" name="familia_relacion_${familiarCount}" placeholder="Relación con el usuario">
    </div>

    <div class="wrapperFamiliarInput">
      <input type="text" class="input-read-write-default" name="familia_nombre_${familiarCount}" placeholder="Nombre">    
    </div>

    <div class="wrapperFamiliarInput">
      <input type="text" class="input-read-write-default" name="familia_tel_${familiarCount}" placeholder="Teléfono">
    </div>
    <div class="wrapperButtonRemove">
      <button type="button" onclick="removeFamiliar(this)" class="button-remove">-</button>
    </div>
  </div>`;
  
  allFamiliarDivs[allFamiliarDivs.length - 1].insertAdjacentHTML("afterend",stringForHTML);

  familiarCount++;
}

function removeFamiliar(button) {
  button.parentElement.parentElement.remove();
}
