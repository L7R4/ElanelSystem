
function initSelectSingleFecha(input) {
    const { Calendar } = window.VanillaCalendarPro;
    deleteSingleCalendarDOM()

    const options = {
        inputMode: true,
        // positionToInput: 'auto',
        styles: {
            calendar: 'vc_singleCalendar',
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

        onChangeToInput(self) {
            if (!self.context.inputElement) return;
            if (self.context.selectedDates[0]) {
                self.context.inputElement.value = reverseDate(self.context.selectedDates[0]);
                // if you want to hide the calendar after picking a date
                self.hide();
            } else {
                self.context.inputElement.value = '';
            }
        },
    };

    const calendarInput = new Calendar(`#${input.id}`, options);
    calendarInput.init();

}

function deleteSingleCalendarDOM() {
    const calendariosActivos = document.querySelectorAll(".vc_singleCalendar");
    calendariosActivos.forEach(c => c.remove());
}

function reverseDate(fecha) {
    return fecha.split('-').reverse().join('/');
}

// Variable global para almacenar la fecha seleccionada previamente (en formato "yyyy-mm-dd")
// let lastSelectedDate = null;

// function initSelectSingleFecha(input) {
//     const { Calendar } = window.VanillaCalendarPro;
//     deleteSingleCalendarDOM();

//     // Si lastSelectedDate ya tiene un valor, se utiliza como fecha predeterminada
//     const options = {
//         inputMode: true,
//         styles: {
//             calendar: 'vc_singleCalendar',
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
//         // Se define la fecha seleccionada por defecto usando la variable global
//         selectedDates: lastSelectedDate ? [lastSelectedDate] : [],
//         onChangeToInput(self) {
//             if (!self.context.inputElement) return;
//             if (self.context.selectedDates[0]) {
//                 // Se actualiza la variable global con la nueva fecha seleccionada
//                 lastSelectedDate = self.context.selectedDates[0];
//                 // Convertir el formato de "yyyy-mm-dd" a "dd/mm/yyyy" para mostrarlo en el input
//                 self.context.inputElement.value = reverseDate(self.context.selectedDates[0]);
//                 // Oculta el calendario si lo deseas
//                 self.hide();
//             } else {
//                 self.context.inputElement.value = '';
//             }
//         },
//     };

//     const calendarInput = new Calendar(`#${input.id}`, options);
//     calendarInput.init();
// }

// function deleteSingleCalendarDOM() {
//     const calendariosActivos = document.querySelectorAll(".vc_singleCalendar");
//     calendariosActivos.forEach(c => c.remove());
// }

// // Función que invierte el formato de la fecha de "yyyy-mm-dd" a "dd/mm/yyyy"
// function reverseDate(fecha) {
//     return fecha.split('-').reverse().join('/');
// }
