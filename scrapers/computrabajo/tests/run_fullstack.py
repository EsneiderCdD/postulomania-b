# DEPRECATED: Sin ubicación — no está en producción.
# Producción (scheduler/run_3.py) siempre usa location="Antioquia".
# Este script usaba location=None (camino B, formulario) que ya no se usa.
#
# import asyncio
# from scrapers.computrabajo.main import run_computrabajo
# from analytics.pipeline import run_pipeline
# from analytics.master_sync import sync_to_master
#
# async def main():
#     SEARCH_TERM = "desarrollador full stack"
#     SLUG = "fullstack"
#     try:
#         raw_data = await run_computrabajo(
#             search_term=SEARCH_TERM,
#             keyword_slug=SLUG,
#             apply_filter=False,
#             location=None
#         )
#         df_cleaned = run_pipeline(raw_data, keyword_slug=SLUG)
#         if df_cleaned is not None:
#             sync_to_master(df_cleaned, slug=SLUG, keyword=SEARCH_TERM)
#     except Exception as e:
#         raise e
#
# if __name__ == "__main__":
#     asyncio.run(main())
