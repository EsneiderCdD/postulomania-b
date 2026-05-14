import asyncio
from .processes.search import execute_search
from .processes.extraction import extract_data
from modules.browser import init_browser


async def run_computrabajo(
    search_term="Desarrollador de Software",
    keyword_slug="dds",
    apply_filter=True,
    location=None
):
    """Ejecuta el scraper y retorna la lista de ofertas encontradas.
    
    Parámetros:
        location: str opcional. Departamento/ciudad para filtrar (ej: 'Antioquia').
                  Si se proporciona, la búsqueda se restringe a ese lugar.
    """
    playwright, browser, page = await init_browser(headless=False)
    url = "https://co.computrabajo.com/"
    results = []

    try:
        has_offers = await execute_search(
            page,
            url,
            search_term,
            apply_filter=apply_filter,
            location=location
        )

        if has_offers:
            results = await extract_data(page, keyword_slug=keyword_slug)

    finally:
        await browser.close()
        await playwright.stop()
        
    return results


if __name__ == "__main__":
    asyncio.run(run_computrabajo())