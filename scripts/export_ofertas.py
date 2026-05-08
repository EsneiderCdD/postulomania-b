import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_session
from database.models import Oferta

OUTPUT_PATH = os.path.join("data", "ofertas_descripciones.txt")

def exportar():
    session = get_session()
    try:
        offers = session.query(Oferta).order_by(Oferta.id).all()
        if not offers:
            print("No hay ofertas en la BD.")
            return

        lines = []
        lines.append(f"Total ofertas: {len(offers)}")
        lines.append("")

        for i, o in enumerate(offers, 1):
            desc = o.descripcion or "(sin descripcion)"
            lines.append(f"--- OFERTA #{i}  |  id_oferta={o.id_oferta}  |  titulo={o.titulo or 'N/A'} ---")
            lines.append(desc)
            lines.append("")

        content = "\n".join(lines)
        os.makedirs("data", exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Exportado: {OUTPUT_PATH}")
        print(f"  {len(offers)} ofertas escritas.")

    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    exportar()
