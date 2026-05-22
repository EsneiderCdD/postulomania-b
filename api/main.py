import asyncio
import logging
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from api.routes import stats, ofertas, scraper, postulaciones, mapa

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)

app = FastAPI(
    title="Postulomaniaco API",
    description="Servicio de estadísticas para el análisis de ofertas laborales.",
    version="1.0.0"
)

# Registro de routers
app.include_router(stats.router, prefix="/api/v1")
app.include_router(ofertas.router, prefix="/api/v1")
app.include_router(scraper.router, prefix="/api/v1")
app.include_router(scraper.admin_router, prefix="/api/v1")
app.include_router(postulaciones.router, prefix="/api/v1")
app.include_router(mapa.router, prefix="/api/v1")



@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Postulomaniaco"}
