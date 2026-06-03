from datetime import datetime, timezone

from fastapi import APIRouter, Query
import pandas as pd
import numpy as np
from database.db import engine

router = APIRouter(
    prefix="/mapa",
    tags=["mapa"]
)

ESTADO_PRIORITY = {
    "Finalista": 5,
    "HdV Vista": 4,
    "Postulado": 3,
    "Proceso finalizado": 2,
}


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
            e.en_seguimiento,
            COUNT(o.id) AS total_ofertas
        FROM empresas e
        LEFT JOIN ofertas o ON o.empresa_id = e.id
        WHERE ((e.lat IS NOT NULL AND e.lng IS NOT NULL) OR e.en_seguimiento = TRUE)
        """
        params = {}
        if departamento:
            query_empresas += " AND e.departamento = %(dep)s"
            params["dep"] = departamento
        query_empresas += " GROUP BY e.id, e.nombre, e.website, e.direccion, e.municipio, e.departamento, e.lat, e.lng, e.en_seguimiento ORDER BY e.nombre"
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
                "lat": float(row["lat"]) if pd.notna(row["lat"]) else None,
                "lng": float(row["lng"]) if pd.notna(row["lng"]) else None,
                "total_ofertas": int(row["total_ofertas"]),
                "ofertas": ofertas_por_empresa.get(eid, []),
                "en_seguimiento": bool(row["en_seguimiento"]) if pd.notna(row["en_seguimiento"]) else False,
            })

        return {
            "total": len(empresas),
            "empresas": empresas,
        }

    except Exception as e:
        return {"error": str(e)}


@router.get("/empresas-seguimiento")
def get_mapa_empresas_seguimiento(departamento: str = Query(None)):
    """Devuelve empresas con coordenadas, ofertas anidadas y campos de
    clasificacion visual (estado_estrella, opacidad, compatibilidad_max,
    dias_ultima_accion) para el mapa de seguimientos."""
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
            e.en_seguimiento,
            e.estado_visual,
            COUNT(o.id) AS total_ofertas
        FROM empresas e
        LEFT JOIN ofertas o ON o.empresa_id = e.id
        WHERE ((e.lat IS NOT NULL AND e.lng IS NOT NULL) OR e.en_seguimiento = TRUE)
        """
        params = {}
        if departamento:
            query_empresas += " AND e.departamento = %(dep)s"
            params["dep"] = departamento
        query_empresas += " GROUP BY e.id ORDER BY e.nombre"
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
            o.fecha_extraccion,
            o.experiencia_anios,
            o.requiere_ingles,
            o.origen_proceso,
            ARRAY_AGG(t.nombre ORDER BY t.nombre) AS tecnologias
        FROM ofertas o
        LEFT JOIN ofertas_tecnologias ot ON ot.oferta_id = o.id
        LEFT JOIN tecnologias t ON ot.tecnologia_id = t.id
        WHERE o.empresa_id IN %(ids)s
        GROUP BY o.id
        ORDER BY o.fecha_publicacion_estimada DESC
        """
        df_ofertas = pd.read_sql(query_ofertas, engine, params={"ids": empresa_ids})

        query_postulaciones = """
        SELECT
            o.empresa_id,
            p.estado_proceso,
            p.fecha_postulacion
        FROM ofertas o
        INNER JOIN postulaciones p ON p.oferta_id = o.id
        WHERE o.empresa_id IN %(ids)s
        """
        df_postulaciones = pd.read_sql(query_postulaciones, engine, params={"ids": empresa_ids})

        query_compat = """
        SELECT
            o.empresa_id,
            MAX(c.score) AS max_score
        FROM ofertas o
        INNER JOIN compatibilidades c ON c.oferta_id = o.id
        WHERE o.empresa_id IN %(ids)s
        GROUP BY o.empresa_id
        """
        df_compat = pd.read_sql(query_compat, engine, params={"ids": empresa_ids})

        compat_map = {}
        for _, row in df_compat.iterrows():
            compat_map[int(row["empresa_id"])] = round(float(row["max_score"]), 4)

        postus_por_empresa = {}
        for _, row in df_postulaciones.iterrows():
            eid = int(row["empresa_id"])
            postus_por_empresa.setdefault(eid, []).append({
                "estado": str(row["estado_proceso"]),
                "fecha": row["fecha_postulacion"],
            })

        now = datetime.now(timezone.utc)

        def _mejor_estado(postus, estado_visual):
            if estado_visual:
                return estado_visual
            if not postus:
                return "frio"
            best = "frio"
            best_prio = 0
            for p in postus:
                prio = ESTADO_PRIORITY.get(p["estado"], 0)
                if prio > best_prio:
                    best_prio = prio
                    best = "postulado" if p["estado"] == "Postulado" else \
                           "hdv_vista" if p["estado"] == "HdV Vista" else \
                           "finalista" if p["estado"] == "Finalista" else \
                           "finalizado"
            return best

        def _opacidad(estado, fecha_max_extraccion, postus):
            if estado == "frio":
                if fecha_max_extraccion and pd.notna(fecha_max_extraccion):
                    dias = max(0, (now - pd.Timestamp(fecha_max_extraccion).tz_localize("UTC")).days)
                    return round(max(0.10, 1.0 - dias / 30.0), 4)
                return 0.50
            if estado == "postulado":
                fechas = [
                    p["fecha"] for p in postus
                    if p["fecha"] and pd.notna(p["fecha"]) and p["estado"] == "Postulado"
                ]
                if fechas:
                    dias = max(0, (now - pd.Timestamp(min(fechas)).tz_localize("UTC")).days)
                    return round(max(0.20, 1.0 - dias / 15.0), 4)
                return 0.50
            if estado in ("hdv_vista", "finalista"):
                return 1.0
            if estado == "finalizado":
                fechas = [
                    p["fecha"] for p in postus
                    if p["fecha"] and pd.notna(p["fecha"]) and p["estado"] == "Proceso finalizado"
                ]
                if fechas:
                    dias = max(0, (now - pd.Timestamp(max(fechas)).tz_localize("UTC")).days)
                    return round(max(0.05, 1.0 - dias / 30.0), 4)
                return 0.06
            return 0.50

        def _dias_ultima_accion(fecha_max_extraccion, postus):
            fechas = []
            if fecha_max_extraccion and pd.notna(fecha_max_extraccion):
                fechas.append(pd.Timestamp(fecha_max_extraccion).tz_localize("UTC"))
            for p in postus:
                if p["fecha"] and pd.notna(p["fecha"]):
                    fechas.append(pd.Timestamp(p["fecha"]).tz_localize("UTC"))
            if not fechas:
                return None
            return max(0, (now - max(fechas)).days)

        ofertas_por_empresa = {}
        extraccion_por_empresa = {}
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
                "fecha_publicacion_estimada": str(row["fecha_publicacion_estimada"]) if pd.notna(row["fecha_publicacion_estimada"]) else None,
                "experiencia_anios": float(row["experiencia_anios"]) if pd.notna(row["experiencia_anios"]) and str(row["experiencia_anios"]) != "nan" else None,
                "requiere_ingles": bool(row["requiere_ingles"]) if str(row["requiere_ingles"]) != "nan" else None,
                "tecnologias": techs,
            }
            ofertas_por_empresa.setdefault(eid, []).append(oferta)

            fe = row["fecha_extraccion"]
            if pd.notna(fe):
                cur = extraccion_por_empresa.get(eid)
                if cur is None or pd.Timestamp(fe) > pd.Timestamp(cur):
                    extraccion_por_empresa[eid] = fe

        empresas = []
        for _, row in df_empresas.iterrows():
            eid = int(row["id"])
            postus = postus_por_empresa.get(eid, [])
            fe_max = extraccion_por_empresa.get(eid)
            estado_visual_val = str(row["estado_visual"]) if pd.notna(row["estado_visual"]) else None

            estado = _mejor_estado(postus, estado_visual_val)
            opc = 1.0 if estado_visual_val else _opacidad(estado, fe_max, postus)
            dias_acc = _dias_ultima_accion(fe_max, postus)
            compat_max = compat_map.get(eid)

            empresas.append({
                "id": eid,
                "nombre": row["nombre"],
                "website": row["website"],
                "direccion": row["direccion"],
                "municipio": row["municipio"],
                "departamento": row["departamento"],
                "lat": float(row["lat"]) if pd.notna(row["lat"]) else None,
                "lng": float(row["lng"]) if pd.notna(row["lng"]) else None,
                "total_ofertas": int(row["total_ofertas"]),
                "ofertas": ofertas_por_empresa.get(eid, []),
                "en_seguimiento": bool(row["en_seguimiento"]) if pd.notna(row["en_seguimiento"]) else False,
                "estado_visual": estado_visual_val,
                "estado_estrella": estado,
                "opacidad": opc,
                "compatibilidad_max": compat_max,
                "dias_ultima_accion": dias_acc,
            })

        return {
            "total": len(empresas),
            "empresas": empresas,
        }

    except Exception as e:
        return {"error": str(e)}
