from fastapi import APIRouter
import numpy as np
import pandas as pd
from database.db import engine
from mining_stats.metrics import (
    calculate_frequency,
    calculate_distribution,
    calculate_mode,
    calculate_null_ratio,
    get_top_n_companies,
    get_company_integrity,
    get_exclusive_companies,
    get_unique_companies_count,
    get_long_tail_analysis,
    get_tech_counts,
    get_avg_techs_per_offer,
    get_tech_combinations,
    get_rare_techs,
    get_tech_trends_by_origin,
    get_tech_density_range,
    calculate_mean,
    calculate_median,
    classify_experience_levels,
    calculate_correlation,
    get_experience_extremes,
    calculate_std_dev,
    calculate_entry_level_rate,
    count_above_threshold,
    get_performance_by_category,
    get_below_threshold_rate,
    get_absolute_range,
    get_percentage,
    compare_averages,
    get_boolean_concentration_by_category,
    get_top_techs_by_condition,
    get_time_distribution,
    count_recent_records,
    get_oldest_record_age,
    get_peak_day,
    get_weekend_dropoff_rate,
    get_timing_by_category,
    check_uniqueness,
    get_daily_timeline
)

def _json_safe(obj):
    if obj is None:
        return None
    if isinstance(obj, (pd.Timestamp,)):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(obj, float) and np.isnan(obj):
        return None
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj) if not np.isnan(obj) else None
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    return obj


router = APIRouter(
    prefix="/stats",
    tags=["stats"]
)

@router.get("/origen")
def get_origen_stats():
    try:
        df = pd.read_sql("SELECT origen_proceso FROM ofertas", engine)
        freq = calculate_frequency(df, 'origen_proceso').to_dict()
        dist = calculate_distribution(df, 'origen_proceso').to_dict()
        mode = calculate_mode(df, 'origen_proceso')
        null_ratio = calculate_null_ratio(df, 'origen_proceso')
        
        return _json_safe({
            "metrica": "Origen del Proceso",
            "frecuencia": freq,
            "distribucion_porcentaje": dist,
            "moda": mode,
            "ratio_nulos": f"{null_ratio:.2f}%"
        })
    except Exception as e:
        return {"error": str(e)}

@router.get("/empresa")
def get_empresa_stats():
    try:
        query = """
        SELECT e.nombre as empresa, o.requiere_ingles
        FROM ofertas o
        LEFT JOIN empresas e ON o.empresa_id = e.id
        """
        df = pd.read_sql(query, engine)
        
        top_10 = get_top_n_companies(df).to_dict()
        integrity = get_company_integrity(df)
        exclusive_english = get_exclusive_companies(df, 'requiere_ingles')
        unique_count = get_unique_companies_count(df)
        single_offer_count, long_tail_percent = get_long_tail_analysis(df)

        total_ofertas = len(df)
        ofertas_anonimas = int(df['empresa'].isna().sum())
        ratio_anonimas = (ofertas_anonimas / total_ofertas * 100) if total_ofertas > 0 else 0
        
        return _json_safe({
            "metrica": "Empresa",
            "total_empresas_identificadas": int(unique_count),
            "total_ofertas_anonimas": ofertas_anonimas,
            "ratio_ofertas_anonimas": f"{ratio_anonimas:.2f}%",
            "top_10_empresas": top_10,
            "ratio_nulos_empresa": f"{integrity:.2f}%",
            "total_empresas_solo_ingles": len(exclusive_english),
            "empresas_solo_ingles": exclusive_english,
            "analisis_larga_cola": {
                "empresas_identificadas_con_una_oferta": int(single_offer_count),
                "porcentaje_larga_cola_identificadas": f"{long_tail_percent:.2f}%"
            }
        })
    except Exception as e:
        return {"error": str(e)}

