
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


// Numero Clientes
const numero_clientes_chart = document.getElementById('numero_clientes_chart')

numero_clientes = data.numero_clientes
numero_clientes = numero_clientes.slice(1, numero_clientes.length-1).split(",")

new Chart(numero_clientes_chart, {
  type: 'line',
  data: {
    labels: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
    datasets: [{
      label: 'Numero de clientes',
      data: numero_clientes,
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