import asyncio
from scrapers.computrabajo.main import run_computrabajo
from scrapers.computrabajo.searches import FULLSTACK_3 as _SRC
from analytics.pipeline import run_pipeline
from analytics.master_sync import sync_to_master

async def main():
    """Ejecuta el ciclo de captura (3 días) para Desarrollador FullStack en Antioquia."""
    SEARCH_TERM, LOCATION, SLUG, APPLY_FILTER, DAYS = _SRC

    try:
        raw_data = await run_computrabajo(
            search_term=SEARCH_TERM,
            keyword_slug=SLUG,
            apply_filter=APPLY_FILTER,
            location=LOCATION,
            days=DAYS
        )

        df_cleaned = run_pipeline(raw_data, keyword_slug=SLUG)

        if df_cleaned is not None:
            sync_to_master(df_cleaned, slug=SLUG, keyword=SEARCH_TERM)

    except Exception as e:
        raise e

if __name__ == "__main__":
    asyncio.run(main())
