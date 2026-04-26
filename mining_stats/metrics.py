import pandas as pd
import numpy as np

# Origen Proceso

def calculate_frequency(df, column):
    """Calcula frecuencia de registros por categoría en una columna."""
    return df[column].value_counts()

def calculate_distribution(df, column):
    """Calcula el porcentaje de representación de cada categoría."""
    return df[column].value_counts(normalize=True) * 100

def calculate_mode(df, column):
    """Retorna la categoría con mayor cantidad de registros."""
    return df[column].mode()[0]

def calculate_null_ratio(df, column):
    """Calcula la proporción de valores nulos en una columna específica."""
    return df[column].isna().mean() * 100

# Empresas

def get_top_n_companies(df, n=10):
    """Retorna las 10 empresas con mayor cantidad de ofertas publicadas."""
    return df['empresa'].value_counts().head(n)

def get_company_integrity(df):
    """Calcula el porcentaje de ofertas con nombre de empresa no especificado."""
    return df['empresa'].isna().mean() * 100

def get_exclusive_companies(df, condition_col):
    """Retorna la lista de empresas que cumplen EXCLUSIVAMENTE una condición."""
    res = df.groupby('empresa')[condition_col].all()
    return res[res].index.tolist()

def get_unique_companies_count(df):
    """Retorna el número total de empresas únicas."""
    return df['empresa'].nunique()

def get_long_tail_analysis(df):
    """Retorna el número y porcentaje de empresas con una sola oferta."""
    counts = df['empresa'].value_counts()
    single_offer_companies = (counts == 1).sum()
    total_companies = len(counts)
    percent = (single_offer_companies / total_companies) * 100 if total_companies > 0 else 0
    return single_offer_companies, percent

# Tech Stack

def get_tech_counts(df_techs):
    """Retorna el conteo de popularidad de todas las tecnologías."""
    return df_techs['tech'].value_counts()

def get_avg_techs_per_offer(df_techs):
    """Calcula el promedio de tecnologías solicitadas por oferta."""
    return df_techs.groupby('oferta_id')['tech'].count().mean()

def get_tech_combinations(df_techs, n=10):
    """Calcula los pares de tecnologías que más co-ocurren."""
    from itertools import combinations
    from collections import Counter
    
    # Agrupamos por oferta e identificamos combinaciones
    groups = df_techs.groupby('oferta_id')['tech'].apply(list)
    combos = Counter()
    
    for techs in groups:
        if len(techs) > 1:
            combos.update(combinations(sorted(techs), 2))
            
    return combos.most_common(n)

def get_rare_techs(df_techs, threshold_percent=1):
    """Retorna tecnologías que aparecen en menos de un X% de las ofertas totales."""
    total_offers = df_techs['oferta_id'].nunique()
    counts = df_techs['tech'].value_counts()
    ratios = (counts / total_offers) * 100
    return ratios[ratios < threshold_percent]

def get_tech_trends_by_origin(df_techs, n=5):
    """Calcula las N tecnologías más populares por cada origen de proceso."""
    # Agrupamos por origen y para cada grupo sacamos el top N como diccionario
    result = {}
    for origin, group in df_techs.groupby('origen_proceso'):
        result[origin] = group['tech'].value_counts().head(n).to_dict()
    return result

def get_tech_density_range(df_techs):
    """Retorna el mínimo y máximo de tecnologías por oferta."""
    counts = df_techs.groupby('oferta_id')['tech'].count()
    return int(counts.min()), int(counts.max())

# Experiencia en Años

def calculate_mean(df, column):
    """Calcula la media aritmética."""
    return df[column].mean()

def calculate_median(df, column):
    """Calcula la mediana (valor central)."""
    return df[column].median()

def classify_experience_levels(df, column):
    """Clasifica las ofertas por niveles según los años de experiencia."""
    bins = [0, 1.9, 4.9, 100]
    labels = ['Junior (0-2)', 'Middle (2-5)', 'Senior (5+)']
    return pd.cut(df[column], bins=bins, labels=labels).value_counts()

def calculate_correlation(df, col1, col2):
    """Calcula la correlación de Pearson entre dos columnas numéricas."""
    return df[col1].corr(df[col2])

