from fastapi import APIRouter
from sqlalchemy.orm import joinedload
from database.db import get_session
from database.models import Postulacion, Oferta, Empresa, EstadoProceso
from datetime import datetime, timezone

router = APIRouter(
    prefix="/postulaciones",
    tags=["postulaciones"]
)


def _postulacion_to_dict(p):
    oferta = p.oferta
    return {
        "id": p.id,
        "oferta_id": p.oferta_id,
        "cargo": oferta.titulo if oferta else None,
        "empresa": oferta.empresa.nombre if oferta and oferta.empresa else None,
        "link": oferta.enlace if oferta else None,
        "fecha_postulacion": p.fecha_postulacion.strftime("%Y-%m-%d %H:%M:%S") if p.fecha_postulacion else None,
        "plataforma": p.plataforma,
        "estado_proceso": p.estado_proceso,
    }


@router.get("/")
def get_postulaciones():
    try:
        session = get_session()
        postulaciones = (
            session.query(Postulacion)
            .options(joinedload(Postulacion.oferta).joinedload(Oferta.empresa))
            .order_by(Postulacion.id.desc())
            .all()
        )
        result = [_postulacion_to_dict(p) for p in postulaciones]
        session.close()
        return {"total": len(result), "postulaciones": result}
    except Exception as e:
        return {"error": str(e)}


@router.get("/{id}")
def get_postulacion(id: int):
    try:
        session = get_session()
        p = (
            session.query(Postulacion)
            .options(joinedload(Postulacion.oferta).joinedload(Oferta.empresa))
            .filter(Postulacion.id == id)
            .first()
        )
        session.close()
        if not p:
            return {"error": "Postulacion no encontrada"}
        return {"postulacion": _postulacion_to_dict(p)}
    except Exception as e:
        return {"error": str(e)}


@router.post("/")
def create_postulacion(payload: dict):
    try:
        session = get_session()

        oferta_id = payload.get("oferta_id")
        estado_raw = payload.get("estado_proceso")

        if not oferta_id or not estado_raw:
            session.close()
            return {"error": "oferta_id y estado_proceso son requeridos"}

        oferta = session.query(Oferta).filter(Oferta.id == oferta_id).first()
        if not oferta:
            session.close()
            return {"error": f"Oferta #{oferta_id} no encontrada"}

        try:
            estado = EstadoProceso(estado_raw)
        except ValueError:
            session.close()
            validos = [e.value for e in EstadoProceso]
            return {"error": f"Estado invalido: '{estado_raw}'. Valores permitidos: {validos}"}

        fecha = payload.get("fecha_postulacion")
        if fecha:
            try:
                fecha = datetime.fromisoformat(str(fecha).replace("Z", "+00:00"))
            except ValueError:
                session.close()
                return {"error": "Formato de fecha invalido. Usa ISO 8601 (YYYY-MM-DDTHH:MM:SS)"}

        p = Postulacion(
            oferta_id=oferta_id,
            estado_proceso=estado,
            plataforma=payload.get("plataforma"),
            fecha_postulacion=fecha or datetime.now(timezone.utc),
        )
        session.add(p)
        session.commit()
        session.refresh(p)
        result = _postulacion_to_dict(p)
        session.close()
        return {"postulacion": result}
    except Exception as e:
        return {"error": str(e)}


@router.put("/{id}")
def update_postulacion(id: int, payload: dict):
    try:
        session = get_session()
        p = session.query(Postulacion).filter(Postulacion.id == id).first()
        if not p:
            session.close()
            return {"error": "Postulacion no encontrada"}

        if "estado_proceso" in payload:
            try:
                p.estado_proceso = EstadoProceso(payload["estado_proceso"])
            except ValueError:
                session.close()
                validos = [e.value for e in EstadoProceso]
                return {"error": f"Estado invalido. Valores permitidos: {validos}"}

        if "plataforma" in payload:
            p.plataforma = payload["plataforma"]

        if "fecha_postulacion" in payload:
            try:
                p.fecha_postulacion = datetime.fromisoformat(
                    str(payload["fecha_postulacion"]).replace("Z", "+00:00")
                )
            except ValueError:
                session.close()
                return {"error": "Formato de fecha invalido"}

        session.commit()
        session.refresh(p)
        result = _postulacion_to_dict(p)
        session.close()
        return {"postulacion": result}
    except Exception as e:
        return {"error": str(e)}


@router.delete("/{id}")
def delete_postulacion(id: int):
    try:
        session = get_session()
        p = session.query(Postulacion).filter(Postulacion.id == id).first()
        if not p:
            session.close()
            return {"error": "Postulacion no encontrada"}
        session.delete(p)
        session.commit()
        session.close()
        return {"deleted": True, "id": id}
    except Exception as e:
        return {"error": str(e)}
