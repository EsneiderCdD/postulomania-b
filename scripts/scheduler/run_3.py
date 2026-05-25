import asyncio
import logging
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from analytics.master_sync import sync_to_master
from analytics.pipeline import run_pipeline
from scrapers.computrabajo.main import run_computrabajo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)

logger = logging.getLogger("postulomaniaco.scheduler_3")

BUSQUEDAS_3 = [
    ("Desarrollador de Software", "Antioquia", "dds_antioquia_3"),
    ("Desarrollador Backend", "Antioquia", "backend_antioquia_3"),
    ("Desarrollador Frontend", "Antioquia", "frontend_antioquia_3"),
    ("Desarrollador FullStack", "Antioquia", "fullstack_antioquia_3"),
]

FREQUENCY_MINUTES = 60
JITTER_MINUTES = 15


async def main():
    logger.info("Scheduler _3 iniciado (cada %d min, secuencial)", FREQUENCY_MINUTES)

    while True:
        total_encontradas = 0

        for term, loc, slug in BUSQUEDAS_3:
            try:
                logger.info("Ejecutando scraper: %s en %s (3 dias)", term, loc)

                raw_data = await run_computrabajo(
                    search_term=term,
                    keyword_slug=slug,
                    apply_filter=True,
                    location=loc,
                    headless=True,
                    days=3,
                )

                if raw_data:
                    df = run_pipeline(raw_data, keyword_slug=slug)
                    if df is not None:
                        sync_to_master(df, slug=slug, keyword=term)

                    count = len(raw_data)
                    total_encontradas += count
                    logger.info("Ciclo completo (%s): %d ofertas", term, count)
                else:
                    logger.info("Ciclo completo (%s): 0 ofertas", term)

            except Exception as e:
                logger.error("Error en scraper (%s): %s", term, e)

        logger.info(
            "Ciclo _3 finalizado. Total ofertas: %d.",
            total_encontradas,
        )

        jitter = random.randint(0, JITTER_MINUTES)
        sleep_minutes = FREQUENCY_MINUTES + jitter
        logger.info("Próxima ejecución en %d minutos (+%d jitter)", sleep_minutes, jitter)
        await asyncio.sleep(sleep_minutes * 60)


if __name__ == "__main__":
    asyncio.run(main())