def get_experience_extremes(df, df_techs):
    """Retorna el valor máximo de experiencia y las tecnologías asociadas a esas ofertas."""
    max_exp = df['experiencia_anios'].max()
    # Identificamos los IDs de las ofertas con la experiencia máxima
    ids_max = df[df['experiencia_anios'] == max_exp]['id']
    # Extraemos las tecnologías únicas asociadas a esos IDs
    techs_max = df_techs[df_techs['oferta_id'].isin(ids_max)]['tech'].unique().tolist()
    return float(max_exp), techs_max

def calculate_std_dev(df, column):
    """Calcula la desviación estándar."""
    return df[column].std()

def calculate_entry_level_rate(df, column):
    """Calcula el porcentaje de ofertas con 0 años de experiencia."""
    return (df[column] == 0).mean() * 100

# Compatibilidad

def count_above_threshold(df, column, threshold=0.7):
    """Cuenta cuántos registros superan un umbral específico."""
    return (df[column] >= threshold).sum()

def get_performance_by_category(df, category_col, target_col):
    """Compara el promedio de una métrica (target) agrupada por una categoría."""
    return df.groupby(category_col)[target_col].mean().sort_values(ascending=False)

def get_below_threshold_rate(df, column, threshold=40.0):
    """Calcula el porcentaje de registros por debajo de un umbral (Tasa de Descarte)."""
    return (df[column] < threshold).mean() * 100

def get_absolute_range(df, column):
    """Retorna el valor mínimo y máximo de una columna."""
    return float(df[column].min()), float(df[column].max())

# Requerimiento de Inglés

def get_percentage(df, column, condition_value=True):
    """Calcula el porcentaje de registros que cumplen una condición."""
    return (df[column] == condition_value).mean() * 100

def compare_averages(df, group_col, target_col):
    """Compara el promedio de una métrica cruzada contra una categoría."""
    return df.groupby(group_col)[target_col].mean()

def get_boolean_concentration_by_category(df, category_col, boolean_col):
    """Calcula el porcentaje de True en una columna booleana agrupado por una categoría."""
    return df.groupby(category_col)[boolean_col].mean() * 100

def get_top_techs_by_condition(df, df_techs, condition_col, condition_value=True, n=10):
    """Retorna las tecnologías más frecuentes dadas una condición en la oferta."""
    # Filtramos IDs de ofertas que cumplen la condición
    ids_validos = df[df[condition_col] == condition_value]['id']
    return df_techs[df_techs['oferta_id'].isin(ids_validos)]['tech'].value_counts().head(n)

# Fecha de Publicación (Tiempo)

def get_time_distribution(df, column, unit='day_name'):
    """Retorna la distribución por día de la semana o franja horaria."""
    if unit == 'day_name':
        return df[column].dt.day_name().value_counts()
    elif unit == 'hour':
        return df[column].dt.hour.value_counts().sort_index()

def count_recent_records(df, column, hours=24):
    """Cuenta cuántos registros hay en las últimas X horas."""
    now = pd.Timestamp.now()
    limit = now - pd.Timedelta(hours=hours)
    return (df[column] >= limit).sum()

def get_oldest_record_age(df, column):
    """Retorna la antigüedad en días del registro más viejo."""
    now = pd.Timestamp.now()
    oldest = df[column].min()
    return (now - oldest).days if pd.notnull(oldest) else 0

def get_peak_day(df, column):
    """Calcula el día de la semana con mayor volumen de actividad (Moda temporal)."""
    return df[column].dt.day_name().mode()[0]

def get_weekend_dropoff_rate(df, column):
    """Calcula el porcentaje de registros que ocurren en fin de semana (Sábado/Domingo)."""
    return df[column].dt.dayofweek.isin([5, 6]).mean() * 100

# Títulos (Texto)

def get_word_frequency(df, column, n=20):
    """[V2] Analiza los términos más frecuentes en una columna de texto."""
    return []

# Integridad (IDs)

def check_uniqueness(df, column):
    """Valida la integridad de IDs y detecta duplicados (incluyendo tasa %)."""
    total = len(df)
    unicos = df[column].nunique()
    duplicados = total - unicos
    tasa_duplicidad = (duplicados / total) * 100 if total > 0 else 0
    return {
        "Total Registros": total,
        "Registros Únicos": unicos,
        "Duplicados Detectados": duplicados,
        "Tasa de Duplicidad (%)": round(tasa_duplicidad, 2)
    }
