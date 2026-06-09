"""Migra puntajes desde user_profile.json a la tabla perfil_tecnologias."""
import json
import os
from dotenv import load_dotenv
load_dotenv()

from database.db import engine, Base, get_session
from database.models import PerfilTecnologia, Tecnologia

PROFILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "correlation", "profile", "user_profile.json"
)


def migrate():
    Base.metadata.create_all(bind=engine)

    if not os.path.exists(PROFILE_PATH):
        print(f"No se encontró {PROFILE_PATH}. Nada que migrar.")
        return

    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        profile = json.load(f)

    tecnico = profile.get("tecnico", {})
    if not tecnico:
        print("user_profile.json sin datos técnicos. Nada que migrar.")
        return

    session = get_session()
    try:
        techs_db = {t.nombre: t.id for t in session.query(Tecnologia).all()}
        creados = 0
        omitidos = 0

        for nombre, score in tecnico.items():
            tid = techs_db.get(nombre)
            if not tid:
                print(f"  Omitida (no en DB): {nombre}")
                omitidos += 1
                continue

            existe = (
                session.query(PerfilTecnologia)
                .filter(PerfilTecnologia.tecnologia_id == tid)
                .first()
            )
            if existe:
                print(f"  Ya existe, actualizando: {nombre} -> {score}")
                existe.score = score
            else:
                session.add(PerfilTecnologia(tecnologia_id=tid, score=score))
                creados += 1

        session.commit()
        print(f"Migración completada: {creados} creados, {omitidos} omitidos (no en DB).")
    except Exception as e:
        session.rollback()
        print(f"Error en migración: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    migrate()
