let itemsSupervisores = document.querySelectorAll(".containerSupervisores > .information > .valuesWrapper > .values > .item > .backgroundItem")

function listenersItemsDisplay() {
    itemsSupervisores.forEach(element => {
        element.addEventListener("click", () => {
            let alturaUl = element.nextElementSibling.scrollHeight
            element.nextElementSibling.style.height = (element.nextElementSibling.style.height === alturaUl + 'px') ? '0px' : alturaUl + 'px';
            element.style.marginBottom = (element.nextElementSibling.style.height === alturaUl + 'px') ? alturaUl + 10 + 'px' : "0px";
        })
    });

}
listenersItemsDisplay()
