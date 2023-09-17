const calendarios = document.querySelectorAll(".calendar_button");

let fromMonth_year = document.getElementById("fromMonth_year");
let toMonth_year = document.getElementById("toMonth_year");

// ---------- BOTONES ------------------
// Butones para el calendario de fecha inicial
const fromDatePrevButton = document.getElementById("fromDatePrevIcon");
const fromDateNextButton = document.getElementById("fromDateNextIcon");

// Butones para el calendario de fecha final
const toDatePrevButton = document.getElementById("toDatePrevIcon");
const toDateNextButton = document.getElementById("toDateNextIcon");


// ------------------ INPUTS PARA LOS CALENDARIOS DE INICIO Y FINAL ------------------
let firstDateInput = document.getElementById("fecha_inicial"); 
let endDateInput = document.getElementById("fecha_final");

// ------------------ TEXTO DE FECHA SELECCIONADAS  ------------------
let fromDateContent = document.getElementById("fromDateContent"); // Para el calendario de fecha inicial
let toDateContent = document.getElementById("toDateContent"); // Para el calendario de fecha final


// ------------------ PARA GENERAR LOS DIAS DEL MES DE LOS CALENDARIOS ------------------
let fromNumbers_days = document.querySelector(".fromDatenumbers"); // Para el calendario de fecha inicial
let toNumbers_days = document.querySelector(".toDatenumbers"); // Para el calendario de fecha final


let fromNumbers_daysChildNodes;
let toNumbers_daysChildNodes;


let date = new Date();
const months = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"];

// ------------------ FUNCION PARA RENDERIZAR LOS DIAS EN EL CALENDARIO DE FECHA INCIAL ------------------
let fromDateCurrentYear = date.getFullYear();
let fromDateCurrentMonth = date.getMonth();
let renderFromCalendario = () =>{
    fromMonth_year.innerHTML = months[fromDateCurrentMonth] + " " + fromDateCurrentYear
    let firstDayOfMonth = new Date(fromDateCurrentYear,fromDateCurrentMonth,1).getDay();
    let lastDayofMonth = new Date(fromDateCurrentYear,fromDateCurrentMonth + 1,0).getDate();
    
    
    let liDay ="";

    for (let i = firstDayOfMonth; i >0; i--) {
        liDay += "<li>-</li>";
        
    }

    for (let i = 1; i <= lastDayofMonth; i++) {
        liDay += "<li>"+i+"</li>";
    }

    fromNumbers_days.innerHTML = liDay;

    fromNumbers_daysChildNodes = fromNumbers_days.childNodes;
}

// ------------------ FUNCION PARA RENDERIZAR LOS DIAS EN EL CALENDARIO DE FECHA FINAL ------------------
let toDateCurrentYear = date.getFullYear();
let toDateCurrentMonth = date.getMonth();
let renderToCalendario = () =>{
    toMonth_year.innerHTML = months[toDateCurrentMonth] + " " + toDateCurrentYear
    let firstDayOfMonth = new Date(toDateCurrentYear,toDateCurrentMonth,1).getDay();
    let lastDayofMonth = new Date(toDateCurrentYear,toDateCurrentMonth + 1,0).getDate();
    
    
    let liDay ="";

    for (let i = firstDayOfMonth; i >0; i--) {
        liDay += "<li>-</li>";
        
    }

    for (let i = 1; i <= lastDayofMonth; i++) {
        liDay += "<li>"+i+"</li>";
    }

    toNumbers_days.innerHTML = liDay;

    toNumbers_daysChildNodes = toNumbers_days.childNodes;
}

renderFromCalendario();
renderToCalendario();

fromNumbers_daysChildNodes.forEach(element => {
    element.addEventListener("click",()=>{
        fillDateFromCalendar(element);
    })
});
toNumbers_daysChildNodes.forEach(element => {
    element.addEventListener("click",()=>{
        fillDateToCalendar(element);
    })
});


