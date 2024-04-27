let familiarCount = 1;



function agregarFamiliar() {
    
  const lastFamiliarDiv = document.querySelectorAll('.familiar');
  const nuevoFamiliarDiv = document.createElement('div');

  nuevoFamiliarDiv.className = 'familiar';

  const relacionInput = document.createElement('input');
  relacionInput.type = 'text';
  relacionInput.name = `familia_relacion_${familiarCount}`;
  relacionInput.placeholder = 'Relación con el usuario';

  const nombreInput = document.createElement('input');
  nombreInput.type = 'text';
  nombreInput.name = `familia_nombre_${familiarCount}`;
  nombreInput.placeholder = 'Nombre';

  const telInput = document.createElement('input');
  telInput.type = 'text';
  telInput.name = `familia_tel_${familiarCount}`;
  telInput.placeholder = 'Teléfono';

  nuevoFamiliarDiv.appendChild(relacionInput);
  nuevoFamiliarDiv.appendChild(nombreInput);
  nuevoFamiliarDiv.appendChild(telInput);
  
  lastFamiliarDiv[lastFamiliarDiv.length - 1].insertAdjacentElement("afterend",nuevoFamiliarDiv);

  familiarCount++;
}
