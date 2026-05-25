from fastapi import APIRouter, Query
import pandas as pd
from database.db import engine

router = APIRouter(
    prefix="/mapa",
    tags=["mapa"]
)


@router.get("/ofertas")
def get_mapa_ofertas(departamento: str = Query(None)):
    """Devuelve ofertas con coordenadas para mostrar en mapa Leaflet."""
    try:
        query = """
        SELECT
            o.id_oferta,
            o.titulo,
            o.enlace,
            e.municipio,
            e.departamento,
            e.nombre AS empresa,
            e.website AS empresa_website,
            e.direccion,
            e.lat,
            e.lng
        FROM ofertas o
        JOIN empresas e ON o.empresa_id = e.id
        WHERE e.lat IS NOT NULL
        """
        params = {}
        if departamento:
            query += " AND o.departamento = %(dep)s"
            params["dep"] = departamento
        query += " ORDER BY o.fecha_publicacion_estimada DESC"
        df = pd.read_sql(query, engine, params=params if params else None)

        if df.empty:
            return {"total": 0, "ofertas": []}

        puntos = []
        for _, row in df.iterrows():
            puntos.append({
                "id_oferta": row["id_oferta"],
                "titulo": row["titulo"],
                "enlace": row["enlace"],
                "empresa": row["empresa"],
                "empresa_website": row["empresa_website"],
                "municipio": row["municipio"],
                "departamento": row["departamento"],
                "direccion": row["direccion"],
                "lat": float(row["lat"]),
                "lng": float(row["lng"]),
            })

        return {
            "total": len(puntos),
            "ofertas": puntos,
        }

    except Exception as e:
        return {"error": str(e)}


@router.get("/empresas")
def get_mapa_empresas(departamento: str = Query(None)):
    """Devuelve empresas con coordenadas y sus ofertas anidadas, para mapa Leaflet."""
    try:
        query_empresas = """
        SELECT
            e.id,
            e.nombre,
            e.website,
            e.direccion,
            e.municipio,
            e.departamento,
            e.lat,
            e.lng,
            COUNT(o.id) AS total_ofertas
        FROM empresas e
        LEFT JOIN ofertas o ON o.empresa_id = e.id
        WHERE 1=1
        """
        params = {}
        if departamento:
            query_empresas += " AND e.departamento = %(dep)s"
            params["dep"] = departamento
        query_empresas += " AND e.lat IS NOT NULL AND e.lng IS NOT NULL"
        query_empresas += " GROUP BY e.id, e.nombre, e.website, e.direccion, e.municipio, e.departamento, e.lat, e.lng ORDER BY e.nombre"
        df_empresas = pd.read_sql(query_empresas, engine, params=params if params else None)

        if df_empresas.empty:
            return {"total": 0, "empresas": []}

        empresa_ids = tuple(int(i) for i in df_empresas["id"].tolist())

        query_ofertas = """
        SELECT
            o.empresa_id,
            o.id_oferta,
            o.titulo,
            o.enlace,
            o.fecha_publicacion_estimada,
            o.experiencia_anios,
            o.requiere_ingles,
            o.origen_proceso,
            ARRAY_AGG(t.nombre ORDER BY t.nombre) AS tecnologias
        FROM ofertas o
        LEFT JOIN ofertas_tecnologias ot ON ot.oferta_id = o.id
        LEFT JOIN tecnologias t ON ot.tecnologia_id = t.id
        WHERE o.empresa_id IN %(ids)s
        GROUP BY o.id, o.empresa_id, o.id_oferta, o.titulo, o.enlace,
                 o.fecha_publicacion_estimada, o.experiencia_anios, o.requiere_ingles, o.origen_proceso
        ORDER BY o.fecha_publicacion_estimada DESC
        """
        df_ofertas = pd.read_sql(query_ofertas, engine, params={"ids": empresa_ids})

        ofertas_por_empresa = {}
        for _, row in df_ofertas.iterrows():
            eid = int(row["empresa_id"])
            techs = row["tecnologias"]
            if techs and isinstance(techs, list):
                techs = [t for t in techs if t]
            else:
                techs = []
            oferta = {
                "id_oferta": row["id_oferta"],
                "titulo": row["titulo"],
                "enlace": row["enlace"],
                "fecha_publicacion_estimada": str(row["fecha_publicacion_estimada"]) if row["fecha_publicacion_estimada"] else None,
                "experiencia_anios": float(row["experiencia_anios"]) if row["experiencia_anios"] and str(row["experiencia_anios"]) != "nan" else None,
                "requiere_ingles": bool(row["requiere_ingles"]) if str(row["requiere_ingles"]) != "nan" else None,
                "tecnologias": techs,
            }
            ofertas_por_empresa.setdefault(eid, []).append(oferta)

        empresas = []
        for _, row in df_empresas.iterrows():
            eid = int(row["id"])
            empresas.append({
                "id": eid,
                "nombre": row["nombre"],
                "website": row["website"],
                "direccion": row["direccion"],
                "municipio": row["municipio"],
                "departamento": row["departamento"],
                "lat": float(row["lat"]),
                "lng": float(row["lng"]),
                "total_ofertas": int(row["total_ofertas"]),
                "ofertas": ofertas_por_empresa.get(eid, []),
            })

        return {
            "total": len(empresas),
            "empresas": empresas,
        }

    except Exception as e:
        return {"error": str(e)}