@router.get("/tech-stack")
def get_tech_stats():
    try:
        # Consulta con triple JOIN para obtener contexto completo
        query = """
        SELECT ot.oferta_id, t.nombre as tech, o.origen_proceso
        FROM ofertas_tecnologias ot
        JOIN tecnologias t ON ot.tecnologia_id = t.id
        JOIN ofertas o ON ot.oferta_id = o.id
        """
        df_techs = pd.read_sql(query, engine)
        
        popularity = get_tech_counts(df_techs).head(15).to_dict()
        combinations = get_tech_combinations(df_techs)
        avg_techs = get_avg_techs_per_offer(df_techs)
        rare_techs = get_rare_techs(df_techs).to_dict()
        trends = get_tech_trends_by_origin(df_techs)
        unique_techs = df_techs['tech'].nunique()
        min_dens, max_dens = get_tech_density_range(df_techs)
        
        # Formatear combinaciones para JSON
        formatted_combos = {f"{c[0][0]} + {c[0][1]}": c[1] for c in combinations}
        
        return _json_safe({
            "metrica": "Tech Stack",
            "total_tecnologias_unicas": int(unique_techs),
            "popularidad_top_15": popularity,
            "promedio_techs_por_oferta": round(float(avg_techs), 2),
            "rango_densidad": {"min": int(min_dens), "max": int(max_dens)},
            "combinaciones_frecuentes": formatted_combos,
            "tecnologias_raras": rare_techs,
            "tendencia_por_origen": trends
        })
    except Exception as e:
        return {"error": str(e)}

@router.get("/experience")
def get_experience_stats():
    try:
        # 1. Carga de datos base (Experiencia)
        df = pd.read_sql("SELECT id, experiencia_anios FROM ofertas", engine)
        
        # 2. Carga de datos tech para correlación y extremos
        query_techs = """
        SELECT ot.oferta_id, t.nombre as tech
        FROM ofertas_tecnologias ot
        JOIN tecnologias t ON ot.tecnologia_id = t.id
        """
        df_techs = pd.read_sql(query_techs, engine)
        
        # Preparación para correlación
        tech_counts = df_techs.groupby('oferta_id')['tech'].count()
        df['num_techs'] = df['id'].map(tech_counts).fillna(0)

        df = df.dropna(subset=["experiencia_anios"])
        
        # Cálculos
        mean_v = calculate_mean(df, 'experiencia_anios')
        median_v = calculate_median(df, 'experiencia_anios')
        levels = classify_experience_levels(df, 'experiencia_anios').to_dict()
        corr_v = calculate_correlation(df, 'experiencia_anios', 'num_techs')
        max_exp, techs_max = get_experience_extremes(df, df_techs)
        entry_rate = calculate_entry_level_rate(df, 'experiencia_anios')
        std_v = calculate_std_dev(df, 'experiencia_anios')
        mode_v = calculate_mode(df, 'experiencia_anios')
        
        return _json_safe({
            "metrica": "Experiencia en Años",
            "promedio": round(float(mean_v), 2),
            "mediana": float(median_v),
            "moda": float(mode_v) if mode_v is not None else None,
            "volatilidad_std": round(float(std_v), 2),
            "tasa_entry_level": f"{entry_rate:.2f}%",
            "distribucion_niveles": levels,
            "correlacion_exp_vs_techs": round(float(corr_v), 4),
            "extremos": {
                "max_anios": max_exp,
                "techs_asociadas": techs_max
            }
        })
    except Exception as e:
        return {"error": str(e)}

