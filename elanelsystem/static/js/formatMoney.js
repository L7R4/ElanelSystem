/**
 * Formatea un número como moneda según locale y currency.
 *
 * @param {number} amount — La cantidad a formatear.
 * @param {string} [locale="es-AR"] — Código de la región (e.g. "en-US", "es-AR").
 * @param {string} [currency="ARS"] — Código de la moneda ISO (e.g. "USD", "ARS", "EUR").
 * @returns {string} — El string formateado.
 */

function formatMoney(amount, locale = "es-AR", currency = "ARS") {
    const options = {
        style: "currency",
        currency
    };
    options.minimumFractionDigits = 0;
    options.maximumFractionDigits = 0;

    return new Intl.NumberFormat(locale, options).format(amount);
}
