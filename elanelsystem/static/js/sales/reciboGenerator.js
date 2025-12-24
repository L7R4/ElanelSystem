/**
 * Función para generar recibo usando HTML2PDF
 * Permite estilos CSS completos y edición visual
 */

// Función para cargar el HTML2PDF library
function loadHtml2Pdf() {
  return new Promise((resolve, reject) => {
    if (window.html2pdf) {
      resolve(window.html2pdf);
      return;
    }

    const script = document.createElement("script");
    script.src =
      "https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js";
    script.onload = () => resolve(window.html2pdf);
    script.onerror = () => reject(new Error("No se pudo cargar html2pdf"));
    document.head.appendChild(script);
  });
}

// Función para obtener datos del recibo desde el formulario
// function obtenerDatosRecibo() {
//   const datos = {
//     // Información de la empresa
//     empresa: {
//       nombre: "ELANEL S.A.",
//       sub: "SOCIEDAD ANÓNIMA",
//       direccion: "Calle Principal 123",
//       ciuefono: "1234-5678",
//       cuidad: "Ciudad",
//       telt: "30-12345678-9",
//       inicio: "01/01/2020",
//       leyenda: "I.V.A. RESPONSABLE INSCRIPTO",
//       regimen: "REGIMEN GENERAL",
//     },

//     // Información del recibo
//     recibo: {
//       numero: "0001-00000001",
//       fecha: new Date(),
//     },

//     // Información del cliente
//     cliente: {
//       nombre: "Juan Pérez",
//       domicilio: "Calle Cliente 456",
//       localidad: "Localidad",
//       cuit: "20-98765432-1",
//       condicionIva: "CONSUMIDOR FINAL",
//       condicionVenta: "CONTADO",
//     },

//     // Importe
//     importe: {
//       importe: "$1,500.00",
//       interes: "$0.00",
//       total: "$1,500.00",
//     },

//     // Concepto
//     concepto: "Pago de cuota mensual - Servicio de consultoría",

//     // Pagos
//     pagos: {
//       efectivo: "$1,500.00",
//       cheques: [],
//     },
//   };

//   // Si hay datos en el formulario, usarlos
//   if (window.datosVenta) {
//     datos.cliente.nombre = window.datosVenta.cliente || datos.cliente.nombre;
//     datos.importe.total = window.datosVenta.total || datos.importe.total;
//     datos.concepto = window.datosVenta.concepto || datos.concepto;
//   }

//   return datos;
// }

// Función para llenar el template HTML con los datos
function llenarTemplate(datos) {
  const template = document.getElementById("recibo-template").innerHTML;

  // Reemplazar placeholders con datos reales
  let html = template
    .replace(/\{\{empresa\.nombre\}\}/g, datos.empresa.nombre)
    .replace(/\{\{empresa\.sub\}\}/g, datos.empresa.sub)
    .replace(/\{\{empresa\.direccion\}\}/g, datos.empresa.direccion)
    .replace(/\{\{empresa\.ciudad\}\}/g, datos.empresa.ciudad)
    .replace(/\{\{empresa\.telefono\}\}/g, datos.empresa.telefono)
    .replace(/\{\{empresa\.cuit\}\}/g, datos.empresa.cuit)
    .replace(/\{\{empresa\.inicio\}\}/g, datos.empresa.inicio)
    .replace(/\{\{empresa\.leyenda\}\}/g, datos.empresa.leyenda)
    .replace(/\{\{empresa\.regimen\}\}/g, datos.empresa.regimen)
    .replace(/\{\{recibo\.numero\}\}/g, datos.recibo.numero)
    .replace(/\{\{fecha\.dia\}\}/g, datos.recibo.fecha.getDate())
    .replace(/\{\{fecha\.mes\}\}/g, datos.recibo.fecha.getMonth() + 1)
    .replace(/\{\{fecha\.anio\}\}/g, datos.recibo.fecha.getFullYear())
    .replace(/\{\{cliente\.nombre\}\}/g, datos.cliente.nombre)
    .replace(/\{\{cliente\.domicilio\}\}/g, datos.cliente.domicilio)
    .replace(/\{\{cliente\.localidad\}\}/g, datos.cliente.localidad)
    .replace(/\{\{cliente\.cuit\}\}/g, datos.cliente.cuit)
    .replace(/\{\{importe\.importe\}\}/g, datos.importe.importe)
    .replace(/\{\{importe\.interes\}\}/g, datos.importe.interes)
    .replace(/\{\{importe\.total\}\}/g, datos.importe.total)
    .replace(/\{\{concepto\}\}/g, datos.concepto)
    .replace(/\{\{pagos\.efectivo\}\}/g, datos.pagos.efectivo);

  return html;
}