@router.get("/origen-experience")
def get_origen_experience_stats():
    try:
        df = pd.read_sql("SELECT id, experiencia_anios, origen_proceso FROM ofertas", engine)

        df = df.dropna(subset=["experiencia_anios"])

        avg_by_origin = df.groupby("origen_proceso")["experiencia_anios"].mean().round(2).to_dict()
        median_by_origin = df.groupby("origen_proceso")["experiencia_anios"].median().to_dict()
        mode_by_origin = df.groupby("origen_proceso")["experiencia_anios"].apply(lambda x: x.mode()[0] if not x.mode().empty else None).to_dict()

        bins = [0, 1.9, 4.9, 100]
        labels = ["Junior (0-2)", "Middle (2-5)", "Senior (5+)"]
        df["nivel"] = pd.cut(df["experiencia_anios"], bins=bins, labels=labels)

        levels_by_origin = {}
        for origen in df["origen_proceso"].unique():
            subset = df[df["origen_proceso"] == origen]
            levels_by_origin[origen] = subset["nivel"].value_counts().to_dict()

        entry_by_origin = {}
        for origen in df["origen_proceso"].unique():
            subset = df[df["origen_proceso"] == origen]
            entry_by_origin[origen] = f"{(subset['experiencia_anios'] == 0).mean() * 100:.2f}%"

        return _json_safe({
            "metrica": "Experiencia por Origen del Proceso",
            "promedio_por_origen": avg_by_origin,
            "mediana_por_origen": median_by_origin,
            "moda_por_origen": mode_by_origin,
            "distribucion_niveles_por_origen": levels_by_origin,
            "tasa_entry_level_por_origen": entry_by_origin,
        })
    except Exception as e:
        return {"error": str(e)}

@router.get("/compatibility")
def get_compatibility_stats():
    try:
        query = """
        SELECT c.score, o.origen_proceso
        FROM compatibilidades c
        JOIN ofertas o ON c.oferta_id = o.id
        """
        df = pd.read_sql(query, engine)
        
        avg_comp = calculate_mean(df, 'score')
        med_comp = calculate_median(df, 'score')
        top_count = count_above_threshold(df, 'score', 70)
        perf = get_performance_by_category(df, 'origen_proceso', 'score').to_dict()
        std_comp = calculate_std_dev(df, 'score')
        bottom_rate = get_below_threshold_rate(df, 'score', 40)
        min_comp, max_comp = get_absolute_range(df, 'score')
        
        return _json_safe({
            "metrica": "Compatibilidad",
            "promedio": round(float(avg_comp), 2),
            "mediana": float(med_comp),
            "top_ofertas_70_plus": int(top_count),
            "desempeno_por_origen": perf,
            "dispersion_std": round(float(std_comp), 2),
            "tasa_descarte_sub_40": f"{bottom_rate:.2f}%",
            "rango_absoluto": {"min": float(min_comp), "max": float(max_comp)}
        })
    except Exception as e:
        return {"error": str(e)}

@router.get("/english")
def get_english_stats():
    try:
        # Consulta maestra
        query = """
        SELECT 
            o.id, 
            o.requiere_ingles, 
            o.experiencia_anios, 
            o.origen_proceso,
            c.score as compatibilidad
        FROM ofertas o
        LEFT JOIN compatibilidades c ON o.id = c.oferta_id
        """
        df = pd.read_sql(query, engine)
        
        # Tecnologías
        query_techs = """
        SELECT ot.oferta_id, t.nombre as tech
        FROM ofertas_tecnologias ot
        JOIN tecnologias t ON ot.tecnologia_id = t.id
        """
        df_techs = pd.read_sql(query_techs, engine)
        
        # Conteo de techs por oferta
        tech_counts = df_techs.groupby('oferta_id')['tech'].count()
        df['num_techs'] = df['id'].map(tech_counts).fillna(0)
        
        # Validar y limpiar booleanos
        df['requiere_ingles'] = df['requiere_ingles'].fillna(False).astype(bool)
        
        # 1. Proporción General
        prop_ingles = get_percentage(df, 'requiere_ingles', True)
        
        # 2. Impacto en Años de Experiencia
        exp_vs_ingles = compare_averages(df, 'requiere_ingles', 'experiencia_anios').to_dict()
        
        # 3. Top Techs Bilingües
        top_techs = get_top_techs_by_condition(df, df_techs, condition_col='requiere_ingles', condition_value=True, n=10).to_dict()
        
        # 4. Concentración por Origen
        concentracion = get_boolean_concentration_by_category(df, 'origen_proceso', 'requiere_ingles').to_dict()
        
        # 5. Brecha de Carga Técnica
        techs_vs_ingles = compare_averages(df, 'requiere_ingles', 'num_techs').to_dict()
        
        # 6. Match Profile (Impacto en Compatibilidad)
        score_vs_ingles = compare_averages(df, 'requiere_ingles', 'compatibilidad').to_dict()
        
        # Formatear claves booleanas a strings legibles para JSON
        def format_bool_keys(d):
            result = {}
            for k, v in d.items():
                key = "Con Ingles" if k else "Sin Ingles"
                result[key] = round(float(v), 2) if pd.notna(v) else 0.0
            return result
        
        return _json_safe({
            "metrica": "Requerimiento de Ingles",
            "proporcion_general": f"{prop_ingles:.2f}%",
            "impacto_experiencia_anios": format_bool_keys(exp_vs_ingles),
            "carga_tecnica_promedio": format_bool_keys(techs_vs_ingles),
            "impacto_compatibilidad": format_bool_keys(score_vs_ingles),
            "concentracion_por_origen": {k: f"{v:.2f}%" for k, v in concentracion.items()},
            "top_tecnologias_bilingues": top_techs
        })
    except Exception as e:
        return {"error": str(e)}

