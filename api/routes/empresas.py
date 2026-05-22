from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database.db import get_session
from database.models import Empresa

router = APIRouter(
    prefix="/empresas",
    tags=["empresas"]
)


class EmpresaUpdate(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None
    direccion: Optional[str] = None
    website: Optional[str] = None
    municipio: Optional[str] = None
    departamento: Optional[str] = None


@router.put("/{empresa_id}")
def update_empresa(empresa_id: int, data: EmpresaUpdate):
    session = get_session()
    try:
        empresa = session.query(Empresa).filter_by(id=empresa_id).first()
        if not empresa:
            raise HTTPException(status_code=404, detail="Empresa no encontrada")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(empresa, field, value)

        session.commit()
        return {"status": "ok", "empresa_id": empresa_id}

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
