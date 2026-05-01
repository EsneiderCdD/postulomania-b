from fastapi import FastAPI
from api.routes import stats, ofertas

app = FastAPI(
    title="Postulomaniaco API",
    description="Servicio de estadísticas para el análisis de ofertas laborales.",
    version="1.0.0"
)

# Registro de routers
app.include_router(stats.router, prefix="/api/v1")
app.include_router(ofertas.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Postulomaniaco"}