@router.get("/timing")
def get_timing_stats():
    try:
        query = "SELECT id, fecha_publicacion_estimada FROM ofertas"
        df = pd.read_sql(query, engine)
        
        df["fecha_publicacion_estimada"] = pd.to_datetime(df["fecha_publicacion_estimada"], errors="coerce")
        df = df.dropna(subset=["fecha_publicacion_estimada"])

        if df.empty:
            return {
                "metrica": "Fecha de Publicacion Estimada",
                "volumen_por_dia": {},
                "frecuencia_por_hora": {},
                "recencia": {"ultimas_24h": 0, "ultimas_48h": 0},
                "antiguedad_maxima_dias": 0,
                "dia_pico_absoluto": None,
                "fuga_fin_de_semana": "0.00%",
            }

        vol_dias = get_time_distribution(df, "fecha_publicacion_estimada", unit="day_name").to_dict()
        frec_horas = get_time_distribution(df, "fecha_publicacion_estimada", unit="hour").to_dict()

        ultimas_24 = count_recent_records(df, "fecha_publicacion_estimada", hours=24)
        ultimas_48 = count_recent_records(df, "fecha_publicacion_estimada", hours=48)

        max_age = get_oldest_record_age(df, "fecha_publicacion_estimada")
        peak_day = get_peak_day(df, "fecha_publicacion_estimada")
        weekend_rate = get_weekend_dropoff_rate(df, "fecha_publicacion_estimada")

        return _json_safe({
            "metrica": "Fecha de Publicacion Estimada",
            "volumen_por_dia": vol_dias,
            "frecuencia_por_hora": {f"{k:02d}:00": v for k, v in frec_horas.items()},
            "recencia": {
                "ultimas_24h": int(ultimas_24),
                "ultimas_48h": int(ultimas_48),
            },
            "antiguedad_maxima_dias": int(max_age),
            "dia_pico_absoluto": peak_day,
            "fuga_fin_de_semana": f"{weekend_rate:.2f}%",
        })
    except Exception as e:
        return {"error": str(e)}

