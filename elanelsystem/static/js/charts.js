
// Reciviendo argumentos
const data = document.currentScript.dataset

// Ganancias
const ganancias_chart = document.getElementById('ganancias_chart')

ganancias = data.ganancias
ganancias = ganancias.slice(1, ganancias.length-1).split(",")

new Chart(ganancias_chart, {
  type: 'line',
  data: {
    labels: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
    datasets: [{
      label: 'Ventas',
      data: ganancias,
      borderWidth: 1,
    }]
  },
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
}); 


// Gastos
const gastos_chart = document.getElementById('gastos_chart')

gastos = data.gastos
gastos = gastos.slice(1, gastos.length-1).split(",")

new Chart(gastos_chart, {
  type: 'line',
  data: {
    labels: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
    datasets: [{
      label: 'Gastos',
      data: gastos,
      borderWidth: 1,
    }]
  },
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
}); 


// Medios Pago
const medios_pago_chart = document.getElementById('medios_pago_chart')

medios_list = data.medios_list
medios_values = data.medios_values
medios_list = medios_list.slice(1, medios_list.length-1).split(', ')
medios_values = medios_values.slice(1, medios_values.length-1).split(', ')

for (let i=0; i<medios_list.length; i++){
  medios_list[i] = medios_list[i].slice(1, medios_list[i].length-1)
}

new Chart(medios_pago_chart, {
  type: 'pie',
  data: {
    labels: medios_list,
    datasets: [{
      label: 'Pagos',
      data: medios_values,
      borderWidth: 1,
    }]
  }
}); 