import asyncio
from scrapers.computrabajo.main import run_computrabajo
from analytics.pipeline import run_pipeline
from analytics.master_sync import sync_to_master

async def main():
    """Ejecuta el ciclo de captura (hoy) para Desarrollador de Software en Antioquia."""
    SEARCH_TERM = "Desarrollador de Software"
    SLUG = "dds_antioquia_1"
    LOCATION = "Antioquia"
    
    try:
        raw_data = await run_computrabajo(
            search_term=SEARCH_TERM, 
            keyword_slug=SLUG, 
            apply_filter=True,
            location=LOCATION
        )
        
        df_cleaned = run_pipeline(raw_data, keyword_slug=SLUG)
        
        if df_cleaned is not None:
            sync_to_master(df_cleaned, slug=SLUG, keyword=SEARCH_TERM)

    except Exception as e:
        raise e

if __name__ == "__main__":
    asyncio.run(main())
