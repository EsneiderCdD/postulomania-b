from .selectors import POPUP

async def handle_popups(page):
    popup_locator = page.locator(POPUP["selector"])

    if not (await popup_locator.count() > 0 and await popup_locator.is_visible()):
        return

    for strategy in POPUP["close_strategies"]:
        try:
            selector = f"{POPUP['selector']} {strategy}"
            await page.locator(selector).first.click(timeout=3000)
            break
        except Exception:
            continue

    try:
        await page.wait_for_selector(
            POPUP["selector"],
            state="hidden",
            timeout=3000
        )
    except Exception:
        pass