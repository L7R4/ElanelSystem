function parseQueryString(queryString) {
    // Eliminar el '?' al principio del query string si está presente
    queryString = queryString.replace(/^\?/, '');

    // Dividir el query string en pares clave=valor
    const pairs = queryString.split('&');

    // Crear un objeto para almacenar los parámetros
    const params = {};

    // Iterar sobre cada par clave=valor y agregarlo al objeto params
    pairs.forEach(pair => {
        const [key, value] = pair.split('=');
        params[key] = decodeURIComponent(value || '');
    });

    return params;
}