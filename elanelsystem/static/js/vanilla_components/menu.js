let path_name = window.location.pathname;
const list_menu = document.querySelectorAll(".list > li > a");
const button_menu = document.querySelector(".toggle-button");
const menu = document.getElementById("menu");

function setActiveMenu(id) {
  ClearClass();
  const el = document.getElementById(id);
  if (el && el.parentElement) {
    el.parentElement.classList.add("in_path");
  }
}

if (path_name.includes("resumen")) {
  setActiveMenu("resumen");
} else if (path_name.includes("cliente") || path_name.includes("detalle_venta")) {
  setActiveMenu("clientes");
} else if (path_name.includes("administracion")) {
  setActiveMenu("configuracion");
} else if (path_name.includes("caja")) {
  setActiveMenu("caja");
} else if (path_name.includes("usuario")) {
  setActiveMenu("usuarios");
} else if (path_name.includes("liquidaciones")) {
  setActiveMenu("liquidaciones");
} else if (path_name.includes("graficos")) {
  setActiveMenu("graficos");
} else if (path_name.includes("planes")) {
  setActiveMenu("planes");
} else if (path_name.includes("postventas")) {
  setActiveMenu("auditorias");
}

if (button_menu) {
  button_menu.addEventListener("click", () => {
    menu.classList.toggle("active");
    if (!menu.classList.contains("active")) {
      list_menu.forEach((element) => {
        element.children[1].style.display = "none";
      });
    } else if (menu.classList.contains("active")) {
      list_menu.forEach((element) => {
        element.children[1].style.display = "block";
      });
    }
  });
}

function ClearClass() {
  list_menu.forEach((element) => {
    element.classList.remove("in_path");
  });
}