let chartDinero = Highcharts.chart('containerDinero', {
    chart: {
        type: 'column',
        backgroundColor: '#ffffff00',
        zooming: {
            key: "alt",
            type: "xy"
        }
    },

    title: {
        text: '',
        align: 'left'
    },

    xAxis: {
        categories: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun','Jul','Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
        labels:{
            style:{
                color: "#fff",
                fontSize: "14px"
            }
        }
    },

    yAxis: {
        min: 0,
        title: {
            text: ''
        },
        stackLabels: {
            enabled: false
        }
    },

    legend: {
        enabled: false
    },

    plotOptions: {
        series: {
            borderRadius: 2,
            borderWidth: 1,
            borderColor: '#ffffff5c',
            dataLabels: {
                enabled: false
            },
            stacking: 'normal'
        }
    },

    series: [
    {
        name: 'Ingresos',
        // data: [14,8,8,12,5,5,5,5,5,5,5],
        color: "#1753ED",
        label: false,
    },
    {
        name: 'Egresos',
        // data: [14,8,8,12,5,5,5,5,5,5,5],
        color:"#e44040fc",
        label: false,
    }, 
    ]
});

// FETCH PARA FLUCTUACION DE DINERO
async function fetchFluctuacionDinero() {
    const response = await fetch("/requestmovscrm/", {
        method: 'get',
        headers: {'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'},
        cache: 'no-store',
    });
    const data = await response.json();
    return data;
}

async function updateChartFluctuacionDinero() {
    try {
        const data = await fetchFluctuacionDinero();
        const context = {
            ingresos: data.sumasIngreso_por_mes,
            egresos: data.sumasEgreso_por_mes
        };
        console.log(context)

        chartDinero.update({
            series: [
                {
                    name: 'Ingresos',
                    data: context.ingresos,
                    color: "#1753ED",
                    label: false,
                },
                {
                    name: 'Egresos',
                    data: context.egresos,
                    color: "#e44040fc",
                    label: false,
                },
            ]
        });
    } catch (error) {
        console.error('Error fetching or updating chart:', error);
    }
}

updateChartFluctuacionDinero();

