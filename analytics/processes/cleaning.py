import pandas as pd
import numpy as np
import unicodedata
import re
from analytics.data.patterns import CLEAN_SPACES_PATTERN

def handle_nulls(df: pd.DataFrame) -> pd.DataFrame:
    return df.replace('-', np.nan)

def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    if 'id_oferta' in df.columns:
        return df.drop_duplicates(subset=['id_oferta'])
    return df

def parse_clean_text(val):
    """Realiza una higienización profunda de texto."""
    if not isinstance(val, str) or pd.isna(val):
        return val
    text = unicodedata.normalize('NFKC', val)
    text = text.replace('\xa0', ' ')
    text = CLEAN_SPACES_PATTERN.sub(' ', text)
    return text.strip()

def sanitize_text(df: pd.DataFrame) -> pd.DataFrame:
    """Higienización profunda de todas las columnas de texto."""
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(parse_clean_text)
    return df
