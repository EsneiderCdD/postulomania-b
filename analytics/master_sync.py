import pandas as pd
from correlation.correlator import apply_correlation
from analytics.processes.persistence import save_to_db

def sync_to_master(new_df, slug, keyword):
    """Sincroniza ofertas a PostgreSQL con deduplicación por id_oferta."""
    if new_df is None or new_df.empty:
        return
    
    df_temp = new_df.copy()
    df_temp["origen_proceso"] = slug
    df_temp["keyword"] = keyword
    
    df_temp = apply_correlation(df_temp)
    
    save_to_db(df_temp)
    
    return df_temp
