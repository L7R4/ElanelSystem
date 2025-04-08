function listenersItemsDisplay() {
    let itemsSupervisores = document.querySelectorAll(".containerSupervisores .backgroundItem");
    itemsSupervisores.forEach(element => {
      element.addEventListener("click", () => {
        // 1) Rotar la flechita
        let imageMore = element.querySelector(".imageMore");
        imageMore.classList.toggle("active");
  
        // 2) Mostrar/ocultar la .detallesItem
        let detallesItem = element.nextElementSibling; 
        detallesItem.classList.toggle("open");
      });
    });
  }
  listenersItemsDisplay();
