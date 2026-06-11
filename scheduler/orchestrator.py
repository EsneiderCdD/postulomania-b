import asyncio
import json
import logging
import os
import random
from datetime import datetime

import pandas as pd
from analytics.master_sync import sync_to_master
from analytics.pipeline import run_pipeline
from correlation.correlator import apply_correlation
from analytics.processes.persistence import update_db_scores
from database.db import get_session
from database.models import Oferta
from modules.notifier import notify
from scrapers.computrabajo.main import run_computrabajo

logger = logging.getLogger("postulomaniaco.scheduler")

BUSQUEDAS = [
    ("Desarrollador de Software", "Antioquia"),
    ("Desarrollador Backend", "Antioquia"),
    ("Desarrollador Frontend", "Antioquia"),
]

STATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config",
    "scheduler_state.json"
)


def _read_state():
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"enabled": False}


def _write_state(state):
    try:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


async def start():
    logger.info("Scheduler iniciado")
    notify("Postulomaniaco", "Hola Mundo — scheduler activo")

    while True:
        state = _read_state()

        if not state.get("enabled"):
            logger.info("Scheduler desactivado. Finalizando.")
            notify("Postulomaniaco", "Scheduler detenido")
            break

        any_new = False
        total_encontradas = 0

        for term, loc in BUSQUEDAS:
            try:
                logger.info("Ejecutando scraper: %s en %s", term, loc)

                raw_data = await run_computrabajo(
                    search_term=term,
                    keyword_slug="scheduler",
                    apply_filter=True,
                    location=loc,
                    headless=True,
                )

                if raw_data:
                    df = run_pipeline(raw_data, keyword_slug="scheduler")
                    if df is not None:
                        sync_to_master(df, slug="scheduler", keyword=term)
                        any_new = True

                    count = len(raw_data)
                    total_encontradas += count
                    notify(
                        "Postulomaniaco",
                        f"{count} ofertas de {term} en {loc}",
                    )
                    logger.info("Ciclo completo (%s): %d ofertas", term, count)
                else:
                    logger.info("Ciclo completo (%s): 0 ofertas", term)

            except Exception as e:
                logger.error("Error en scraper (%s): %s", term, e)

        if any_new:
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

        state["last_run"] = datetime.now().isoformat()
        state["last_offers_count"] = total_encontradas
        _write_state(state)

        freq = state.get("frequency_minutes", 60)
        jitter = random.randint(0, state.get("jitter_minutes", 15))
        sleep_seconds = (freq + jitter) * 60
        logger.info("Próxima ejecución en %d minutos", freq + jitter)
        await asyncio.sleep(sleep_seconds)
