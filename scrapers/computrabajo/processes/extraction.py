import asyncio
import random

async def extract_data(page, keyword_slug="dds"):
    all_offers = await page.locator("article.box_offer").all()

    end_texts = [
        "Ya viste todas las ofertas",
        "No hay más ofertas",
        "Estas opciones también podrían interesarte",
        "Mira estas oportunidades",
    ]

    end_exists = False
    for text in end_texts:
        if await page.locator(f"text={text}").count() > 0:
            end_exists = True
            break

    if end_exists and all_offers:
        cutoff = await page.evaluate('''() => {
            const offers = [...document.querySelectorAll("article.box_offer")];
            const markers = [
                "Ya viste todas las ofertas",
                "No hay más ofertas",
                "Estas opciones también podrían interesarte",
                "Mira estas oportunidades"
            ];

            let firstEnd = null;
            for (const text of markers) {
                const xpath = "//*[contains(text(), '" + text + "')]";
                const el = document.evaluate(
                    xpath, document, null,
                    XPathResult.FIRST_ORDERED_NODE_TYPE, null
                ).singleNodeValue;
                if (!el) continue;
                if (!firstEnd || (el.compareDocumentPosition(firstEnd) & Node.DOCUMENT_POSITION_FOLLOWING)) {
                    firstEnd = el;
                }
            }

            if (!firstEnd) return offers.length;
            for (let i = 0; i < offers.length; i++) {
                const pos = firstEnd.compareDocumentPosition(offers[i]);
                if (pos & Node.DOCUMENT_POSITION_FOLLOWING) return i;
            }
            return offers.length;
        }''')
        all_offers = all_offers[:cutoff]

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