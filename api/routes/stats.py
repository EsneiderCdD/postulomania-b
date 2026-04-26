from fastapi import APIRouter
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
    check_uniqueness
)

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
        
        return {
            "metrica": "Origen del Proceso",
            "frecuencia": freq,
            "distribucion_porcentaje": dist,
            "moda": mode,
            "ratio_nulos": f"{null_ratio:.2f}%"
        }
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
        
        return {
            "metrica": "Empresa",
            "total_empresas_unicas": int(unique_count),
            "top_10_empresas": top_10,
            "ratio_nulos_empresa": f"{integrity:.2f}%",
            "total_empresas_solo_ingles": len(exclusive_english),
            "empresas_solo_ingles": exclusive_english,
            "analisis_larga_cola": {
                "empresas_con_una_oferta": int(single_offer_count),
                "porcentaje_larga_cola": f"{long_tail_percent:.2f}%"
            }
        }
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
        
        return {
            "metrica": "Tech Stack",
            "total_tecnologias_unicas": int(unique_techs),
            "popularidad_top_15": popularity,
            "promedio_techs_por_oferta": round(float(avg_techs), 2),
            "rango_densidad": {"min": int(min_dens), "max": int(max_dens)},
            "combinaciones_frecuentes": formatted_combos,
            "tecnologias_raras": rare_techs,
            "tendencia_por_origen": trends
        }
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
        
        # Cálculos
        mean_v = calculate_mean(df, 'experiencia_anios')
        median_v = calculate_median(df, 'experiencia_anios')
        levels = classify_experience_levels(df, 'experiencia_anios').to_dict()
        corr_v = calculate_correlation(df, 'experiencia_anios', 'num_techs')
        max_exp, techs_max = get_experience_extremes(df, df_techs)
        entry_rate = calculate_entry_level_rate(df, 'experiencia_anios')
        std_v = calculate_std_dev(df, 'experiencia_anios')
        mode_v = df['experiencia_anios'].mode()[0]
        
        return {
            "metrica": "Experiencia en Años",
            "promedio": round(float(mean_v), 2),
            "mediana": float(median_v),
            "moda": float(mode_v),
            "volatilidad_std": round(float(std_v), 2),
            "tasa_entry_level": f"{entry_rate:.2f}%",
            "distribucion_niveles": levels,
            "correlacion_exp_vs_techs": round(float(corr_v), 4),
            "extremos": {
                "max_anios": max_exp,
                "techs_asociadas": techs_max
            }
        }
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
        
        return {
            "metrica": "Compatibilidad",
            "promedio": round(float(avg_comp), 2),
            "mediana": float(med_comp),
            "top_ofertas_70_plus": int(top_count),
            "desempeno_por_origen": perf,
            "dispersion_std": round(float(std_comp), 2),
            "tasa_descarte_sub_40": f"{bottom_rate:.2f}%",
            "rango_absoluto": {"min": float(min_comp), "max": float(max_comp)}
        }
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
            return {("Con Ingles" if k else "Sin Ingles"): round(float(v), 2) for k, v in d.items() if pd.notna(k)}
        
        return {
            "metrica": "Requerimiento de Ingles",
            "proporcion_general": f"{prop_ingles:.2f}%",
            "impacto_experiencia_anios": format_bool_keys(exp_vs_ingles),
            "carga_tecnica_promedio": format_bool_keys(techs_vs_ingles),
            "impacto_compatibilidad": format_bool_keys(score_vs_ingles),
            "concentracion_por_origen": {k: f"{v:.2f}%" for k, v in concentracion.items()},
            "top_tecnologias_bilingues": top_techs
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/timing")
def get_timing_stats():
    try:
        query = "SELECT id, fecha_publicacion_estimada FROM ofertas"
        df = pd.read_sql(query, engine)
        
        # Convertir a datetime
        df['fecha_publicacion_estimada'] = pd.to_datetime(df['fecha_publicacion_estimada'])
        
        # Cálculos base
        vol_dias = get_time_distribution(df, 'fecha_publicacion_estimada', unit='day_name').to_dict()
        frec_horas = get_time_distribution(df, 'fecha_publicacion_estimada', unit='hour').to_dict()
        
        # Recencia
        ultimas_24 = count_recent_records(df, 'fecha_publicacion_estimada', hours=24)
        ultimas_48 = count_recent_records(df, 'fecha_publicacion_estimada', hours=48)
        
        # Complementariedad (Singularidad)
        max_age = get_oldest_record_age(df, 'fecha_publicacion_estimada')
        peak_day = get_peak_day(df, 'fecha_publicacion_estimada')
        weekend_rate = get_weekend_dropoff_rate(df, 'fecha_publicacion_estimada')
        
        return {
            "metrica": "Fecha de Publicacion Estimada",
            "volumen_por_dia": vol_dias,
            "frecuencia_por_hora": {f"{k:02d}:00": v for k, v in frec_horas.items()},
            "recencia": {
                "ultimas_24h": int(ultimas_24),
                "ultimas_48h": int(ultimas_48)
            },
            "antiguedad_maxima_dias": int(max_age),
            "dia_pico_absoluto": peak_day,
            "fuga_fin_de_semana": f"{weekend_rate:.2f}%"
        }
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
        
        return {
            "metrica": "ID de Oferta (Llave Primaria)",
            "auditoria_integridad": {
                "total_registros_volumen": int(auditoria["Total Registros"]),
                "registros_unicos_unicidad": int(auditoria["Registros Únicos"]),
                "duplicados_detectados": int(auditoria["Duplicados Detectados"]),
                "tasa_duplicidad": f"{auditoria['Tasa de Duplicidad (%)']}%"
            }
        }
    except Exception as e:
        return {"error": str(e)}
