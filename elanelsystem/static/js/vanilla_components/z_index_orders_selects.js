function ordersZindexSelects() {
    const wrappers = Array.from(document.querySelectorAll(".wrapperSelectCustom")).reverse();

    wrappers.forEach((wrapper, index) => {
        const pseudoInput = wrapper.querySelector(".pseudo-input-select-wrapper");
        const iconDesplegar = wrapper.querySelector(".iconDesplegar");
        const listSelect = wrapper.querySelector(".list-select-custom");

        if (pseudoInput) pseudoInput.style.zIndex = `${(index * 3) + 2}`;
        if (iconDesplegar) iconDesplegar.style.zIndex = `${(index * 3) + 3}`;
        if (listSelect) listSelect.style.zIndex = `${(index * 3) + 1}`;
    });

}