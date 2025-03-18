// const { Calendar } = window.VanillaCalendarPro; // Desestructurar el constructor

// // Variable global para almacenar las fechas seleccionadas previamente
// let lastSelectedDates = [];

// function initSelectMultipleFecha(input) {
//     input.placeholder = "Seleccionar"; // Volver a mostrar el placeholder

//     // Eliminar calendarios previos si existen
//     deleteMultipleCalendarDOM();

//     // Configuración de Vanilla Calendar Pro
//     const options = {
//         type: 'default',
//         inputMode: true,
//         selectionDatesMode: 'multiple-ranged',

//         // Si hay fechas guardadas, se usan como predeterminadas
//         selectedDates: lastSelectedDates.length > 0 ? [...lastSelectedDates] : [],

//         onClickDate(self) {
//             if (self.context.selectedDates.length > 1) {
//                 self.context.selectedDates.sort((a, b) => new Date(a) - new Date(b));
//                 input.value = `${reverseDate(self.context.selectedDates[0])} — ${reverseDate(self.context.selectedDates[self.context.selectedDates.length - 1])}`;
//             } else if (self.context.selectedDates.length === 1) {
//                 input.value = reverseDate(self.context.selectedDates[0]);
//             } else {
//                 input.value = '';
//             }

//             // Actualizar la variable global con las fechas seleccionadas
//             lastSelectedDates = [...self.context.selectedDates];
//         },

//         styles: {
//             calendar: 'vc_multipleRango',
//         },

//         locale: {
//             months: {
//                 short: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
//                 long: [
//                     'Enero',
//                     'Febrero',
//                     'Marzo',
//                     'Abril',
//                     'Mayo',
//                     'Junio',
//                     'Julio',
//                     'Agosto',
//                     'Septiembre',
//                     'Octubre',
//                     'Noviembre',
//                     'Diciembre',
//                 ],
//             },
//             weekdays: {
//                 short: ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
//                 long: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
//             },
//         },
//     };

//     // Inicializar el calendario
//     const calendar = new Calendar(`#${input.id}`, options);
//     calendar.init();

//     // Si hay fechas previamente seleccionadas, actualizar el valor del input al cargar el calendario
//     if (lastSelectedDates.length > 0) {
//         if (lastSelectedDates.length > 1) {
//             // Ordenar las fechas cronológicamente para mostrar el rango correcto
//             const sortedDates = [...lastSelectedDates].sort((a, b) => new Date(a) - new Date(b));
//             input.value = `${reverseDate(sortedDates[0])} — ${reverseDate(sortedDates[sortedDates.length - 1])}`;
//         } else {
//             input.value = reverseDate(lastSelectedDates[0]);
//         }
//     }

//     // Mostrar calendario al hacer clic en el input
//     input.addEventListener("click", function () {
//         document.getElementById(`${input.id}`).classList.toggle("visible");
//     });
// }

// // Función para formatear la fecha (YYYY-MM-DD -> DD/MM/YYYY)
// function reverseDate(fecha) {
//     return fecha.split('-').reverse().join('/');
// }

// // Función para eliminar calendarios previos si existen
// function deleteMultipleCalendarDOM() {
//     const calendariosActivos = document.querySelectorAll(".vc_multipleRango");
//     calendariosActivos.forEach(c => c.remove());
// }
const { Calendar } = window.VanillaCalendarPro; // Desestructurar el constructor

// Variable global para almacenar las fechas seleccionadas previamente
let lastSelectedDates = [];

