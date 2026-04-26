import asyncio
import random

async def extract_data(page, keyword_slug="dds"):
    all_offers = await page.locator("article.box_offer").all()

    results = []

    async def get_safe_text(locator, selector, default="-"):
        try:
            element = locator.locator(selector).first

            if await element.count() == 0:
                return default

            text = await element.inner_text(timeout=2000)
            return text.strip()

        except:
            return default

    async def get_safe_link(locator, selector, default="-"):
        try:
            element = locator.locator(selector).first

            if await element.count() == 0:
                return default

            link = await element.get_attribute("href", timeout=2000)

            if not link:
                return default

            return "https://co.computrabajo.com" + link

        except:
            return default

    for i, offer in enumerate(all_offers):
        try:
            try:
                await offer.click()
                await page.wait_for_selector(
                    ".description_offer .fs16.t_word_wrap",
                    timeout=3000
                )
            except:
                pass

            data = {
                "id_oferta": await offer.get_attribute("data-id"),
                "titulo": await get_safe_text(offer, "a.js-o-link"),
                "enlace": await get_safe_link(offer, "a.js-o-link"),
                "empresa": await get_safe_text(offer, "p.dFlex a"),
                "valoracion": await get_safe_text(offer, "span.fwB"),
                "ubicacion": await get_safe_text(offer, "p.fs16.fc_base.mt5:not(.dFlex) span.mr10"),
                "salario": await get_safe_text(offer, "span:has-text('$')"),
                "modalidad": await get_safe_text(offer, ".i_home_office + span"),
                "tiempo": await get_safe_text(offer, "p.fs13.fc_aux.mt15"),
                "descripcion": await get_safe_text(page, ".description_offer .fs16.t_word_wrap")
            }

            results.append(data)

            await asyncio.sleep(random.uniform(0.1, 0.4))

        except:
            continue

    return results