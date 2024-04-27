let items = document.querySelectorAll(".wrapperShortInfo.wrapperItem")

items.forEach(element => {
    element.addEventListener("click", () => {
        let alturaUl = element.nextElementSibling.scrollHeight
        element.nextElementSibling.style.height = (element.nextElementSibling.style.height === alturaUl + 'px') ? '0px' : alturaUl + 'px';

        let vendedores = element.nextElementSibling.querySelectorAll(".containerTittleAndData > .itemsVendedores > li > .wrapperShortInfo")
        vendedores.forEach(v => {
            v.addEventListener("click", () => {
                let alturaDetail = v.nextElementSibling.scrollHeight
                if (v.nextElementSibling.style.height === alturaDetail + 'px') {
                    v.nextElementSibling.style.height = "0px"
                    element.nextElementSibling.style.height = element.nextElementSibling.scrollHeight - alturaDetail + "px"

                } else {
                    v.nextElementSibling.style.height = alturaDetail + 'px'
                    element.nextElementSibling.style.height = alturaUl + alturaDetail + "px"

                }
            })

        });
    })
});
