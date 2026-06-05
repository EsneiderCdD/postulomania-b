from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
import pandas as pd
import numpy as np
from database.db import engine, get_session
from database.models import Empresa

router = APIRouter(
    prefix="/seguimientos",
    tags=["seguimientos"]
)


def _json_safe(val):
    if val is None:
        return None
    if isinstance(val, float) and np.isnan(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val) if not np.isnan(val) else None
    if isinstance(val, (np.bool_,)):
        return bool(val)
    return val


def _compute_estado_estrella(empresa):
    """Compute estado_estrella replicating the logic from mapa.py."""
    if empresa.estado_visual:
        return empresa.estado_visual

    postus = []
    try:
        query = """
        SELECT p.estado_proceso
        FROM postulaciones p
        JOIN ofertas o ON p.oferta_id = o.id
        WHERE o.empresa_id = %(empresa_id)s
        """
        df = pd.read_sql(query, engine, params={"empresa_id": empresa.id})
        postus = [{"estado": str(row["estado_proceso"])} for _, row in df.iterrows()]
    except Exception:
        pass

    if not postus:
        return "frio"

    ESTADO_PRIORITY = {
        "Finalista": 5,
        "HdV Vista": 4,
        "Postulado": 3,
        "Proceso finalizado": 2,
        "Suspendido": 1,
    }

    best = "frio"
    best_prio = 0
    for p in postus:
        prio = ESTADO_PRIORITY.get(p["estado"], 0)
        if prio > best_prio:
            best_prio = prio
            best = "postulado" if p["estado"] == "Postulado" else \
                   "hdv_vista" if p["estado"] == "HdV Vista" else \
                   "finalista" if p["estado"] == "Finalista" else \
                   "finalizado"
    return best


@router.get("/empresas")
def get_empresas_seguimiento():
    try:
        query = """
        SELECT e.id, e.nombre, e.tipo, e.foto_url, e.estado_visual
        FROM empresas e
        WHERE e.en_seguimiento = TRUE
        ORDER BY e.nombre
        """
        df = pd.read_sql(query, engine)

        empresas = []
        for _, row in df.iterrows():
            empresas.append({
                "id": int(row["id"]),
                "nombre": row["nombre"],
                "tipo": row["tipo"] if pd.notna(row["tipo"]) else None,
                "foto_url": row["foto_url"] if pd.notna(row["foto_url"]) else None,
                "estado_visual": row["estado_visual"] if pd.notna(row["estado_visual"]) else None,
            })

        return {"total": len(empresas), "empresas": empresas}

    except Exception as e:
        return {"error": str(e)}


@router.get("/{empresa_id}")
def get_seguimiento_detail(empresa_id: int):
    session = get_session()
    try:
        empresa = session.query(Empresa).filter_by(id=empresa_id).first()
        if not empresa:
            raise HTTPException(status_code=404, detail="Empresa no encontrada")
        if not empresa.en_seguimiento:
            raise HTTPException(status_code=404, detail="Esta empresa no está en seguimiento")

        query_ofertas = """
        SELECT
            o.id,
            o.titulo,
            o.enlace,
            c.score AS compatibilidad,
            CASE WHEN p.oferta_id IS NOT NULL THEN TRUE ELSE FALSE END AS postulado
        FROM ofertas o
        LEFT JOIN (
            SELECT DISTINCT ON (oferta_id) oferta_id, score
            FROM compatibilidades
            ORDER BY oferta_id, fecha_calculo DESC
        ) c ON o.id = c.oferta_id
        LEFT JOIN (
            SELECT DISTINCT oferta_id
            FROM postulaciones
        ) p ON o.id = p.oferta_id
        WHERE o.empresa_id = %(empresa_id)s
        ORDER BY c.score DESC NULLS LAST, o.id ASC
        """
        df_ofertas = pd.read_sql(query_ofertas, engine, params={"empresa_id": empresa_id})

        ofertas = []
        for _, row in df_ofertas.iterrows():
            ofertas.append({
                "id": int(row["id"]),
                "titulo": row["titulo"],
                "enlace": row["enlace"] if pd.notna(row["enlace"]) else None,
                "compatibilidad": float(row["compatibilidad"]) if pd.notna(row["compatibilidad"]) else None,
                "postulado": bool(row["postulado"]),
            })

        query_techs = """
        SELECT t.nombre AS tech, COUNT(DISTINCT ot.oferta_id) AS ofertas
        FROM ofertas_tecnologias ot
        JOIN tecnologias t ON ot.tecnologia_id = t.id
        JOIN ofertas o ON ot.oferta_id = o.id
        WHERE o.empresa_id = %(empresa_id)s
        GROUP BY t.nombre
        ORDER BY ofertas DESC, t.nombre ASC
        """
        df_techs = pd.read_sql(query_techs, engine, params={"empresa_id": empresa_id})

        tecnologias = []
        for _, row in df_techs.iterrows():
            tecnologias.append({
                "tech": row["tech"],
                "ofertas": int(row["ofertas"]),
            })

        estado_estrella = _compute_estado_estrella(empresa)

        return {
            "empresa": {
                "id": empresa.id,
                "nombre": empresa.nombre,
                "tipo": empresa.tipo,
                "foto_url": empresa.foto_url,
                "estado_visual": empresa.estado_visual,
                "estado_estrella": estado_estrella,
            },
            "ofertas": ofertas,
            "tecnologias": tecnologias,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
