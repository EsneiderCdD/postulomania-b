import asyncio
from .processes.search import execute_search
from .processes.extraction import extract_data
from modules.browser import init_browser


async def run_computrabajo(
    search_term,
    keyword_slug,
    location,
    apply_filter=True,
    headless=False,
    days=1
):
    playwright, browser, page = await init_browser(headless=headless)
  
    results = []

    try:
        has_offers = await execute_search(
            page,
            search_term,
            apply_filter=apply_filter,
            location=location,
            days=days
        )

        if has_offers:
            results = await extract_data(page, keyword_slug=keyword_slug)

    finally:
        await browser.close()
        await playwright.stop()
        
    return results