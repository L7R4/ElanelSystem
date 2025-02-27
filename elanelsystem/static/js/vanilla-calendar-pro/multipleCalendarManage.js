const { Calendar } = window.VanillaCalendarPro; // Desestructurar el constructor

function initSelectFecha(input) {
    console.log(input);

    // Eliminar calendarios previos si existen
    const calendariosActivos = document.querySelectorAll(".vc_multipleRango");
    calendariosActivos.forEach(c => c.remove());

    // Configuración de Vanilla Calendar Pro
    const options = {
        type: 'multiple',
        inputMode: true,
        // selectionDatesMode: 'multiple-ranged',
        selection: {
            mode: 'multiple-ranged'
        },
        settings: {
            lang: 'es',
        },
        // layouts: {
        //     default: `<#ControlNavigation /><#Days />`,
        // },
        onSelect(self) {
            if (self.context.selectedDates.length > 1) {
                self.context.selectedDates.sort((a, b) => new Date(a) - new Date(b));
                input.value = `${reverseDate(self.context.selectedDates[0])} — ${reverseDate(self.context.selectedDates[self.context.selectedDates.length - 1])}`;
            } else if (self.context.selectedDates.length === 1) {
                input.value = reverseDate(self.context.selectedDates[0]);
            } else {
                input.value = '';
            }
        },
        styles: {
            calendar: 'vc_multipleRango',
        },
    };

    // Inicializar el calendario
    const calendar = new Calendar(`#${input.id}`, options);
    calendar.init();

    // Mostrar calendario al hacer clic en el input
    input.addEventListener("click", function () {
        document.getElementById(`${input.id}`).classList.toggle("visible");
    });
}

// Función para formatear la fecha (YYYY-MM-DD -> DD/MM/YYYY)
function reverseDate(fecha) {
    return fecha.split('-').reverse().join('/');
}
