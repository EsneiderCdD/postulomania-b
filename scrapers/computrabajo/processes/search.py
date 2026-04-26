from .popups import handle_popups

async def execute_search(page, url, search_term, apply_filter=False):
    """Ejecuta la búsqueda de ofertas y gestiona filtros iniciales."""
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