// ------------------ BOTONES PARA CAMBIAR DE MES EN LOS CALENDARIOS ------------------

// ------------------ Para el calendario incial ------------------
fromDatePrevButton.addEventListener("click", ()=>{
    fromDateCurrentMonth--;
    if(fromDateCurrentMonth<0){
        date = new Date(fromDateCurrentYear,fromDateCurrentMonth);
        fromDateCurrentYear = date.getFullYear();
        fromDateCurrentMonth = date.getMonth();
    }
    renderFromCalendario();

    fromNumbers_daysChildNodes.forEach(element => {
        element.addEventListener("click",()=>{
            fillDateFromCalendar(element);
        })
    });
    
})

fromDateNextButton.addEventListener("click", ()=>{
    fromDateCurrentMonth++;
    if(fromDateCurrentMonth>11){
        date = new Date(fromDateCurrentYear,fromDateCurrentMonth);
        fromDateCurrentYear = date.getFullYear();
        fromDateCurrentMonth = date.getMonth();
    }
    renderFromCalendario();

    fromNumbers_daysChildNodes.forEach(element => {
        element.addEventListener("click",()=>{
            fillDateFromCalendar(element);
        })
    });

})


// ------------------ Para el calendario final ------------------
toDatePrevButton.addEventListener("click", ()=>{
    toDateCurrentMonth--;
    if(toDateCurrentMonth<0){
        date = new Date(toDateCurrentYear,toDateCurrentMonth);
        toDateCurrentYear = date.getFullYear();
        toDateCurrentMonth = date.getMonth();
    }
    renderToCalendario();

    toNumbers_daysChildNodes.forEach(element => {
        element.addEventListener("click",()=>{
            fillDateToCalendar(element);
        })
    });
    
})

toDateNextButton.addEventListener("click", ()=>{
    toDateCurrentMonth++;
    if(toDateCurrentMonth>11){
        date = new Date(toDateCurrentYear,toDateCurrentMonth);
        toDateCurrentYear = date.getFullYear();
        toDateCurrentMonth = date.getMonth();
    }
    renderToCalendario();

    toNumbers_daysChildNodes.forEach(element => {
        element.addEventListener("click",()=>{
            fillDateToCalendar(element);
        })
    });

})


// ------------------ FUNCIONES PARA RELLENAR EL TEXTO DE LA FECHA ------------------

let datePicked;
// ------------------ Para el calendario de Inicio ------------------
let fillDateFromCalendar = (element) =>{
    datePicked = element.innerHTML + "-" + (fromDateCurrentMonth+1)+"-"+(fromDateCurrentYear);
    LimpiarActiveFromCalendar();
    element.classList.add("active")
    fromDateContent.innerHTML = datePicked;
    firstDateInput.value = datePicked;
}

// ------------------ Para el calendario de Fin ------------------
let fillDateToCalendar = (element) =>{
    datePicked = element.innerHTML + "-" + (toDateCurrentMonth+1)+"-"+(toDateCurrentYear);
    LimpiarActiveToCalendar();
    element.classList.add("active")
    toDateContent.innerHTML = datePicked;
    endDateInput.value = datePicked;
}

// // LIMPIAR ACTIVES DE LOS LIs PARA MARCAR NUEVOS
function LimpiarActiveFromCalendar() {
    let numbers_daysLis = document.querySelectorAll(".fromDatenumbers > li");

    numbers_daysLis.forEach(element => {
        if (element.classList.contains("active")) {
            element.classList.remove("active")
        }
    });
}


function LimpiarActiveToCalendar() {
    let numbers_daysLis = document.querySelectorAll(".toDatenumbers > li");

    numbers_daysLis.forEach(element => {
        if (element.classList.contains("active")) {
            element.classList.remove("active")
        }
    });
}

calendarios.forEach(element => {
    element.addEventListener("click",()=>{
        element.nextElementSibling.classList.add("active")
    })
});






