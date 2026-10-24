(function () {
    const STORAGE_KEY = "documentos_vista";
    const wrapper = document.getElementById("documentosVista");
    const switchWrapper = document.getElementById("documentosVistaSwitch");
    if (!wrapper || !switchWrapper) return;

    const botones = switchWrapper.querySelectorAll(".vista-btn");

    function aplicarVista(vista) {
        wrapper.dataset.vista = vista;
        botones.forEach((btn) => btn.classList.toggle("active", btn.dataset.vista === vista));
        try { localStorage.setItem(STORAGE_KEY, vista); } catch (_) {}
    }

    botones.forEach((btn) => {
        btn.addEventListener("click", () => aplicarVista(btn.dataset.vista));
    });

    let vistaGuardada = null;
    try { vistaGuardada = localStorage.getItem(STORAGE_KEY); } catch (_) {}
    aplicarVista(vistaGuardada || wrapper.dataset.vista);

    // #region Modal de previsualizacion
    const modal = document.getElementById("documentoPreviewModal");
    const modalBody = document.getElementById("documentoPreviewBody");
    const modalClose = document.getElementById("documentoPreviewClose");

    function abrirPreview(url, tipo) {
        if (!url) return;
        modalBody.innerHTML = "";
        if (tipo === "imagen") {
            const img = document.createElement("img");
            img.src = url;
            modalBody.appendChild(img);
        } else if (tipo === "pdf") {
            const iframe = document.createElement("iframe");
            iframe.src = url;
            modalBody.appendChild(iframe);
        } else {
            return;
        }
        modal.classList.add("open");
    }

    function cerrarPreview() {
        modal.classList.remove("open");
        modalBody.innerHTML = "";
    }

    function manejarClickItem(el) {
        el.addEventListener("click", (event) => {
            if (event.target.closest(".documentos-acciones")) return;
            if (el.dataset.previsualizable === "1") {
                abrirPreview(el.dataset.url, el.dataset.tipo);
            } else {
                window.open(el.dataset.url, "_blank", "noopener");
            }
        });
    }

    document.querySelectorAll(".doc-card").forEach(manejarClickItem);
    document.querySelectorAll(".documento-fila").forEach(manejarClickItem);

    modalClose.addEventListener("click", cerrarPreview);
    modal.querySelector(".documento-preview-backdrop").addEventListener("click", cerrarPreview);
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") cerrarPreview();
    });
    // #endregion

    // #region Miniaturas reales de PDF (primera pagina), tipo Google Drive
    if (typeof pdfjsLib !== "undefined") {
        pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

        document.querySelectorAll("[data-pdf-url]").forEach((contenedor) => {
            const url = contenedor.dataset.pdfUrl;
            pdfjsLib.getDocument(url).promise
                .then((pdf) => pdf.getPage(1))
                .then((page) => {
                    const anchoObjetivo = 320;
                    const viewportBase = page.getViewport({ scale: 1 });
                    const escala = anchoObjetivo / viewportBase.width;
                    const viewport = page.getViewport({ scale: escala });

                    const canvas = document.createElement("canvas");
                    canvas.width = viewport.width;
                    canvas.height = viewport.height;
                    const contexto = canvas.getContext("2d");

                    return page.render({ canvasContext: contexto, viewport: viewport }).promise.then(() => canvas);
                })
                .then((canvas) => {
                    contenedor.innerHTML = "";
                    contenedor.appendChild(canvas);
                })
                .catch(() => {
                    // Si falla, se deja el icono de PDF que ya estaba renderizado.
                });
        });
    }
    // #endregion
})();
