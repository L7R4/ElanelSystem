const { Calendar } = window.VanillaCalendarPro; // Desestructurar el constructor

function initSelectHora(input) {
    console.log(input)

    const calendariosActivos = document.querySelectorAll(".vc_onlyHora")
    calendariosActivos.forEach(c => c.remove())

    const options = {
        inputMode: true,
        selectionTimeMode: 24,
        layouts: {
            default: `
            <#ControlTime />
          `,
        },
        onChangeTime(self) {
            console.log(self.context.selectedTime);
            input.value = self.context.selectedTime
        },
        styles: {
            calendar: 'vc_onlyHora',
        }
    };

    //Configuración de Vanilla Calendar
    const calendar = new Calendar(`#${input.id}`, options);

    calendar.init();

    // Mostrar calendario al hacer clic en el input
    input.addEventListener("click", function () {
        document.getElementById(`${input.id}`).classList.toggle("visible");
    });
}