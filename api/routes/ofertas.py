from fastapi import APIRouter
import pandas as pd
import numpy as np
from database.db import engine

router = APIRouter(
    prefix="/ofertas",
    tags=["ofertas"]
)

def _json_safe(val):
    if val is None:
        return None
    if isinstance(val, (pd.Timestamp,)):
        return val.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(val, float) and np.isnan(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val) if not np.isnan(val) else None
    if isinstance(val, (np.bool_,)):
        return bool(val)
    if isinstance(val, (list,)):
        return [_json_safe(v) for v in val]
    return val

@router.get("/")
def get_ofertas():
    try:
        query_ofertas = """
        SELECT
            o.id,
            o.id_oferta,
            o.titulo,
            o.enlace,
            o.descripcion,
            o.fecha_publicacion_estimada,
            o.fecha_extraccion,
            o.experiencia_anios,
            o.requiere_ingles,
            o.keyword,
            o.origen_proceso,
            o.empresa_id,
            e.nombre AS empresa,
            c.score AS compatibilidad
        FROM ofertas o
        LEFT JOIN empresas e ON o.empresa_id = e.id
        LEFT JOIN compatibilidades c ON o.id = c.oferta_id
        ORDER BY o.fecha_publicacion_estimada DESC
        """
        df = pd.read_sql(query_ofertas, engine)

        if df.empty:
            return {"total": 0, "ofertas": []}

        query_techs = """
        SELECT ot.oferta_id, t.nombre AS tech
        FROM ofertas_tecnologias ot
        JOIN tecnologias t ON ot.tecnologia_id = t.id
        """
        df_techs = pd.read_sql(query_techs, engine)

        techs_por_oferta = (
            df_techs.groupby("oferta_id")["tech"]
            .apply(list)
            .to_dict()
        )

        df["tecnologias"] = df["id"].map(techs_por_oferta).apply(
            lambda x: x if isinstance(x, list) else []
        )

        ofertas = []
        for _, row in df.iterrows():
            oferta = {col: _json_safe(row[col]) for col in df.columns}
            ofertas.append(oferta)

        return {
            "total": len(ofertas),
            "ofertas": ofertas
        }

    except Exception as e:
        return {"error": str(e)}
