function initSelectSingleDateWithTime(input) {
    const { Calendar } = window.VanillaCalendarPro;
    deleteSingleCalendarTimeDOM();

    const options = {
        inputMode: true,
        selectionTimeMode: 24,
        styles: {
            calendar: 'vc_singleCalendar',
        },
        locale: {
            months: {
                short: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                long: [
                    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
                ],
            },
            weekdays: {
                short: ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
                long: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
            },
        },

        onChangeToInput(self) {
            if (!self.context.inputElement) return;

            const selectedDate = self.context.selectedDates[0]; // "YYYY-MM-DD"
            const selectedTime = self.context.selectedTime; // { hours: "HH", minutes: "MM" }
            console.log(selectedTime)
            if (selectedDate) {
                const formattedDate = reverseDate(selectedDate); // "DD/MM/YYYY"
                const formattedTime = selectedTime
                    ? selectedTime
                    : "00:00"; // Si no seleccionan hora, poner "00:00"

                self.context.inputElement.value = `${formattedDate} ${formattedTime}`;
                // self.hide();
            } else {
                self.context.inputElement.value = '';
            }
        },
    };

    const calendarInput = new Calendar(`#${input.id}`, options);
    calendarInput.init();
}

function deleteSingleCalendarTimeDOM() {
    const calendariosActivos = document.querySelectorAll(".vc_singleCalendar");
    calendariosActivos.forEach(c => c.remove());
}

function reverseDate(fecha) {
    return fecha.split('-').reverse().join('/');
}
