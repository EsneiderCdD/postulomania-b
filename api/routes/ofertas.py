from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import pandas as pd
import numpy as np
from database.db import engine, get_session
from database.models import Oferta, Empresa, Tecnologia, OfertaTecnologia, Compatibilidad
from sqlalchemy import func


def _resolver_empresa(session, empresa_nombre: str | None, empresa_id: int | None) -> int | None:
    if empresa_id is not None:
        emp = session.query(Empresa).filter_by(id=empresa_id).first()
        if not emp:
            raise HTTPException(status_code=400, detail=f"Empresa #{empresa_id} no encontrada")
        return emp.id
    if empresa_nombre and empresa_nombre.strip():
        nombre = empresa_nombre.strip()
        emp = session.query(Empresa).filter(
            func.lower(Empresa.nombre) == nombre.lower()
        ).first()
        if not emp:
            emp = Empresa(nombre=nombre)
            session.add(emp)
            session.flush()
        return emp.id
    return None

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
    empresa: Optional[str] = None
    empresa_id: Optional[int] = None
    tecnologias: Optional[list[str]] = None
    compatibilidad: Optional[float] = None


class OfertaUpdate(BaseModel):
    id_oferta: Optional[str] = None
    origen_proceso: Optional[str] = None
    titulo: Optional[str] = None
    enlace: Optional[str] = None
    descripcion: Optional[str] = None
    municipio: Optional[str] = None
    departamento: Optional[str] = None
    fecha_publicacion_estimada: Optional[datetime] = None
    experiencia_anios: Optional[float] = None
    requiere_ingles: Optional[bool] = None
    keyword: Optional[str] = None
    empresa: Optional[str] = None
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
def get_ofertas(q: str = Query(None, description="Buscar por título o empresa"), limite: int = Query(20, ge=1, le=200)):
    try:
        where_clause = ""
        params = {}
        if q:
            where_clause = "WHERE (LOWER(o.titulo) LIKE %(q)s OR LOWER(e.nombre) LIKE %(q)s)"
            params["q"] = f"%{q.lower()}%"
            order_clause = "o.fecha_publicacion_estimada DESC"
        else:
            order_clause = "o.fecha_publicacion_estimada DESC"

        query_ofertas = f"""
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
        {where_clause}
        ORDER BY {order_clause}
        {f"LIMIT {limite}" if q else ""}
        """
        df = pd.read_sql(query_ofertas, engine, params=params if q else None)

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

        emp_id = _resolver_empresa(session, data.empresa, data.empresa_id)

        now = datetime.now()
        oferta = Oferta(
            **data.model_dump(exclude={"tecnologias", "compatibilidad", "empresa", "empresa_id"}),
            empresa_id=emp_id,
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
            "empresa": oferta.empresa.nombre if oferta.empresa else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.get("/{oferta_id}")
def get_oferta(oferta_id: int):
    session = get_session()
    try:
        oferta = session.query(Oferta).filter_by(id=oferta_id).first()
        if not oferta:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")

        tecnologias = [t.nombre for t in oferta.tecnologias]

        ultima_comp = None
        if oferta.compatibilidades:
            ultima = sorted(oferta.compatibilidades, key=lambda c: c.fecha_calculo, reverse=True)
            if ultima:
                ultima_comp = ultima[0].score

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
            "empresa": oferta.empresa.nombre if oferta.empresa else None,
            "tecnologias": tecnologias,
            "compatibilidad": ultima_comp,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.put("/{oferta_id}")
def update_oferta(oferta_id: int, data: OfertaUpdate):
    session = get_session()
    try:
        oferta = session.query(Oferta).filter_by(id=oferta_id).first()
        if not oferta:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")

        update_data = data.model_dump(exclude_unset=True, exclude={"tecnologias", "compatibilidad", "empresa", "empresa_id"})
        excluidas = {"tecnologias", "compatibilidad", "empresa", "empresa_id"}
        ORIGENES = {"dds", "dds_full", "fullstack", "linkedin", "freelance", "otro"}

        if "origen_proceso" in update_data:
            if update_data["origen_proceso"] not in ORIGENES:
                raise HTTPException(
                    status_code=400,
                    detail=f"origen_proceso inválido. Valores: {', '.join(sorted(ORIGENES))}",
                )

        if "id_oferta" in update_data and update_data["id_oferta"] != oferta.id_oferta:
            existing = session.query(Oferta).filter(
                Oferta.id_oferta == update_data["id_oferta"],
                Oferta.id != oferta_id,
            ).first()
            if existing:
                raise HTTPException(
                    status_code=409,
                    detail=f"id_oferta '{update_data['id_oferta']}' ya existe",
                )

        if data.empresa is not None or data.empresa_id is not None:
            oferta.empresa_id = _resolver_empresa(session, data.empresa, data.empresa_id)

        for campo, valor in update_data.items():
            if campo not in excluidas:
                setattr(oferta, campo, valor)

        if data.compatibilidad is not None:
            session.query(Compatibilidad).filter(
                Compatibilidad.oferta_id == oferta_id
            ).delete(synchronize_session="fetch")
            session.add(
                Compatibilidad(oferta_id=oferta_id, score=float(data.compatibilidad))
            )

        if data.tecnologias is not None:
            session.query(OfertaTecnologia).filter(
                OfertaTecnologia.oferta_id == oferta_id
            ).delete(synchronize_session="fetch")
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
                session.add(OfertaTecnologia(oferta_id=oferta_id, tecnologia_id=tid))

        session.commit()
        session.refresh(oferta)

        return {
            "id": oferta.id,
            "id_oferta": oferta.id_oferta,
            "titulo": oferta.titulo,
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
