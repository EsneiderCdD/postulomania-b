import pandas as pd
import re
import numpy as np
import unicodedata
from datetime import datetime, timedelta
from analytics.data.patterns import (
    EXP_PATTERN, 
    CONTRACT_PATTERNS, 
    ENGLISH_PATTERN, 
    EDUCATION_PATTERNS,
    COMPANY_SUFFIXES_PATTERN,
    CLEAN_SPACES_PATTERN,
    AUTHORIZED_JOB_TITLES,
    DIGITS_ONLY_PATTERN,
    PARENTHESES_CONTENT_PATTERN,
    DATE_MINUTES_PATTERN,
    DATE_HOURS_PATTERN,
    DATE_DAYS_PATTERN
)
from analytics.data.tech_registry import TECH_KEYWORDS

# Pre-compilación de patrones 
COMPILED_TECHS = {
    tech: [re.compile(p, re.IGNORECASE) for p in patterns]
    for tech, patterns in TECH_KEYWORDS.items()
}

def parse_tech_stack(text):
    """Identifica tecnologías en el texto usando patrones pre-compilados."""
    if pd.isna(text): 
        return []
    
    text_str = str(text)
    found = []
    
    for tech, compiled_patterns in COMPILED_TECHS.items():
        for pattern in compiled_patterns:
            if pattern.search(text_str):
                found.append(tech)
                break
    return found

def parse_company_name(text):
    """Limpia sufijos legales de los nombres de empresa."""
    if pd.isna(text): 
        return text
    clean = COMPANY_SUFFIXES_PATTERN.sub('', str(text))
    clean = clean.strip().rstrip('.').title()
    clean = unicodedata.normalize('NFKD', clean).encode('ascii', 'ignore').decode()
    return clean

def parse_job_title(text):
    """Categoriza el cargo basado en palabras clave."""
    if pd.isna(text): 
        return "No especificado"
    clean_text = str(text).lower()
    
    for keyword in AUTHORIZED_JOB_TITLES:
        if keyword.lower() in clean_text:
            return keyword
            
    return "Otros"

def parse_location_text(val):
    """Limpia redundancias en una cadena de ubicación separada por comas."""
    if pd.isna(val): 
        return val
    parts = [p.strip() for p in str(val).split(',')]
    unique_parts = []
    for p in parts:
        if p and p not in unique_parts:
            unique_parts.append(p)
    return ", ".join(unique_parts)

def parse_contract_type(text):
    """Identifica el tipo de contrato legal."""
    if pd.isna(text): 
        return "No especificado"
    
    text_str = str(text)
    for contract, pattern in CONTRACT_PATTERNS.items():
        if pattern.search(text_str):
            return contract
    return "No especificado"

def parse_english(text):
    """Retorna True si menciona requerimiento de inglés."""
    if pd.isna(text): 
        return False
    return bool(ENGLISH_PATTERN.search(str(text)))

def parse_education(text):
    """Identifica el nivel educativo requerido."""
    if pd.isna(text): 
        return "No especificado"
    
    text_str = str(text)
    for edu, pattern in EDUCATION_PATTERNS.items():
        if pattern.search(text_str):
            return edu
    return "No especificado"

def parse_experience(text):
    """
    Convierte el tiempo en float y hace la conversion de (meses/años).
    Valida rango 0-15 años y prefiere matches con contexto de 'experiencia'.
    """
    if pd.isna(text): 
        return np.nan

    text_str = str(text)
    first_valid = None

    for match in EXP_PATTERN.finditer(text_str):
        min_val = float(match.group(1))
        max_val = float(match.group(2)) if match.group(2) else None
        unidad = match.group(3)

        if max_val is not None:
            valor = round((min_val + max_val) / 2, 2)
        else:
            valor = min_val

        years = round(valor / 12, 2) if 'mes' in unidad else valor

        if years > 15:
            continue

        start = max(0, match.start() - 60)
        end = min(len(text_str), match.end() + 60)
        context = text_str[start:end].lower()

        if 'experiencia' in context:
            return years

        if first_valid is None:
            first_valid = years

    return first_valid if first_valid is not None else np.nan

def parse_salary_amount(val):
    """Extrae el monto numérico de una cadena de salario."""
    if pd.isna(val) or val == 'NaN': 
        return np.nan
    digits = DIGITS_ONLY_PATTERN.sub('', str(val))
    if not digits: 
        return np.nan
    if digits.endswith('00') and len(digits) > 2:
        digits = digits[:-2]
    return float(digits)

def parse_salary_period(text):
    """Extrae el periodo de pago del texto de salario."""
    if pd.isna(text): 
        return np.nan
    match = PARENTHESES_CONTENT_PATTERN.search(str(text))
    return match.group(1) if match else np.nan

def parse_rating_text(val):
    """Convierte valoraciones de texto (con coma) a flotantes."""
    if pd.isna(val) or str(val) == '-': 
        return np.nan
    try:
        return float(str(val).replace(',', '.'))
    except (ValueError, TypeError):
        return np.nan

def parse_relative_date(rel_time, base_date):
    """Convierte tiempos relativos en fechas absolutas."""
    if pd.isna(rel_time): 
        return np.nan
    text = str(rel_time).lower()
    
    # 1. Caso: Minutos
    match_min = DATE_MINUTES_PATTERN.search(text)
    if match_min:
        delta = int(match_min.group(1))
        return (base_date - timedelta(minutes=delta)).strftime('%Y-%m-%d %H:%M')
        
    # 2. Caso: Horas
    match_h = DATE_HOURS_PATTERN.search(text)
    if match_h:
        delta = int(match_h.group(1))
        return (base_date - timedelta(hours=delta)).strftime('%Y-%m-%d %H:%M')
        
    # 3. Caso: Ayer
    if 'ayer' in text:
        return (base_date - timedelta(days=1)).strftime('%Y-%m-%d %H:%M')
        
    # 4. Caso: Días
    match_d = DATE_DAYS_PATTERN.search(text)
    if match_d:
        delta = int(match_d.group(1))
        return (base_date - timedelta(days=delta)).strftime('%Y-%m-%d %H:%M')
        
    # 5. Por defecto: Hoy
    return base_date.strftime('%Y-%m-%d %H:%M')
