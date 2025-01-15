document.addEventListener('DOMContentLoaded', () => {
    const inputs = document.querySelectorAll(".inputSearchSelect"); // IDs de los inputs que se quieren convertir en select
    const queryParams = {}; // Variable para almacenar los valores de los inputs

    inputs.forEach(input => {
        const input = input.id;
        const dropdown = document.getElementById(`${input}-options`);

        input.addEventListener('input', () => {
            const query = input.value.trim();
            queryParams[input] = query; // Guardar el valor del input en queryParams
            // dropdown.innerHTML = '';

            if (query === '') {
                const li = document.createElement('li');
                li.textContent = 'Escriba para filtrar';
                dropdown.appendChild(li);
                dropdown.style.display = 'block';
                return;
            }

            if (query.length > 1) {
                // Aquí puedes usar queryParams si necesitas enviarlos todos al backend
                const url = `/search-usuarios/?${new URLSearchParams(queryParams)}`;
                
                fetch(url)
                    .then(response => response.json())
                    .then(data => {
                        dropdown.innerHTML = '';
                        dropdown.style.display = 'block';

                        if (data.length === 0) {
                            const li = document.createElement('li');
                            li.textContent = 'Sin resultados';
                            li.classList.add('no-results');
                            dropdown.appendChild(li);
                        } else {
                            data.forEach(option => {
                                const li = document.createElement('li');
                                li.textContent = option.name;
                                li.addEventListener('click', () => {
                                    input.value = option.name;
                                    queryParams[input] = option.name; // Actualizar queryParams
                                    dropdown.style.display = 'none';
                                });
                                dropdown.appendChild(li);
                            });
                        }
                    })
                    .catch(err => console.error('Error fetching options:', err));
            }
        });

        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target) && !input.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });
    });
});