// Función para crear el recibo HTML
function crearReciboHTML(datos) {
  const fecha = datos.recibo.fecha;
  const dia = fecha.getDate();
  const mes = fecha.getMonth() + 1;
  const anio = fecha.getFullYear();

  return `
    <div class="recibo-container">
        <div class="recibo-header">
            <div class="empresa-info">
                <div class="empresa-nombre">${datos.empresa.nombre}</div>
                <div class="empresa-sub">${datos.empresa.sub}</div>
                <div class="empresa-direccion">${datos.empresa.direccion}</div>
                <div class="empresa-ciudad">${datos.empresa.ciudad}</div>
                <div class="empresa-telefono">${datos.empresa.telefono}</div>
                <div class="empresa-cuit">C.U.I.T.: ${datos.empresa.cuit}</div>
                <div class="empresa-inicio">Inicio Act.: ${
                  datos.empresa.inicio
                }</div>
                <div class="empresa-leyenda">${datos.empresa.leyenda}</div>
                <div class="empresa-regimen">${datos.empresa.regimen}</div>
            </div>
            <div class="recibo-info">
                <div class="recibo-x">X</div>
                <div class="recibo-titulo">RECIBO</div>
                <div class="recibo-numero">N° ${datos.recibo.numero}</div>
                <div class="fecha-container">
                    <div class="fecha-item">
                        <span class="fecha-label">DÍA</span>
                        <span class="fecha-valor">${dia}</span>
                    </div>
                    <div class="fecha-item">
                        <span class="fecha-label">MES</span>
                        <span class="fecha-valor">${mes}</span>
                    </div>
                    <div class="fecha-item">
                        <span class="fecha-label">AÑO</span>
                        <span class="fecha-valor">${anio}</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="cliente-section">
            <div class="cliente-info">
                <div class="info-row">
                    <span class="info-label">Recibí de:</span>
                    <span class="info-value">${datos.cliente.nombre}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Domicilio:</span>
                    <span class="info-value">${datos.cliente.domicilio}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Localidad:</span>
                    <span class="info-value">${datos.cliente.localidad}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">C.U.I.T.:</span>
                    <span class="info-value">${datos.cliente.cuit}</span>
                </div>
            </div>
            
            <div class="condiciones-section">
                <div class="condicion-iva">
                    <span class="condicion-label">Condición frente al I.V.A.:</span>
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" ${
                              datos.cliente.condicionIva === "CONSUMIDOR FINAL"
                                ? "checked"
                                : ""
                            }>
                            <label>Consumidor Final</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" ${
                              datos.cliente.condicionIva ===
                              "RESPONSABLE INSCRIPTO"
                                ? "checked"
                                : ""
                            }>
                            <label>Responsable Inscripto</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" ${
                              datos.cliente.condicionIva === "EXENTO"
                                ? "checked"
                                : ""
                            }>
                            <label>Exento</label>
                        </div>
                    </div>
                </div>
                
                <div class="condicion-venta">
                    <span class="condicion-label">Condición de venta:</span>
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" ${
                              datos.cliente.condicionVenta === "CONTADO"
                                ? "checked"
                                : ""
                            }>
                            <label>Contado</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" ${
                              datos.cliente.condicionVenta ===
                              "CUENTA CORRIENTE"
                                ? "checked"
                                : ""
                            }>
                            <label>Cuenta Corriente</label>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="importe-section">
            <div class="importe-row">
                <span class="importe-label">La suma de pesos:</span>
                <span class="importe-value">${datos.importe.importe}</span>
            </div>
            <div class="importe-row">
                <span class="importe-label">Interés:</span>
                <span class="importe-value">${datos.importe.interes}</span>
            </div>
        </div>

        <div class="concepto-section">
            <div class="concepto-header">
                <span class="concepto-label">En concepto de:</span>
            </div>
            <div class="concepto-content">${datos.concepto}</div>
        </div>

        <div class="pagos-section">
            <div class="pago-efectivo">
                <span class="pago-label">Efectivo</span>
                <span class="pago-line"></span>
                <span class="pago-moneda">$</span>
                <span class="pago-valor">${datos.pagos.efectivo}</span>
            </div>
            
            <div class="pago-cheque">
                <span class="pago-valor-cheque">Cheque N°:</span>
                <span class="pago-valor-banco">Banco:</span>
                <span class="pago-moneda">$</span>
                <span class="pago-valor"></span>
            </div>
        </div>

        <div class="footer-section">
            <div class="total-section">
                <div class="total-box">
                    <span class="total-label">TOTAL $</span>
                    <span class="total-valor">${datos.importe.total}</span>
                </div>
            </div>
            
            <div class="firma-section">
                <span class="firma-label">Firma:</span>
                <span class="firma-linea"></span>
            </div>
        </div>

        <div class="pie-section">
            <div class="pie-text">
                Este recibo es un documento válido. Conserve su copia.
            </div>
        </div>
    </div>
    `;
}

