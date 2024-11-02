const options = {
  input: true,
  actions: {
    changeToInput(e, self) {
      if (!self.HTMLInputElement) return;
      if (self.selectedDates[0]) {
        self.HTMLInputElement.value = self.selectedDates[0];
        // if you want to hide the calendar after picking a date
        self.hide();
      } else {
        self.HTMLInputElement.value = '';
      }
    },
  },
  settings: {
    visibility: {
      positionToInput: 'center',
    },
  },
};
  
const calendar = new VanillaCalendar('#calendar-input', options);
calendar.init();