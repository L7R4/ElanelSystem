const inputCampania = document.getElementById("inputCampania");
inputCampania.addEventListener('input', async () => {
    let data = await requestVentas(sucursalInput.value, inputCampania.value)
    const texto = inputSearchOperation.value;
    const resultados = buscar(texto, data["ventas"]);
    // realodAmountAuditorias(data["resumenAuditorias"])
    actualizarResultados(resultados, containerData);
    showDetailsVentas();
})


const inputSucursal = document.getElementById("sucursalInput");
inputSucursal.addEventListener('input', async () => {
    let data = await requestVentas(sucursalInput.value, inputCampania.value)
    const texto = inputSearchOperation.value;
    const resultados = buscar(texto, data["ventas"]);
    // realodAmountAuditorias(data["resumenAuditorias"])
    actualizarResultados(resultados, containerData);
    showDetailsVentas();
})