// Función principal para generar el recibo con HTML2PDF
async function generarReciboHTML2PDF(datosRecibo = null) {
  try {
    // Cargar la librería HTML2PDF
    await loadHtml2Pdf();

    // Obtener datos
    const datos = datosRecibo;

    // Crear el HTML del recibo
    const reciboHTML = crearReciboHTML(datos);

    // Crear un contenedor temporal para el recibo
    const tempContainer = document.createElement("div");
    tempContainer.innerHTML = reciboHTML;
    tempContainer.style.position = "absolute";
    tempContainer.style.left = "-9999px";
    tempContainer.style.top = "0";
    document.body.appendChild(tempContainer);

    // Obtener los estilos CSS actuales
    const styles = Array.from(document.styleSheets)
      .map((sheet) => {
        try {
          return Array.from(sheet.cssRules)
            .map((rule) => rule.cssText)
            .join("\n");
        } catch (e) {
          return "";
        }
      })
      .join("\n");

    // Crear un elemento style con los estilos
    const styleElement = document.createElement("style");
    styleElement.textContent = styles;
    tempContainer.appendChild(styleElement);

    // Configurar opciones para HTML2PDF
    const opt = {
      margin: 0,
      filename: `recibo_${datos.recibo.numero}.pdf`,
      image: { type: "jpeg", quality: 0.98 },
      html2canvas: {
        scale: 2,
        useCORS: true,
        letterRendering: true,
      },
      jsPDF: {
        unit: "mm",
        format: "a4",
        orientation: "portrait",
      },
    };

    // Generar el PDF
    await window.html2pdf().set(opt).from(tempContainer).save();

    // Limpiar el contenedor temporal
    document.body.removeChild(tempContainer);

    console.log("Recibo generado exitosamente con HTML2PDF");
  } catch (error) {
    console.error("Error al generar el recibo:", error);
    alert("Error al generar el recibo: " + error.message);
  }
}

// Función para abrir el editor de estilos
function abrirEditorEstilos() {
  const editor = document.getElementById("styleEditor");
  const customCSSTextarea = document.getElementById("customCSS");

  // Obtener los estilos actuales
  const estilosActuales = Array.from(document.styleSheets)
    .map((sheet) => {
      try {
        return Array.from(sheet.cssRules)
          .filter(
            (rule) => rule.selectorText && rule.selectorText.includes(".recibo")
          )
          .map((rule) => rule.cssText)
          .join("\n");
      } catch (e) {
        return "";
      }
    })
    .join("\n");

  customCSSTextarea.value = estilosActuales;
  editor.style.display = "block";
}