@router.get("/timeline")
def get_timeline_stats():
    try:
        query_ofertas = "SELECT fecha_extraccion, origen_proceso FROM ofertas WHERE fecha_extraccion IS NOT NULL"
        df_ofertas = pd.read_sql(query_ofertas, engine)
        serie, resumen = get_daily_timeline(df_ofertas, 'fecha_extraccion', 'origen_proceso')

        query_postulaciones = "SELECT fecha_postulacion, plataforma FROM postulaciones WHERE fecha_postulacion IS NOT NULL"
        df_postulaciones = pd.read_sql(query_postulaciones, engine)
        if not df_postulaciones.empty:
            serie_post, resumen_post = get_daily_timeline(df_postulaciones, 'fecha_postulacion', 'plataforma')
        else:
            serie_post, resumen_post = [], {
                "total_historico": 0, "primer_dia": None, "ultimo_dia": None,
                "dias_con_datos": 0, "promedio_diario": 0.0, "mediana_diaria": 0.0
            }

        hoy = pd.Timestamp.now().strftime('%Y-%m-%d')
        ofertas_hoy = next((d["total"] for d in serie if d["fecha"] == hoy), 0)
        postulaciones_hoy = next((d["total"] for d in serie_post if d["fecha"] == hoy), 0)
        tasa_hoy = round((postulaciones_hoy / ofertas_hoy) * 100, 1) if ofertas_hoy > 0 else 0.0

        total_ofertas = resumen["total_historico"]
        total_postulaciones = resumen_post["total_historico"]
        tasa_historico = round((total_postulaciones / total_ofertas) * 100, 1) if total_ofertas > 0 else 0.0

        return _json_safe({
            "metrica": "Línea de tiempo diaria",
            "serie": serie,
            "resumen": resumen,
            "postulaciones": {
                "serie": serie_post,
                "resumen": resumen_post
            },
            "comparativa": {
                "hoy": {
                    "fecha": hoy,
                    "ofertas": ofertas_hoy,
                    "postulaciones": postulaciones_hoy,
                    "tasa_postulacion": tasa_hoy
                },
                "historico": {
                    "total_ofertas": total_ofertas,
                    "total_postulaciones": total_postulaciones,
                    "tasa_postulacion": tasa_historico
                }
            }
        })
    except Exception as e:
        return {"error": str(e)}

@router.get("/title")
def get_title_stats():
    """Endpoint programado para la v.2 (Análisis avanzado de NLP)."""
    return {
        "metrica": "Titulo de la Oferta",
        "nube_de_palabras": [],
        "nota": "trabajar en v.2"
    }

@router.get("/id")
def get_id_stats():
    """Endpoint de auditoría técnica: Integridad de la llave primaria."""
    try:
        query = "SELECT id FROM ofertas"
        df = pd.read_sql(query, engine)
        
        # Ejecutar auditoría
        auditoria = check_uniqueness(df, 'id')
        
        return _json_safe({
            "metrica": "ID de Oferta (Llave Primaria)",
            "auditoria_integridad": {
                "total_registros_volumen": int(auditoria["Total Registros"]),
                "registros_unicos_unicidad": int(auditoria["Registros Únicos"]),
                "duplicados_detectados": int(auditoria["Duplicados Detectados"]),
                "tasa_duplicidad": f"{auditoria['Tasa de Duplicidad (%)']}%"
            }
        })
    except Exception as e:
        return {"error": str(e)}

# ── Capítulo III: endpoints de cruce entre dimensiones ──

@router.get("/origen-timing")
def get_origen_timing_stats():
    try:
        df = pd.read_sql("SELECT origen_proceso, fecha_publicacion_estimada FROM ofertas", engine)
        vol_por_dia, dia_pico, fuga = get_timing_by_category(df, "origen_proceso", "fecha_publicacion_estimada")
        return _json_safe({
            "metrica": "Timing por Origen del Proceso",
            "volumen_por_dia_por_origen": vol_por_dia,
            "dia_pico_por_origen": dia_pico,
            "fuga_finde_por_origen": fuga,
        })
    except Exception as e:
        return {"error": str(e)}

