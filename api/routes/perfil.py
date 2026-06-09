from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.db import get_session
from database.models import Tecnologia, CategoriaTech, PerfilTecnologia
from sqlalchemy import func

router = APIRouter(
    prefix="/perfil",
    tags=["perfil"]
)


class ScoreEntry(BaseModel):
    tecnologia_id: int
    score: float


class ScoresUpdate(BaseModel):
    scores: dict[str, float]


@router.get("/")
def get_perfil():
    session = get_session()
    try:
        total_techs_db = (
            session.query(func.count(Tecnologia.id))
            .filter(Tecnologia.categoria_id.isnot(None))
            .scalar()
        ) or 0

        rows = (
            session.query(Tecnologia.nombre, CategoriaTech.nombre, PerfilTecnologia.score)
            .join(CategoriaTech, Tecnologia.categoria_id == CategoriaTech.id)
            .outerjoin(PerfilTecnologia, PerfilTecnologia.tecnologia_id == Tecnologia.id)
            .order_by(Tecnologia.nombre)
            .all()
        )

        tecnico: dict[str, float] = {}
        tecnologias_db: list[str] = []
        categorias: dict[str, str] = {}

        for tech_nombre, cat_nombre, score in rows:
            tecnologias_db.append(tech_nombre)
            categorias[tech_nombre] = cat_nombre or "otras"
            tecnico[tech_nombre] = round(score, 2) if score is not None else 0.0

        techs_calificadas = sum(1 for s in tecnico.values() if s > 0)
        score_promedio = (
            round(sum(s for s in tecnico.values() if s > 0) / techs_calificadas, 2)
            if techs_calificadas > 0
            else 0.0
        )
        techs_no_calificadas = max(0, total_techs_db - techs_calificadas)

        return {
            "tecnico": tecnico,
            "categorias": categorias,
            "idiomas": {"ingles": 0.0},
            "experiencia": 0.0,
            "nivel_educativo": 0,
            "metricas": {
                "total_tecnologias_db": total_techs_db,
                "tecnologias_calificadas": techs_calificadas,
                "tecnologias_sin_calificar": techs_no_calificadas,
                "score_promedio": score_promedio,
            },
            "tecnologias_db": tecnologias_db,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.post("/")
def create_score(entry: ScoreEntry):
    session = get_session()
    try:
        tech = session.query(Tecnologia).filter(Tecnologia.id == entry.tecnologia_id).first()
        if not tech:
            raise HTTPException(status_code=404, detail="Tecnología no encontrada")

        existe = (
            session.query(PerfilTecnologia)
            .filter(PerfilTecnologia.tecnologia_id == entry.tecnologia_id)
            .first()
        )
        if existe:
            raise HTTPException(status_code=409, detail="Ya existe un puntaje para esta tecnología. Usá PUT para modificarlo.")

        nuevo = PerfilTecnologia(tecnologia_id=entry.tecnologia_id, score=entry.score)
        session.add(nuevo)
        session.commit()
        session.refresh(nuevo)
        return {"id": nuevo.id, "tecnologia_id": nuevo.tecnologia_id, "score": nuevo.score}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.put("/")
def update_scores(payload: ScoresUpdate):
    session = get_session()
    try:
        tech_names = list(payload.scores.keys())
        techs_db = session.query(Tecnologia).filter(Tecnologia.nombre.in_(tech_names)).all()
        tech_map = {t.nombre: t.id for t in techs_db}

        no_encontradas = [n for n in tech_names if n not in tech_map]
        if no_encontradas:
            raise HTTPException(status_code=404, detail=f"Tecnologías no encontradas: {', '.join(no_encontradas)}")

        for nombre, score in payload.scores.items():
            tid = tech_map[nombre]
            existing = (
                session.query(PerfilTecnologia)
                .filter(PerfilTecnologia.tecnologia_id == tid)
                .first()
            )
            if existing:
                existing.score = score
            else:
                session.add(PerfilTecnologia(tecnologia_id=tid, score=score))

        session.commit()
        return {"message": "Puntajes actualizados", "actualizados": len(payload.scores)}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.delete("/{perfil_tech_id}")
def delete_score(perfil_tech_id: int):
    session = get_session()
    try:
        entry = session.query(PerfilTecnologia).filter(PerfilTecnologia.id == perfil_tech_id).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Puntaje no encontrado")
        session.delete(entry)
        session.commit()
        return {"message": "Puntaje eliminado", "id": perfil_tech_id}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
