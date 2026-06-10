from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.db import get_session
from database.models import Tecnologia, CategoriaTech

router = APIRouter(
    prefix="/tecnologias",
    tags=["tecnologias"]
)


class NuevaTecnologia(BaseModel):
    nombre: str
    categoria: str


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


@router.post("/")
def create_tecnologia(payload: NuevaTecnologia):
    session = get_session()
    try:
        nombre = payload.nombre.strip()
        if not nombre:
            raise HTTPException(status_code=422, detail="El nombre de la tecnología es obligatorio.")

        existente = session.query(Tecnologia).filter(Tecnologia.nombre == nombre).first()
        if existente:
            cat = session.query(CategoriaTech).filter(CategoriaTech.id == existente.categoria_id).first()
            return {
                "id": existente.id,
                "nombre": existente.nombre,
                "categoria": cat.nombre if cat else None,
                "existia": True,
            }

        cat_nombre = payload.categoria.strip().lower()
        categoria = session.query(CategoriaTech).filter(CategoriaTech.nombre == cat_nombre).first()
        if not categoria:
            if not cat_nombre:
                raise HTTPException(status_code=422, detail="La categoría es obligatoria para una nueva tecnología.")
            categoria = CategoriaTech(nombre=cat_nombre)
            session.add(categoria)
            session.flush()

        nueva = Tecnologia(nombre=nombre, categoria_id=categoria.id)
        session.add(nueva)
        session.commit()
        session.refresh(nueva)

        return {
            "id": nueva.id,
            "nombre": nueva.nombre,
            "categoria": categoria.nombre,
            "existia": False,
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
