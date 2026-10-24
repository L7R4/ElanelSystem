function ordersZindexSelects() {
    const wrappers = Array.from(document.querySelectorAll(".wrapperSelectCustom")).reverse();

    wrappers.forEach((wrapper, index) => {
        const pseudoInput = wrapper.querySelector(".pseudo-input-select-wrapper");
        const iconDesplegar = wrapper.querySelector(".iconDesplegar");

        // El z-index de la lista desplegada (.list-select-custom) lo define el
        // CSS de cada página con un valor alto y fijo (para que siempre quede
        // por encima del resto del formulario); acá solo ordenamos el trigger
        // y el ícono entre selects cerrados, sin pisar ese valor.
        if (pseudoInput) pseudoInput.style.zIndex = `${(index * 3) + 2}`;
        if (iconDesplegar) iconDesplegar.style.zIndex = `${(index * 3) + 3}`;
    });

}