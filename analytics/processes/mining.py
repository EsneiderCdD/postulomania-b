import pandas as pd
import re
import numpy as np
from analytics.processes.parsing import (
    parse_experience, 
    parse_tech_stack, 
    parse_seniority,
    parse_contract_type,
    parse_english,
    parse_education
)

def extract_experience(df: pd.DataFrame) -> pd.DataFrame:
    if 'descripcion' in df.columns:
        df['experiencia_anios'] = df['descripcion'].apply(parse_experience)
    return df

def extract_tech_stack(df: pd.DataFrame) -> pd.DataFrame:
    """Extrae tecnologías de la descripción."""
    if 'descripcion' in df.columns:
        df['tech_stack'] = df['descripcion'].apply(parse_tech_stack)
    return df

def extract_seniority(df: pd.DataFrame) -> pd.DataFrame:
    """Categoriza el nivel de experiencia (seniority) de la oferta."""
    if 'descripcion' in df.columns:
        df['seniority'] = df['descripcion'].apply(parse_seniority)
    return df

def extract_contract_type(df: pd.DataFrame) -> pd.DataFrame:
    """Identifica el tipo de contrato legal."""
    if 'descripcion' in df.columns:
        df['tipo_contrato'] = df['descripcion'].apply(parse_contract_type)
    return df

def extract_english(df: pd.DataFrame) -> pd.DataFrame:
    """Identifica si la oferta requiere inglés."""
    if 'descripcion' in df.columns:
        df['requiere_ingles'] = df['descripcion'].apply(parse_english)
    return df

def extract_education(df: pd.DataFrame) -> pd.DataFrame:
    """Identifica el nivel educativo requerido."""
    if 'descripcion' in df.columns:
        df['educacion_requerida'] = df['descripcion'].apply(parse_education)
    return df
