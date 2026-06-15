from fastapi import APIRouter
from scrapers.computrabajo.main import run_computrabajo
from analytics.pipeline import run_pipeline
from analytics.master_sync import sync_to_master
from analytics.processes.persistence import reset_db
from correlation.correlator import apply_correlation
from analytics.processes.persistence import update_db_scores
from database.db import get_session
from database.models import Oferta
import pandas as pd

router = APIRouter(
    prefix="/scraper",
    tags=["scraper"]
)

admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.post("/dds")
async def run_dds():
    try:
        raw_data = await run_computrabajo(
            search_term="Desarrollador de Software",
            location="Antioquia",
            apply_filter=True
        )
        df_cleaned = run_pipeline(raw_data)
        if df_cleaned is not None:
            sync_to_master(df_cleaned, slug="dds", keyword="Desarrollador de Software")
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/dds-full")
async def run_dds_full():
    try:
        raw_data = await run_computrabajo(
            search_term="Desarrollador de Software",
            location="Antioquia",
            apply_filter=False
        )
        df_cleaned = run_pipeline(raw_data)
        if df_cleaned is not None:
            sync_to_master(df_cleaned, slug="dds_full", keyword="Desarrollador de Software")
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/fullstack")
async def run_fullstack():
    try:
        raw_data = await run_computrabajo(
            search_term="desarrollador full stack",
            location="Antioquia",
            apply_filter=False
        )
        df_cleaned = run_pipeline(raw_data)
        if df_cleaned is not None:
            sync_to_master(df_cleaned, slug="fullstack", keyword="desarrollador full stack")
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/refresh")
async def run_refresh():
    try:
        session = get_session()
        offers = session.query(Oferta).all()
        if not offers:
            session.close()
            return {"status": "error", "message": "No hay ofertas para refrescar"}

        data = [
            {
                "id_oferta": o.id_oferta,
                "titulo": o.titulo,
                "tech_stack": [t.nombre for t in o.tecnologias],
                "experiencia_anios": o.experiencia_anios,
                "requiere_ingles": o.requiere_ingles
            }
            for o in offers
        ]
        session.close()

        df = apply_correlation(pd.DataFrame(data))
        update_db_scores(df)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@admin_router.post("/reset-db")
async def run_reset_db():
    try:
        reset_db()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
