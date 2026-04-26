import pandas as pd
from correlation.correlator import apply_correlation
from database.db import get_session
from database.models import Oferta
from analytics.processes.persistence import update_db_scores

def refresh():
    """Recalcula compatibilidad de ofertas en BD con el perfil actual."""
    session = get_session()
    try:
        offers = session.query(Oferta).all()
        if not offers:
            return

        data = [
            {
                "id_oferta": o.id_oferta,
                "titulo": o.titulo,
                "tech_stack": [t.nombre for t in o.tecnologias],
                "experiencia_anios": o.experiencia_anios,
                "requiere_ingles": o.requiere_ingles
            }
            for o in offers
        ]
        
        df = apply_correlation(pd.DataFrame(data))
        update_db_scores(df)

    except Exception as e:
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    refresh()