function initSelectMultipleFecha(input) {
    input.placeholder = "Seleccionar"; // Mostrar el placeholder

    // Eliminar calendarios previos si existen
    deleteMultipleCalendarDOM();

    // Configuración de Vanilla Calendar Pro con layout personalizado
    const options = {
        type: 'default',
        inputMode: true,
        selectionDatesMode: 'multiple-ranged',

        // Si hay fechas guardadas, se usan como predeterminadas
        selectedDates: lastSelectedDates.length > 0 ? [...lastSelectedDates] : [],

        layouts: {
            default: `
              <div class="vc-header" data-vc="header" role="toolbar" aria-label="Calendar Navigation">
                <#ArrowPrev />
                <div class="vc-header__content" data-vc-header="content">
                  <#Month />
                  <#Year />
                </div>
                <#ArrowNext />
              </div>
              <div class="vc-wrapper" data-vc="wrapper">
                <#WeekNumbers />
                <div class="vc-content" data-vc="content">
                  <#Week />
                  <#Dates />
                  <#DateRangeTooltip />
                </div>
              </div>
              <#ControlTime />
              <button id="btn-clear" type="button">Limpiar</button>
            `,
        },

        onClickDate(self) {
            if (self.context.selectedDates.length > 1) {
                self.context.selectedDates.sort((a, b) => new Date(a) - new Date(b));
                input.value = `${reverseDate(self.context.selectedDates[0])} — ${reverseDate(self.context.selectedDates[self.context.selectedDates.length - 1])}`;
            } else if (self.context.selectedDates.length === 1) {
                input.value = reverseDate(self.context.selectedDates[0]);
            } else {
                input.value = '';
            }
            // Actualizar la variable global con las fechas seleccionadas
            lastSelectedDates = [...self.context.selectedDates];
        },

        onInit(self) {
            // En lugar de self.container, usamos document.querySelector
            // Buscamos el botón dentro del contenedor del calendario (que es el mismo que el input.id)
            const clearBtn = document.querySelector(`.vc_multipleRango #btn-clear`);
            if (clearBtn) {
                clearBtn.addEventListener('click', function () {
                    // Limpiar el valor del input
                    input.value = '';
                    // Reiniciar la variable global de fechas seleccionadas
                    lastSelectedDates = [];
                    // Limpiar la selección en el calendario
                    self.context.selectedDates = [];

                    self.update({
                        dates: true,
                    });
                });
            }
        },
        onUpdate(self) {
            // En lugar de self.container, usamos document.querySelector
            // Buscamos el botón dentro del contenedor del calendario (que es el mismo que el input.id)
            const clearBtn = document.querySelector(`.vc_multipleRango #btn-clear`);
            if (clearBtn) {
                clearBtn.addEventListener('click', function () {
                    // Limpiar el valor del input
                    input.value = '';
                    // Reiniciar la variable global de fechas seleccionadas
                    lastSelectedDates = [];
                    // Limpiar la selección en el calendario
                    self.context.selectedDates = [];

                    self.update({
                        dates: true,
                    });
                });
            }
        },

        styles: {
            calendar: 'vc_multipleRango',
        },

        locale: {
            months: {
                short: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                long: [
                    'Enero',
                    'Febrero',
                    'Marzo',
                    'Abril',
                    'Mayo',
                    'Junio',
                    'Julio',
                    'Agosto',
                    'Septiembre',
                    'Octubre',
                    'Noviembre',
                    'Diciembre',
                ],
            },
            weekdays: {
                short: ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
                long: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
            },
        },
    };

    // Inicializar el calendario
    const calendar = new Calendar(`#${input.id}`, options);
    calendar.init();

    // Si hay fechas previamente seleccionadas, actualizar el valor del input al cargar el calendario
    if (lastSelectedDates.length > 0) {
        if (lastSelectedDates.length > 1) {
            const sortedDates = [...lastSelectedDates].sort((a, b) => new Date(a) - new Date(b));
            input.value = `${reverseDate(sortedDates[0])} — ${reverseDate(sortedDates[sortedDates.length - 1])}`;
        } else {
            input.value = reverseDate(lastSelectedDates[0]);
        }
    }

    // Mostrar/ocultar calendario al hacer clic en el input
    input.addEventListener("click", function () {
        document.getElementById(`${input.id}`).classList.toggle("visible");
    });
}

// Función para formatear la fecha (de "YYYY-MM-DD" a "DD/MM/YYYY")
function reverseDate(fecha) {
    return fecha.split('-').reverse().join('/');
}

// Función para eliminar calendarios previos si existen
function deleteMultipleCalendarDOM() {
    const calendariosActivos = document.querySelectorAll(".vc_multipleRango");
    calendariosActivos.forEach(c => c.remove());
}