// Función para aplicar estilos personalizados
function aplicarEstilosPersonalizados() {
  const customCSS = document.getElementById("customCSS").value;
  let styleElement = document.getElementById("customStyles");

  if (!styleElement) {
    styleElement = document.createElement("style");
    styleElement.id = "customStyles";
    document.head.appendChild(styleElement);
  }

  styleElement.textContent = customCSS;
  cerrarEditorEstilos();
}

// Función para cerrar el editor de estilos
function cerrarEditorEstilos() {
  document.getElementById("styleEditor").style.display = "none";
}

// Función para abrir el editor de estilos
function abrirEditorEstilos() {
  document.getElementById("styleEditor").style.display = "block";
}

// Función para aplicar estilos personalizados
function aplicarEstilosPersonalizados() {
  const cssPersonalizado = document.getElementById("customCSS").value;
  let styleElement = document.getElementById("estilos-personalizados");

  if (!styleElement) {
    styleElement = document.createElement("style");
    styleElement.id = "estilos-personalizados";
    document.head.appendChild(styleElement);
  }

  styleElement.textContent = cssPersonalizado;
}

// Función para guardar estilos en localStorage
function guardarEstilos() {
  const cssPersonalizado = document.getElementById("customCSS").value;
  localStorage.setItem("estilosReciboPersonalizados", cssPersonalizado);
  alert("Estilos guardados correctamente");
}

// Función para cargar estilos desde localStorage
function cargarEstilos() {
  const cssGuardado = localStorage.getItem("estilosReciboPersonalizados");
  if (cssGuardado) {
    document.getElementById("customCSS").value = cssGuardado;
    aplicarEstilosPersonalizados();
    alert("Estilos cargados correctamente");
  } else {
    alert("No hay estilos guardados");
  }
}

// Función para generar PDF usando html2pdf
function generarPDF() {
  const element = document.getElementById("reciboContainer");

  const opt = {
    margin: 10,
    filename: "recibo.pdf",
    image: { type: "jpeg", quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: "mm", format: "a4", orientation: "portrait" },
  };

  // Verificar si html2pdf está disponible
  if (typeof html2pdf !== "undefined") {
    html2pdf().set(opt).from(element).save();
  } else {
    alert("La librería html2pdf no está disponible. Por favor, instálala.");
  }
}

// Función para imprimir
function imprimirRecibo() {
  window.print();
}

// Función para inicializar los eventos del generador
function inicializarReciboGenerator() {
  // Botones de control
  const btnEditarEstilos = document.getElementById("btnEditarEstilos");
  const btnGenerarPDF = document.getElementById("btnGenerarPDF");
  const btnImprimir = document.getElementById("btnImprimir");
  const btnCerrar = document.getElementById("btnCerrar");

  // Botones del editor
  const btnAplicarEstilos = document.getElementById("btnAplicarEstilos");
  const btnGuardarEstilos = document.getElementById("btnGuardarEstilos");
  const btnCargarEstilos = document.getElementById("btnCargarEstilos");
  const btnCerrarEditor = document.getElementById("btnCerrarEditor");

  // Event listeners
  if (btnEditarEstilos)
    btnEditarEstilos.addEventListener("click", abrirEditorEstilos);
  if (btnGenerarPDF) btnGenerarPDF.addEventListener("click", generarPDF);
  if (btnImprimir) btnImprimir.addEventListener("click", imprimirRecibo);
  if (btnCerrar) btnCerrar.addEventListener("click", () => window.close());

  if (btnAplicarEstilos)
    btnAplicarEstilos.addEventListener("click", aplicarEstilosPersonalizados);
  if (btnGuardarEstilos)
    btnGuardarEstilos.addEventListener("click", guardarEstilos);
  if (btnCargarEstilos)
    btnCargarEstilos.addEventListener("click", cargarEstilos);
  if (btnCerrarEditor)
    btnCerrarEditor.addEventListener("click", cerrarEditorEstilos);

  // Aplicar estilos guardados automáticamente
  cargarEstilos();
}

