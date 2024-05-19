const options = {
  input: true,
  type: 'default',
  settings: {
    lang: 'es',
    selection: {
      day: 'multiple-ranged',
    },
  },
  actions: {
    changeToInput(e, self) {
      if (!self.HTMLInputElement) return;
      if (self.selectedDates[1]) {
        self.selectedDates.sort((a, b) => +new Date(a) - +new Date(b));
        self.HTMLInputElement.value = `${reverseDate(self.selectedDates[0])} — ${reverseDate(self.selectedDates[self.selectedDates.length - 1])}`;
      } else if (self.selectedDates[0]) {
        self.HTMLInputElement.value = reverseDate(self.selectedDates[0]);
      } else {
        self.HTMLInputElement.value = '';
      }
    },
  },
};

const calendarInput = new VanillaCalendar('#calendar-input', options);
calendarInput.init();

function reverseDate(fecha) {
  return fecha.split('-').reverse().join('/');
}