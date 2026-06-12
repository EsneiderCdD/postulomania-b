from .selectors import OFFERS_CARD, STOP_TEXTS, NO_RESULTS_CONTAINER
from .popups import handle_popups

def _slugify(text):
    """Convierte texto a slug compatible con URLs de Computrabajo."""
    return str(text).lower().strip().replace(' ', '-')

async def execute_search(page, search_term, location, apply_filter=True, days=1):
    """Ejecuta la búsqueda de ofertas en Computrabajo usando URL directa con ubicación."""

    term_slug = _slugify(search_term)
    loc_slug = _slugify(location)
    target_url = f"https://co.computrabajo.com/trabajo-de-{term_slug}-en-{loc_slug}"

    if apply_filter:
        target_url += f"?pubdate={days}"

    await page.goto(target_url)

    try:
        await page.wait_for_selector(f"{OFFERS_CARD}, {NO_RESULTS_CONTAINER}", timeout=10000)

        if await page.locator(OFFERS_CARD).count() > 0:
            await handle_popups(page)
            return True

        for text in STOP_TEXTS:
            if await page.locator(f"text={text}").count() > 0:
                return False

        return False

    except Exception:
        return False
