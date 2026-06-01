import asyncio
import logging
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import pandas as pd

from analytics.master_sync import sync_to_master
from analytics.pipeline import run_pipeline
from analytics.processes.persistence import update_db_scores
from correlation.correlator import apply_correlation
from database.db import get_session
from database.models import Oferta
from scrapers.computrabajo.main import run_computrabajo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)

logger = logging.getLogger("postulomaniaco.scheduler_3")

BUSQUEDAS_3 = [
    ("Desarrollador de Software", "Antioquia", "dds_antioquia_3",                 True,   3),
    ("Desarrollador de Software", "Antioquia", "desarrollador_software_antioquia", False, None),
    ("Desarrollador Backend",     "Antioquia", "backend_antioquia_3",              True,   3),
    ("Desarrollador Backend",     "Antioquia", "backend_antioquia_todas",          False, None),
    ("Desarrollador Frontend",    "Antioquia", "frontend_antioquia_3",             True,   3),
    ("Desarrollador Frontend",    "Antioquia", "frontend_antioquia_todas",         False, None),
    ("Desarrollador FullStack",   "Antioquia", "fullstack_antioquia_3",            True,   3),
    ("Desarrollador FullStack",   "Antioquia", "fullstack_antioquia_todas",        False, None),
]

FREQUENCY_MINUTES = 60
JITTER_MINUTES = 15
INTER_SEARCH_DELAY_MIN = 30
INTER_SEARCH_DELAY_MAX = 90


async def main():
    logger.info("Scheduler _3 iniciado (cada %d min, secuencial)", FREQUENCY_MINUTES)

    while True:
        total_encontradas = 0

        for i, (term, loc, slug, filtrar, dias) in enumerate(BUSQUEDAS_3):
            try:
                logger.info("Ejecutando scraper: %s en %s (filtrar=%s, dias=%s)", term, loc, filtrar, dias)

                raw_data = await run_computrabajo(
                    search_term=term,
                    keyword_slug=slug,
                    apply_filter=filtrar,
                    location=loc,
                    headless=True,
                    days=dias if dias else 1,
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

            if i < len(BUSQUEDAS_3) - 1:
                delay = random.randint(INTER_SEARCH_DELAY_MIN, INTER_SEARCH_DELAY_MAX)
                logger.info("Pausa entre búsquedas: %d segundos", delay)
                await asyncio.sleep(delay)

        if total_encontradas > 0:
            try:
                session = get_session()
                try:
                    offers = session.query(Oferta).all()
                    if offers:
                        data = [
                            {
                                "id_oferta": o.id_oferta,
                                "titulo": o.titulo,
                                "tech_stack": [t.nombre for t in o.tecnologias],
                                "experiencia_anios": o.experiencia_anios,
                                "requiere_ingles": o.requiere_ingles,
                            }
                            for o in offers
                        ]
                        scores_df = apply_correlation(pd.DataFrame(data))
                        update_db_scores(scores_df)
                        logger.info("Scores de compatibilidad actualizados")
                finally:
                    session.close()
            except Exception as e:
                logger.error("Error en refresh de scores: %s", e)

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
