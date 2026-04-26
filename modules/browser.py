import asyncio
from playwright.async_api import async_playwright

async def init_browser(headless=False, slow_mo=500):
    """
    Inicializa Playwright y lanza una instancia de Chromium.
    Retorna el navegador, el contexto y la página.
    """
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless, slow_mo=slow_mo)
    context = await browser.new_context()
    page = await context.new_page()
    
    return playwright, browser, page
