from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, field_validator
from database.db import get_session
from database.models import Nota

router = APIRouter(
    prefix="/notas",
    tags=["notas"]
)

MAX_PALABRAS = 200


def _contar_palabras(texto: str) -> int:
    return len(texto.strip().split()) if texto.strip() else 0


class NotaCreate(BaseModel):
    oferta_id: int | None = None
    empresa_id: int | None = None
    contenido: str

    @field_validator("contenido")
    @classmethod
    def validar_contenido(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El contenido no puede estar vacío")
        palabras = _contar_palabras(v)
        if palabras > MAX_PALABRAS:
            raise ValueError(f"Máximo {MAX_PALABRAS} palabras ({palabras} actuales)")
        return v.strip()


class NotaUpdate(BaseModel):
    contenido: str

    @field_validator("contenido")
    @classmethod
    def validar_contenido(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El contenido no puede estar vacío")
        palabras = _contar_palabras(v)
        if palabras > MAX_PALABRAS:
            raise ValueError(f"Máximo {MAX_PALABRAS} palabras ({palabras} actuales)")
        return v.strip()


def _nota_a_dict(nota: Nota) -> dict:
    return {
        "id": nota.id,
        "oferta_id": nota.oferta_id,
        "empresa_id": nota.empresa_id,
        "contenido": nota.contenido,
        "fecha_creacion": nota.fecha_creacion.isoformat() if nota.fecha_creacion else None,
    }


@router.get("")
def listar_notas(oferta_id: int | None = Query(None), empresa_id: int | None = Query(None)):
    session = get_session()
    try:
        query = session.query(Nota)
        if oferta_id is not None:
            query = query.filter(Nota.oferta_id == oferta_id)
        if empresa_id is not None:
            query = query.filter(Nota.empresa_id == empresa_id)
        if oferta_id is None and empresa_id is None:
            raise HTTPException(status_code=400, detail="Debe especificar oferta_id o empresa_id")

        notas = query.order_by(Nota.fecha_creacion.desc()).all()
        return {"notas": [_nota_a_dict(n) for n in notas]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.post("")
def crear_nota(body: NotaCreate):
    if body.oferta_id is None and body.empresa_id is None:
        raise HTTPException(status_code=400, detail="Debe especificar oferta_id o empresa_id")
    if body.oferta_id is not None and body.empresa_id is not None:
        raise HTTPException(status_code=400, detail="Solo uno: oferta_id o empresa_id")

    session = get_session()
    try:
        nota = Nota(
            oferta_id=body.oferta_id,
            empresa_id=body.empresa_id,
            contenido=body.contenido,
        )
        session.add(nota)
        session.commit()
        session.refresh(nota)
        return _nota_a_dict(nota)
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.put("/{nota_id}")
def actualizar_nota(nota_id: int, body: NotaUpdate):
    session = get_session()
    try:
        nota = session.query(Nota).filter_by(id=nota_id).first()
        if not nota:
            raise HTTPException(status_code=404, detail="Nota no encontrada")

        nota.contenido = body.contenido
        session.commit()
        session.refresh(nota)
        return _nota_a_dict(nota)
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.delete("/{nota_id}")
def eliminar_nota(nota_id: int):
    session = get_session()
    try:
        nota = session.query(Nota).filter_by(id=nota_id).first()
        if not nota:
            raise HTTPException(status_code=404, detail="Nota no encontrada")

        session.delete(nota)
        session.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
