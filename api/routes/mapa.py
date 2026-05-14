from fastapi import APIRouter, Query
import pandas as pd
from database.db import engine

router = APIRouter(
    prefix="/mapa",
    tags=["mapa"]
)


@router.get("/ofertas")
def get_mapa_ofertas(departamento: str = Query("Antioquia")):
    """Devuelve ofertas con coordenadas para mostrar en mapa Leaflet."""
    try:
        query = """
        SELECT
            o.id_oferta,
            o.titulo,
            e.municipio,
            e.departamento,
            e.nombre AS empresa,
            e.direccion,
            e.lat,
            e.lng
        FROM ofertas o
        JOIN empresas e ON o.empresa_id = e.id
        WHERE e.lat IS NOT NULL
          AND o.departamento = %(dep)s
        ORDER BY o.fecha_publicacion_estimada DESC
        """
        df = pd.read_sql(query, engine, params={"dep": departamento})

        if df.empty:
            return {"total": 0, "ofertas": []}

        puntos = []
        for _, row in df.iterrows():
            puntos.append({
                "id_oferta": row["id_oferta"],
                "titulo": row["titulo"],
                "empresa": row["empresa"],
                "municipio": row["municipio"],
                "departamento": row["departamento"],
                "direccion": row["direccion"],
                "lat": float(row["lat"]),
                "lng": float(row["lng"]),
            })

        return {
            "total": len(puntos),
            "ofertas": puntos,
        }

    except Exception as e:
        return {"error": str(e)}
