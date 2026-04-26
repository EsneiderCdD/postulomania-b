import pandas as pd
from datetime import datetime
from analytics.processes.parsing import (
    parse_location_text,
    parse_company_name,
    parse_job_title,
    parse_salary_amount,
    parse_salary_period,
    parse_rating_text,
    parse_relative_date
)

def normalize_locations(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina redundancias en la columna de ubicación."""
    if 'ubicacion' in df.columns:
        df['ubicacion'] = df['ubicacion'].apply(parse_location_text)
    return df

def normalize_companies(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia sufijos legales de los nombres de empresa."""
    if 'empresa' in df.columns:
        df['empresa'] = df['empresa'].apply(parse_company_name)
    return df

def normalize_titles(df: pd.DataFrame) -> pd.DataFrame:
    """Categoriza el cargo de la oferta."""
    if 'titulo' in df.columns:
        df['cargo_normalizado'] = df['titulo'].apply(parse_job_title)
    return df

def normalize_salaries(df: pd.DataFrame) -> pd.DataFrame:
    """Divide el campo salario en monto numérico y periodo."""
    if 'salario' in df.columns:
        df['salario_periodo'] = df['salario'].apply(parse_salary_period)
        df['salario_monto'] = df['salario'].apply(parse_salary_amount)
    return df

def normalize_ratings(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte valoraciones a formato numérico."""
    if 'valoracion' in df.columns:
        df['valoracion'] = df['valoracion'].apply(parse_rating_text)
    return df

def normalize_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte tiempos relativos en fechas absolutas."""
    if 'tiempo' in df.columns:
        ahora = datetime.now()
        df['fecha_extraccion'] = ahora.strftime('%Y-%m-%d %H:%M')
        df['fecha_publicacion_estimada'] = df['tiempo'].apply(parse_relative_date, base_date=ahora)
    return df
