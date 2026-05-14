import unicodedata
from .popups import handle_popups

def _slugify(text):
    """Convierte texto a slug compatible con URLs de Computrabajo."""
    normalized = unicodedata.normalize('NFKD', str(text))
    ascii_text = normalized.encode('ascii', 'ignore').decode()
    cleaned = ascii_text.lower().strip()
    cleaned = cleaned.replace(',', ' ').replace('.', ' ')
    cleaned = '-'.join(cleaned.split())
    return cleaned

async def execute_search(page, url, search_term, apply_filter=False, location=None):
    """Ejecuta la búsqueda de ofertas y gestiona filtros iniciales.
    
    Si se proporciona `location`, construye la URL con filtro de lugar:
        /trabajo-de-{search_term}-en-{location}
    y navega directamente, sin pasar por el formulario de búsqueda."""
    
    if location:
        term_slug = _slugify(search_term)
        loc_slug = _slugify(location)
        target_url = f"https://co.computrabajo.com/trabajo-de-{term_slug}-en-{loc_slug}"
        
        if apply_filter:
            target_url += "?pubdate=1"
        
        await page.goto(target_url)
    else:
        await page.goto(url)
        
        try:
            search_selector = "input[placeholder*='Cargo']"
            await page.wait_for_selector(search_selector, timeout=5000)
            await page.fill(search_selector, search_term)
            await page.press(search_selector, "Enter")
        except:
            return False

        if apply_filter:
            current_url = page.url
            separator = "&" if "?" in current_url else "?"
            await page.goto(current_url + f"{separator}pubdate=1")

    try:
        await page.wait_for_selector("article.box_offer, .bg-white.p30.tc", timeout=10000)
        
        if await page.locator("article.box_offer").count() > 0:
            await handle_popups(page)
            return True
        return False
            
    except:
        return False