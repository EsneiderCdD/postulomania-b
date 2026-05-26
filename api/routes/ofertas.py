from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import pandas as pd
import numpy as np
from database.db import engine, get_session
from database.models import Oferta, Empresa, Tecnologia, OfertaTecnologia, Compatibilidad

router = APIRouter(
    prefix="/ofertas",
    tags=["ofertas"]
)


class OfertaCreate(BaseModel):
    id_oferta: str
    origen_proceso: str
    titulo: Optional[str] = None
    enlace: Optional[str] = None
    descripcion: Optional[str] = None
    municipio: Optional[str] = None
    departamento: Optional[str] = None
    fecha_publicacion_estimada: Optional[datetime] = None
    experiencia_anios: Optional[float] = None
    requiere_ingles: bool = False
    keyword: Optional[str] = None
    empresa_id: Optional[int] = None
    tecnologias: Optional[list[str]] = None
    compatibilidad: Optional[float] = None

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
        LEFT JOIN (
            SELECT DISTINCT ON (oferta_id) oferta_id, score
            FROM compatibilidades
            ORDER BY oferta_id, fecha_calculo DESC
        ) c ON o.id = c.oferta_id
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


@router.post("/")
def create_oferta(data: OfertaCreate):
    session = get_session()
    try:
        ORIGENES = {"dds", "dds_full", "fullstack", "linkedin", "freelance", "otro"}
        if data.origen_proceso not in ORIGENES:
            raise HTTPException(
                status_code=400,
                detail=f"origen_proceso inválido: '{data.origen_proceso}'. Valores: {', '.join(sorted(ORIGENES))}",
            )

        existing = session.query(Oferta).filter_by(id_oferta=data.id_oferta).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"id_oferta '{data.id_oferta}' ya existe",
            )

        if data.empresa_id is not None:
            empresa = session.query(Empresa).filter_by(id=data.empresa_id).first()
            if not empresa:
                raise HTTPException(
                    status_code=400,
                    detail=f"Empresa #{data.empresa_id} no encontrada",
                )

        now = datetime.now()
        oferta = Oferta(
            **data.model_dump(exclude={"tecnologias", "compatibilidad"}),
            fecha_extraccion=now,
        )
        session.add(oferta)
        session.flush()

        if data.compatibilidad is not None:
            session.add(
                Compatibilidad(
                    oferta_id=oferta.id,
                    score=float(data.compatibilidad),
                )
            )

        if data.tecnologias:
            tech_map = {t.nombre: t.id for t in session.query(Tecnologia).all()}
            for nombre in data.tecnologias:
                nombre_clean = nombre.strip()
                if not nombre_clean:
                    continue
                tid = tech_map.get(nombre_clean)
                if tid is None:
                    tech = Tecnologia(nombre=nombre_clean)
                    session.add(tech)
                    session.flush()
                    tid = tech.id
                    tech_map[nombre_clean] = tid
                session.add(OfertaTecnologia(oferta_id=oferta.id, tecnologia_id=tid))

        session.commit()
        session.refresh(oferta)

        return {
            "id": oferta.id,
            "id_oferta": oferta.id_oferta,
            "titulo": oferta.titulo,
            "enlace": oferta.enlace,
            "descripcion": oferta.descripcion,
            "municipio": oferta.municipio,
            "departamento": oferta.departamento,
            "fecha_publicacion_estimada": (
                oferta.fecha_publicacion_estimada.strftime("%Y-%m-%d %H:%M:%S")
                if oferta.fecha_publicacion_estimada
                else None
            ),
            "fecha_extraccion": (
                oferta.fecha_extraccion.strftime("%Y-%m-%d %H:%M:%S")
                if oferta.fecha_extraccion
                else None
            ),
            "experiencia_anios": oferta.experiencia_anios,
            "requiere_ingles": oferta.requiere_ingles,
            "keyword": oferta.keyword,
            "origen_proceso": oferta.origen_proceso,
            "empresa_id": oferta.empresa_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