@router.get("/origen-empresa")
def get_origen_empresa_stats():
    try:
        query = """
        SELECT o.origen_proceso, e.nombre as empresa
        FROM ofertas o
        LEFT JOIN empresas e ON o.empresa_id = e.id
        """
        df = pd.read_sql(query, engine)

        unicas = {}
        top_3 = {}
        larga_cola = {}
        anonimas = {}
        for origen in df["origen_proceso"].unique():
            sub = df[df["origen_proceso"] == origen]
            unicas[origen] = int(sub["empresa"].nunique())
            anonimas[origen] = int(sub["empresa"].isna().sum())
            top_3[origen] = sub["empresa"].value_counts().head(3).to_dict()
            counts = sub["empresa"].value_counts()
            single = int((counts == 1).sum())
            total_emp = len(counts)
            larga_cola[origen] = f"{(single / total_emp * 100):.2f}%" if total_emp else "0.00%"

        return _json_safe({
            "metrica": "Empresa por Origen del Proceso",
            "empresas_identificadas_por_origen": unicas,
            "ofertas_anonimas_por_origen": anonimas,
            "top_3_por_origen": top_3,
            "larga_cola_por_origen": larga_cola,
        })
    except Exception as e:
        return {"error": str(e)}

@router.get("/english-timing")
def get_english_timing_stats():
    try:
        df = pd.read_sql("SELECT requiere_ingles, fecha_publicacion_estimada FROM ofertas", engine)
        df["requiere_ingles"] = df["requiere_ingles"].fillna(False).astype(bool)
        vol_raw, pico_raw, fuga_raw = get_timing_by_category(df, "requiere_ingles", "fecha_publicacion_estimada")
        vol_por_dia = {("Con Ingles" if k else "Sin Ingles"): v for k, v in vol_raw.items()}
        dia_pico = {("Con Ingles" if k else "Sin Ingles"): v for k, v in pico_raw.items()}
        fuga = {("Con Ingles" if k else "Sin Ingles"): v for k, v in fuga_raw.items()}
        return _json_safe({
            "metrica": "Timing por Requerimiento de Ingles",
            "volumen_por_dia_por_ingles": vol_por_dia,
            "dia_pico_por_ingles": dia_pico,
            "fuga_finde_por_ingles": fuga,
        })
    except Exception as e:
        return {"error": str(e)}

@router.get("/experience-empresa")
def get_experience_empresa_stats():
    try:
        query = """
        SELECT e.nombre as empresa, o.experiencia_anios
        FROM ofertas o
        LEFT JOIN empresas e ON o.empresa_id = e.id
        """
        df = pd.read_sql(query, engine)
        df = df.dropna(subset=["empresa", "experiencia_anios"])

        if df.empty:
            return {
                "metrica": "Experiencia por Empresa",
                "top_experiencia_empresas": {},
                "nivel_mas_demandado": {},
            }

        exp_by_emp = df.groupby("empresa")["experiencia_anios"].mean().round(2).sort_values(ascending=False)
        top = exp_by_emp.head(10).to_dict()

        bins = [0, 1.9, 4.9, 100]
        labels = ["Junior (0-2)", "Middle (2-5)", "Senior (5+)"]
        df["nivel"] = pd.cut(df["experiencia_anios"], bins=bins, labels=labels)

        nivel_mas_demandado = df["nivel"].value_counts().to_dict()

        return _json_safe({
            "metrica": "Experiencia por Empresa",
            "top_experiencia_empresas": top,
            "nivel_mas_demandado": nivel_mas_demandado,
        })
    except Exception as e:
        return {"error": str(e)}

