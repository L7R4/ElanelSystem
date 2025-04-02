const selectsFilters = document.querySelectorAll('.inputFilter');
let url = window.location.href

selectsFilters.forEach(select => {
    select.addEventListener('input', async (e) => {

        createParams(selectsFilters);

        try {
            const data = await fetchFunction(url);
            console.log(data)
            // Actualizar el DOM con los datos recibidos
            updateDOM_vendedores(data.vendedores);
            console.log("weps")

            updateDOM_supervisores(data.supervisores);
            console.log("weps2")

        } catch (error) {
            console.error("Error al obtener datos:", error);
        }
    });
});

// Función para actualizar el DOM de vendedores
function updateDOM_vendedores(vendedores) {
    const container = document.querySelector('.containerVendedores .valuesWrapper .values');
    container.innerHTML = ''; // Limpiar contenido actual
    vendedores.forEach(vendedor => {
        container.innerHTML += `
            <li class="itemValores">
                <div class="backgroundItemVendedores">
                    <div><p>${vendedor.nombre_usuario}</p></div>
                    <div><p>$${vendedor.productividad}</p></div>
                    <div><p>${vendedor.cantidadVentas}</p></div>
                    <div><p>${vendedor.cuotas1Adelantadas}</p></div>
                </div>
            </li>
        `;
    });
}

// Función para actualizar el DOM de supervisores
function updateDOM_supervisores(supervisores) {
    const container = document.querySelector('.containerSupervisores .valuesWrapper .values');
    container.innerHTML = ''; // Limpiar contenido actual
    supervisores.forEach(supervisor => {
        container.innerHTML += `
            <li class="item">
                <div class="backgroundItem">
                    <img class="imageMore" src="/static/images/icons/arrowDown.png" alt="">
                    <div><p>${supervisor.nombre_usuario}</p></div>
                    <div><p>$${supervisor.productividad}</p></div>
                    <div><p>${supervisor.cantidadVentas}</p></div>
                    <div><p>${supervisor.cuotas_1_total}</p></div>

                </div>
                <ul class="detallesItem">
                    <h2>Vendedores a cargo</h2>
                    <div class="tittlesWrapperItem">
                        <ul class="tittles">
                            <li>Vendedor</li>
                            <li>Dinero total</li>
                            <li>Cantidad ventas</li>
                            <li>Cuotas 1</li>
                        </ul>   
                    </div>
                    <div class="valuesWrapperItem">
                        <ul>
                            ${supervisor.vendedoresACargo.map(v => `
                                <li class="itemValores">
                                    <div class="backgroundItemVendedores">
                                        <div><p>${v.nombre_usuario}</p></div>
                                        <div><p>$${v.productividad}</p></div>
                                        <div><p>${v.cantidadVentas}</p></div>
                                        <div><p>${v.cuotas1Adelantadas}</p></div>

                                    </div>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                </ul>
            </li>
        `;
    });
    listenersItemsDisplay()
}

// function updateDOM_total_supervisores(data) {
//     const container = document.querySelector('.containerSupervisores .valuesWrapper .values');
//     container.innerHTML = ''; // Limpiar contenido actual
//     supervisores.forEach(supervisor => {
//         container.innerHTML += `
//             <li class="item">
//                 <div class="backgroundItem">
//                     <img class="imageMore" src="/static/images/icons/arrowDown.png" alt="">
//                     <div><p>${supervisor.nombre_usuario}</p></div>
//                     <div><p>$${supervisor.productividad}</p></div>
//                     <div><p>${supervisor.cantidadVentas}</p></div>
//                 </div>
//                 <ul class="detallesItem">
//                     <h2>Vendedores a cargo</h2>
//                     <div class="tittlesWrapperItem">
//                         <ul class="tittles">
//                             <li>Vendedor</li>
//                             <li>Dinero total</li>
//                             <li>Cantidad total</li>
//                         </ul>   
//                     </div>
//                     <div class="valuesWrapperItem">
//                         <ul>
//                             ${supervisor.vendedoresACargo.map(v => `
//                                 <li class="itemValores">
//                                     <div class="backgroundItemVendedores">
//                                         <div><p>${v.nombre_usuario}</p></div>
//                                         <div><p>$${v.productividad}</p></div>
//                                         <div><p>${v.cantidadVentas}</p></div>
//                                     </div>
//                                 </li>
//                             `).join('')}
//                         </ul>
//                     </div>
//                 </ul>
//             </li>
//         `;
//     });
//     listenersItemsDisplay()
// }

// Función fetch para hacer solicitudes
async function fetchFunction(url) {
    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) throw new Error('Error en la solicitud');

        return await response.json();
    } catch (error) {
        console.error(error);
    }
}

function createParams(inputs) {
    if (url.includes("?")) {
        url = window.location.href;
    }

    inputs.forEach(input => {
        if (input.value.trim() !== "") {
            url += url.includes("?") ? "&" : "?";

            const inputName = input.name; // Obtener el atributo 'name' del input
            const inputValue = input.value; // Obtener el valor seleccionado
            let newParam = `${inputName}=${inputValue}`;
            url += newParam;
        }
    })
}
