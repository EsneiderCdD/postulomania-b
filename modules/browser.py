import asyncio
from playwright.async_api import async_playwright

async def init_browser(headless=False, slow_mo=500):
    """
    Inicializa Playwright y lanza una instancia de Chromium.
    Retorna el navegador, el contexto y la página.
    """
    playwright = await async_playwright().start()

    launch_args = []
    context_kwargs = {}

    if headless:
        launch_args.append("--disable-blink-features=AutomationControlled")
        context_kwargs["user_agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )
        context_kwargs["viewport"] = {"width": 1920, "height": 1080}

    browser = await playwright.chromium.launch(
        headless=headless, slow_mo=slow_mo, args=launch_args
    )
    context = await browser.new_context(**context_kwargs)
    page = await context.new_page()

    return playwright, browser, page
