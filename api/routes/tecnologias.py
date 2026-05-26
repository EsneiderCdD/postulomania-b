from fastapi import APIRouter, HTTPException
from database.db import get_session
from database.models import Tecnologia, CategoriaTech

router = APIRouter(
    prefix="/tecnologias",
    tags=["tecnologias"]
)


@router.get("/")
def get_tecnologias():
    session = get_session()
    try:
        techs = (
            session.query(Tecnologia, CategoriaTech.nombre)
            .outerjoin(CategoriaTech, Tecnologia.categoria_id == CategoriaTech.id)
            .order_by(Tecnologia.nombre)
            .all()
        )

        return {
            "total": len(techs),
            "tecnologias": [
                {
                    "id": t.id,
                    "nombre": t.nombre,
                    "categoria": cat_nombre,
                }
                for t, cat_nombre in techs
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
