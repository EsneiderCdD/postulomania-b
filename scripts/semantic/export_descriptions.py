"""
Exporta todas las descripciones de ofertas con sus tecnologias detectadas
para auditoria manual del TECH_KEYWORDS / TECH_CATEGORIES.

Uso:
    python scripts/semantic/export_descriptions.py

Output:
    scripts/semantic/descripciones_export.txt
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from database.db import get_session
from database.models import Oferta
from sqlalchemy.orm import joinedload


def export():
    session = get_session()
    try:
        offers = (
            session.query(Oferta)
            .options(joinedload(Oferta.tecnologias))
            .all()
        )

        if not offers:
            print("No hay ofertas en la base de datos.")
            return

        output_dir = os.path.dirname(__file__)
        output_path = os.path.join(output_dir, "descripciones_export.txt")

        lines = []
        for i, o in enumerate(offers, 1):
            techs_detectadas = sorted([t.nombre for t in o.tecnologias])
            lines.append(f"[Oferta {i}/{len(offers)}]")
            lines.append(f"id_oferta: {o.id_oferta}")
            lines.append(f"origen:    {o.origen_proceso}")
            lines.append(f"titulo:    {o.titulo or '-'}")
            lines.append(f"detectadas: {', '.join(techs_detectadas) if techs_detectadas else '(ninguna)'}")
            lines.append(f"descripcion:")
            lines.append(o.descripcion or "(sin descripcion)")
            lines.append("---")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"Exportado: {len(offers)} ofertas -> {output_path}")

    except Exception as e:
        print(f"Error: {e}")
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    export()
