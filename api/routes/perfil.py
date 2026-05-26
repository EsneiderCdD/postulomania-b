import json
import os
from fastapi import APIRouter, HTTPException
from database.db import get_session
from database.models import Tecnologia
from sqlalchemy import func

router = APIRouter(
    prefix="/perfil",
    tags=["perfil"]
)

PROFILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "correlation", "profile", "user_profile.json"
)


def _leer_profile() -> dict:
    if not os.path.exists(PROFILE_PATH):
        raise HTTPException(status_code=404, detail="Archivo de perfil no encontrado")
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/")
def get_perfil():
    session = get_session()
    try:
        profile = _leer_profile()

        total_techs_db = session.query(func.count(Tecnologia.id)).scalar() or 0
        techs_perfil = profile.get("tecnico", {})

        techs_calificadas = len(techs_perfil)
        score_promedio = (
            round(sum(techs_perfil.values()) / techs_calificadas, 3)
            if techs_calificadas > 0
            else 0
        )
        techs_no_calificadas = max(0, total_techs_db - techs_calificadas)

        techs_db = (
            session.query(Tecnologia).order_by(Tecnologia.nombre).all()
        )
        techs_db_nombres = [t.nombre for t in techs_db]

        return {
            "tecnico": techs_perfil,
            "idiomas": profile.get("idiomas", {}),
            "experiencia": profile.get("experiencia", 0),
            "nivel_educativo": profile.get("nivel_educativo", 0),
            "metricas": {
                "total_tecnologias_db": total_techs_db,
                "tecnologias_calificadas": techs_calificadas,
                "tecnologias_sin_calificar": techs_no_calificadas,
                "score_promedio": score_promedio,
            },
            "tecnologias_db": techs_db_nombres,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
