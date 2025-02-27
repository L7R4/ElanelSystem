const { Calendar } = window.VanillaCalendarPro; // Desestructurar el constructor

function initSelectFecha(input) {
    console.log(input);

    // Eliminar calendarios previos si existen
    deleteCalendarDOM()

    // Configuración de Vanilla Calendar Pro
    const options = {
        type: 'default',
        inputMode: true,
        selectionDatesMode: 'multiple-ranged',

        onClickDate(self) {
            console.log(self.context.selectedDates);
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
    console.log(calendar)


    // Mostrar calendario al hacer clic en el input
    input.addEventListener("click", function () {
        document.getElementById(`${input.id}`).classList.toggle("visible");
    });
}

// Función para formatear la fecha (YYYY-MM-DD -> DD/MM/YYYY)
function reverseDate(fecha) {
    return fecha.split('-').reverse().join('/');
}

// Función para eliminar calendarios previos si existen
function deleteCalendarDOM() {
    const calendariosActivos = document.querySelectorAll(".vc_multipleRango");
    calendariosActivos.forEach(c => c.remove());
}