import pandas as pd
from analytics.processes import cleaning, normalization, mining

def run_pipeline(data: list, keyword_slug: str = "dds"):
    """Procesa y enriquece los datos de ofertas en memoria."""
    if not data:
        return None
    
    df = pd.DataFrame(data)
    
    if not df.empty:
        df = cleaning.sanitize_text(df)
        df = cleaning.handle_nulls(df)
        df = cleaning.deduplicate(df)
        
        df = normalization.normalize_locations(df)
        df = normalization.normalize_companies(df)
        df = normalization.normalize_titles(df)
        df = normalization.normalize_ratings(df)
        df = normalization.normalize_dates(df)
        
        df = mining.extract_experience(df)
        df = mining.extract_tech_stack(df)
        df = mining.extract_contract_type(df)
        df = mining.extract_english(df)
        df = mining.extract_education(df)
    
    return df

