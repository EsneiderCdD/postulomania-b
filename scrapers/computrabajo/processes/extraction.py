import asyncio
import random
from .selectors import OFFERS_CARD, STOP_TEXTS, BASE_URL, TITLE_LINK, COMPANY_LINK, RATING, LOCATION, MODALITY, PUBLISHED_TIME, DESCRIPTION

async def extract_data(page):
    all_offers = await page.locator(OFFERS_CARD).all()

    end_exists = False
    for text in STOP_TEXTS:
        if await page.locator(f"text={text}").count() > 0:
            end_exists = True
            break

    if end_exists and all_offers:
        cutoff = await page.evaluate('''
            (args) => {
                const offers = [...document.querySelectorAll(args.offers_selector)];

                let cut_marker = null;
                for (const text of args.marker_texts) {
                    const xpath_query = "//*[contains(text(), '" + text + "')]";
                    const element = document.evaluate(
                        xpath_query, document, null,
                        XPathResult.FIRST_ORDERED_NODE_TYPE, null
                    ).singleNodeValue;
                    if (!element) continue;
                    if (!cut_marker || (element.compareDocumentPosition(cut_marker) & Node.DOCUMENT_POSITION_FOLLOWING)) {
                        cut_marker = element;
                    }
                }

                if (!cut_marker) return offers.length;
                for (let i = 0; i < offers.length; i++) {
                    const pos = cut_marker.compareDocumentPosition(offers[i]);
                    if (pos & Node.DOCUMENT_POSITION_FOLLOWING) return i;
                }
                return offers.length;
            }
        ''', {"offers_selector": OFFERS_CARD, "marker_texts": STOP_TEXTS})
        all_offers = all_offers[:cutoff]

    results = []

    async def get_safe_text(locator, selector, default="-"):
        try:
            element = locator.locator(selector).first

            if await element.count() == 0:
                return default

            text = await element.inner_text(timeout=2000)
            return text.strip()

        except Exception:
            return default

    async def get_safe_link(locator, selector, default="-"):
        try:
            element = locator.locator(selector).first

            if await element.count() == 0:
                return default

            link = await element.get_attribute("href", timeout=2000)

            if not link:
                return default

            return BASE_URL + link

        except Exception:
            return default

    for offer in all_offers:
        try:
            try:
                await offer.click()
                await page.wait_for_selector(
                    DESCRIPTION,
                    timeout=3000
                )
            except Exception:
                pass

            data = {
                "id_oferta": await offer.get_attribute("data-id"),
                "titulo": await get_safe_text(offer, TITLE_LINK),
                "enlace": await get_safe_link(offer, TITLE_LINK),
                "empresa": await get_safe_text(offer, COMPANY_LINK),
                "valoracion": await get_safe_text(offer, RATING),
                "ubicacion": await get_safe_text(offer, LOCATION),
                "modalidad": await get_safe_text(offer, MODALITY),
                "tiempo": await get_safe_text(offer, PUBLISHED_TIME),
                "descripcion": await get_safe_text(page, DESCRIPTION)
            }

            results.append(data)
            print(f"[EXTRACT] id={data.get('id_oferta')} | titulo={data.get('titulo')}")

            await asyncio.sleep(random.uniform(0.1, 0.4))

        except Exception:
            continue

    return results