// Función para abrir la vista previa del recibo
function abrirVistaPreviaRecibo(pid) {
  // Guardar datos de la venta para usarlos en el recibo
  if (!pid) {
    return;
  }

  // Abrir la ventana de vista previa
  const ventana = window.open(
    `/ventas/detalle_venta/recibo-preview/${pid}/`,
    "_blank",
    "width=1000,height=800,scrollbars=yes"
  );

  // Si la ventana no se puede abrir (bloqueador de popups)
  if (!ventana || ventana.closed || typeof ventana.closed == "undefined") {
    alert(
      "Por favor, permite ventanas emergentes para ver la vista previa del recibo."
    );
  }
}

// Función para cerrar la vista previa
function cerrarVistaPrevia() {
  window.close();
}

// Función para generar PDF desde la vista previa
async function generarPDFDesdeVistaPrevia() {
  try {
    const reciboContainer = document.querySelector(".recibo-container");
    if (!reciboContainer) {
      alert("No se encontró el contenedor del recibo");
      return;
    }

    await loadHtml2Pdf();

    const opt = {
      margin: 0,
      filename: `recibo_${new Date().getTime()}.pdf`,
      image: { type: "jpeg", quality: 0.98 },
      html2canvas: {
        scale: 2,
        useCORS: true,
        letterRendering: true,
      },
      jsPDF: {
        unit: "mm",
        format: "a4",
        orientation: "portrait",
      },
    };

    await window.html2pdf().set(opt).from(reciboContainer).save();
  } catch (error) {
    console.error("Error al generar PDF:", error);
    alert("Error al generar el PDF: " + error.message);
  }
}

// Función para imprimir el recibo
function imprimirRecibo() {
  window.print();
}

// Función para guardar configuración de estilos
function guardarConfiguracionEstilos() {
  const customCSS = document.getElementById("customCSS").value;
  localStorage.setItem("reciboCustomCSS", customCSS);
  alert("Configuración de estilos guardada exitosamente!");
}

// Función para cargar configuración de estilos
function cargarConfiguracionEstilos() {
  const customCSS = localStorage.getItem("reciboCustomCSS");
  if (customCSS) {
    document.getElementById("customCSS").value = customCSS;
    aplicarEstilosPersonalizados();
  }
}

// Inicializar cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", function () {
  // Cargar configuración guardada
  cargarConfiguracionEstilos();

  // Agregar event listeners a los botones
  const btnEditarEstilos = document.getElementById("btnEditarEstilos");
  const btnGenerarPDF = document.getElementById("btnGenerarPDF");
  const btnCerrar = document.getElementById("btnCerrar");
  const btnAplicarEstilos = document.getElementById("btnAplicarEstilos");
  const btnResetEstilos = document.getElementById("btnResetEstilos");
  const btnCerrarEditor = document.getElementById("btnCerrarEditor");
  const btnGuardarEstilos = document.getElementById("btnGuardarEstilos");

  if (btnEditarEstilos) {
    btnEditarEstilos.addEventListener("click", abrirEditorEstilos);
  }

  if (btnGenerarPDF) {
    btnGenerarPDF.addEventListener("click", generarPDFDesdeVistaPrevia);
  }

  if (btnCerrar) {
    btnCerrar.addEventListener("click", cerrarVistaPrevia);
  }

  if (btnAplicarEstilos) {
    btnAplicarEstilos.addEventListener("click", aplicarEstilosPersonalizados);
  }

  if (btnResetEstilos) {
    btnResetEstilos.addEventListener("click", function () {
      document.getElementById("customCSS").value = "";
      aplicarEstilosPersonalizados();
    });
  }

  if (btnCerrarEditor) {
    btnCerrarEditor.addEventListener("click", cerrarEditorEstilos);
  }

  if (btnGuardarEstilos) {
    btnGuardarEstilos.addEventListener("click", guardarConfiguracionEstilos);
  }
});
