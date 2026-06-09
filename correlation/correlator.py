import pandas as pd
from database.db import get_session
from database.models import Tecnologia, PerfilTecnologia


def _load_profile() -> dict:
    session = get_session()
    try:
        rows = (
            session.query(Tecnologia.nombre, PerfilTecnologia.score)
            .join(PerfilTecnologia, PerfilTecnologia.tecnologia_id == Tecnologia.id)
            .filter(PerfilTecnologia.score > 0)
            .all()
        )
        tecnico = {nombre: score for nombre, score in rows}
        return {
            "tecnico": tecnico,
            "idiomas": {"ingles": 0.0},
            "experiencia": 0.0,
            "nivel_educativo": 0,
        }
    finally:
        session.close()


def calculate_score(offer, profile):
    """
    Calcula el puntaje de compatibilidad (0.0 a 1.0) entre una oferta y el perfil.
    """
    # 1. AFINIDAD TÉCNICA (Peso: 70%)
    tech_requirements = offer.get('tech_stack', [])
    if not tech_requirements:
        tech_score = 0.5
    else:
        user_scores = []
        for tech in tech_requirements:
            score = profile.get('tecnico', {}).get(tech, 0.0)
            user_scores.append(score)
        tech_score = sum(user_scores) / len(user_scores)

    # 2. FACTOR DE EXPERIENCIA (Peso: 30%)
    req_exp = offer.get('experiencia_anios', 0)
    user_exp = profile.get('experiencia', 0.0)

    if pd.isna(req_exp) or req_exp == 0:
        exp_factor = 1.0
    elif user_exp >= req_exp:
        exp_factor = 1.0
    else:
        exp_factor = user_exp / req_exp

    # 3. PENALIZACIÓN DE INGLÉS (Multiplicador)
    requires_english = offer.get('requiere_ingles', False)
    user_english = profile.get('idiomas', {}).get('ingles', 0.0)

    english_multiplier = 1.0
    if requires_english:
        english_multiplier = user_english

    # 4. FACTOR EDUCACIÓN (Bono/Compensación)
    edu_map = {"Ingeniero": 3, "Tecnólogo": 2, "Técnico": 1, "No especificado": 0}
    req_edu_str = offer.get('educacion_requerida', 'No especificado')
    req_edu = edu_map.get(req_edu_str, 0)
    user_edu = profile.get('nivel_educativo', 0)

    effective_edu = user_edu
    if user_exp >= 5:
        effective_edu += 2
    elif user_exp >= 3:
        effective_edu += 1

    edu_penalty = 1.0
    if effective_edu < req_edu:
        edu_penalty = 0.9

    # CÁLCULO FINAL
    base_score = (tech_score * 0.7) + (exp_factor * 0.3)
    final_score = base_score * english_multiplier * edu_penalty

    return round(final_score, 4)


def apply_correlation(df):
    """
    Carga el perfil desde la base de datos y aplica el cálculo a todo el DataFrame.
    """
    profile = _load_profile()
    if not profile.get("tecnico"):
        print("Advertencia: No hay tecnologías puntuadas en perfil_tecnologias")
    df['compatibilidad'] = df.apply(lambda row: calculate_score(row, profile), axis=1)
    return df
