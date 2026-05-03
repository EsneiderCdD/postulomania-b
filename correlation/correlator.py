import json
import os
import pandas as pd

def calculate_score(offer, profile):
    """
    Calcula el puntaje de compatibilidad (0.0 a 1.0) entre una oferta y el perfil.
    """
    # 1. AFINIDAD TÉCNICA (Peso: 70%)
    tech_requirements = offer.get('tech_stack', [])
    if not tech_requirements:
        # Si la oferta no pide nada específico, afinidad neutral
        tech_score = 0.5
    else:
        user_scores = []
        for tech in tech_requirements:
            # Buscamos la tech en el perfil del usuario (case sensitive coincidente con mining.py)
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
    # Si requiere inglés y el usuario tiene poco, el score baja proporcionalmente
    requires_english = offer.get('requiere_ingles', False)
    user_english = profile.get('idiomas', {}).get('ingles', 0.0)
    
    english_multiplier = 1.0
    if requires_english:
        # Si pide inglés, tu nivel actúa como filtro. 
        # Un 0.3 de inglés reduce el score al 30% de su valor original para esta oferta.
        english_multiplier = user_english

    # 4. FACTOR EDUCACIÓN (Bono/Compensación)
    # 0: Sin, 1: Técnico, 2: Tecnólogo, 3: Ingeniero
    edu_map = {"Ingeniero": 3, "Tecnólogo": 2, "Técnico": 1, "No especificado": 0}
    req_edu_str = offer.get('educacion_requerida', 'No especificado')
    req_edu = edu_map.get(req_edu_str, 0)
    user_edu = profile.get('nivel_educativo', 0)
    
    edu_penalty = 1.0
    if user_edu < req_edu:
        # Penalización leve (10%) por no tener el título
        edu_penalty = 0.9
        
        # COMPENSACIÓN: Si tienes más de 2 años extra de experiencia que lo pedido, ignoramos la falta de título
        exp_diff = user_exp - (0 if pd.isna(req_exp) else req_exp)
        if exp_diff >= 2.0:
            edu_penalty = 1.0

    # CÁLCULO FINAL
    base_score = (tech_score * 0.7) + (exp_factor * 0.3)
    final_score = base_score * english_multiplier * edu_penalty
    
    return round(final_score, 4)

def apply_correlation(df):
    """
    Carga el perfil y aplica el cálculo a todo el DataFrame.
    """
    profile_path = os.path.join("correlation", "profile", "user_profile.json")
    if not os.path.exists(profile_path):
        print("Error: No se encontró user_profile.json")
        return df
        
    with open(profile_path, 'r', encoding='utf-8') as f:
        profile = json.load(f)
        
    df['compatibilidad'] = df.apply(lambda row: calculate_score(row, profile), axis=1)
    return df
