import asyncio
import httpx

DOLARAPI_BLUE = "https://dolarapi.com/v1/dolares/blue"
DOLARAPI_OFICIAL = "https://dolarapi.com/v1/dolares/oficial"


async def _fetch_json(client: httpx.AsyncClient, url: str) -> dict:
    r = await client.get(url)
    r.raise_for_status()
    return r.json()


async def get_dolar_blue_y_oficial_async() -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        blue, oficial = await asyncio.gather(
            _fetch_json(client, DOLARAPI_BLUE),
            _fetch_json(client, DOLARAPI_OFICIAL),
        )

    return {
        "blue": {
            "compra": blue["compra"],
            "venta": blue["venta"],
            "fecha": blue.get("fechaActualizacion"),
        },
        "oficial": {
            "compra": oficial["compra"],
            "venta": oficial["venta"],
            "fecha": oficial.get("fechaActualizacion"),
        },
        "fuente": "dolarapi.com",
    }