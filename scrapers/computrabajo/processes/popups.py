async def handle_popups(page):
    popup_selector = "#pop-up-webpush-sub"
    close_button_selector = f"{popup_selector} button[onclick*='webpush_subscribe_ko']"

    popup_locator = page.locator(popup_selector)

    if not (await popup_locator.count() > 0 and await popup_locator.is_visible()):
        return

    try:
        await page.locator(close_button_selector).first.click(timeout=3000)
    except:
        try:
            await page.click(
                f"{popup_selector} button:has-text('Ahora no')",
                timeout=2000
            )
        except:
            pass

    try:
        await page.wait_for_selector(
            popup_selector,
            state="hidden",
            timeout=3000
        )
    except:
        pass