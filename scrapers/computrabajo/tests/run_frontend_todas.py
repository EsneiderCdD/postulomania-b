import asyncio
from scrapers.computrabajo.main import run_computrabajo
from scrapers.computrabajo.searches import FRONTEND_TODAS as _SRC
from analytics.pipeline import run_pipeline
from analytics.master_sync import sync_to_master

async def main():
    """Ejecuta el ciclo de captura (todas, sin filtro) para Desarrollador Frontend en Antioquia."""
    SEARCH_TERM, LOCATION, SLUG, APPLY_FILTER, DAYS = _SRC

    try:
        raw_data = await run_computrabajo(
            search_term=SEARCH_TERM,
            apply_filter=APPLY_FILTER,
            location=LOCATION,
        )

        df_cleaned = run_pipeline(raw_data)

        if df_cleaned is not None:
            sync_to_master(df_cleaned, slug=SLUG, keyword=SEARCH_TERM)

    except Exception as e:
        raise e

if __name__ == "__main__":
    asyncio.run(main())
