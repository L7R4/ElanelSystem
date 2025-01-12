document.addEventListener('DOMContentLoaded', () => {
    const inputs = ['vendedores', 'supervisores'];

    inputs.forEach(inputName => {
        const input = document.getElementById(inputName);
        const dropdown = document.getElementById(`${inputName}-options`);

        input.addEventListener('input', () => {
            const query = input.value.trim();
            dropdown.innerHTML = '';

            if (query === '') {
                const li = document.createElement('li');
                li.textContent = 'Escriba para filtrar';
                dropdown.appendChild(li);
                dropdown.style.display = 'block';
                return;
            }

            if (query.length > 1) {
                fetch(`/search-${inputName}/?q=${query}`)
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