@router.get("/experience-compatibility")
def get_experience_compatibility_stats():
    try:
        query = """
        SELECT o.experiencia_anios, c.score
        FROM ofertas o
        JOIN compatibilidades c ON o.id = c.oferta_id
        """
        df = pd.read_sql(query, engine)

        df = df.dropna(subset=["experiencia_anios"])

        bins = [0, 1.9, 4.9, 100]
        labels = ["Junior (0-2)", "Middle (2-5)", "Senior (5+)"]
        df["nivel"] = pd.cut(df["experiencia_anios"], bins=bins, labels=labels)

        score_por_nivel = df.groupby("nivel")["score"].mean().round(4).to_dict()
        corr = float(df["experiencia_anios"].corr(df["score"]))
        min_exp, max_exp = float(df["experiencia_anios"].min()), float(df["experiencia_anios"].max())

        return _json_safe({
            "metrica": "Compatibilidad por Nivel de Experiencia",
            "score_por_nivel": score_por_nivel,
            "correlacion_exp_vs_score": round(corr, 4),
            "rango_experiencia_analizado": {"min": min_exp, "max": max_exp},
        })
    except Exception as e:
        return {"error": str(e)}

@router.get("/experience-timing")
def get_experience_timing_stats():
    try:
        df = pd.read_sql("SELECT experiencia_anios, fecha_publicacion_estimada FROM ofertas WHERE fecha_publicacion_estimada IS NOT NULL", engine)
        df["fecha_publicacion_estimada"] = pd.to_datetime(df["fecha_publicacion_estimada"], errors="coerce")
        df = df.dropna(subset=["fecha_publicacion_estimada", "experiencia_anios"])

        if df.empty:
            return {
                "metrica": "Experiencia Promedio por Dia",
                "promedio_exp_por_dia": {},
                "mediana_exp_por_dia": {},
                "dia_con_mas_experiencia_promedio": None,
            }

        df["dia"] = df["fecha_publicacion_estimada"].dt.dayofweek.map(
            lambda d: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][d] if 0 <= d <= 6 else None
        )

        exp_por_dia = {k: float(v) for k, v in df.groupby("dia")["experiencia_anios"].mean().round(2).to_dict().items()}
        mediana_por_dia = {k: float(v) for k, v in df.groupby("dia")["experiencia_anios"].median().to_dict().items()}
        mejor_dia = max(exp_por_dia, key=exp_por_dia.get) if exp_por_dia else None

        return _json_safe({
            "metrica": "Experiencia Promedio por Dia",
            "promedio_exp_por_dia": exp_por_dia,
            "mediana_exp_por_dia": mediana_por_dia,
            "dia_con_mas_experiencia_promedio": mejor_dia,
        })
    except Exception as e:
        return {"error": str(e)}

@router.get("/empresa-compatibility")
def get_empresa_compatibility_stats():
    try:
        query = """
        SELECT e.nombre as empresa, c.score
        FROM ofertas o
        JOIN empresas e ON o.empresa_id = e.id
        JOIN compatibilidades c ON o.id = c.oferta_id
        """
        df = pd.read_sql(query, engine)

        score_por_emp = df.groupby("empresa")["score"].mean().round(4).sort_values(ascending=False)
        top = score_por_emp.head(10).to_dict()
        empresas_sin_match = [e for e, s in score_por_emp.items() if s == 0.0]

        return _json_safe({
            "metrica": "Compatibilidad por Empresa",
            "top_score_empresas": top,
            "empresas_con_match_cero": len(empresas_sin_match),
        })
    except Exception as e:
        return {"error": str(e)}

@router.get("/tech-compatibility")
def get_tech_compatibility_stats():
    try:
        query = """
        SELECT t.nombre as tech, c.score
        FROM ofertas_tecnologias ot
        JOIN tecnologias t ON ot.tecnologia_id = t.id
        JOIN compatibilidades c ON ot.oferta_id = c.oferta_id
        """
        df = pd.read_sql(query, engine)

        score_por_tech = df.groupby("tech")["score"].mean().round(4).sort_values(ascending=False)
        top = score_por_tech.head(15).to_dict()
        bottom = score_por_tech.tail(5).to_dict()

        return _json_safe({
            "metrica": "Compatibilidad por Tecnologia",
            "top_score_tecnologias": top,
            "bottom_score_tecnologias": bottom,
        })
    except Exception as e:
        return {"error": str(e)}


