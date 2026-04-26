import pandas as pd
import os
import json
from analytics.master_sync import sync_to_master

def bootstrap():
    """
    Carga inicial de datos existentes en las carpetas de analytics 
    hacia la Tabla Maestra Global.
    """
    mappings = [
        {"slug": "dds", "keyword": "Desarrollador de Software", "file": "analytics_2026_04_12.json"},
        {"slug": "fullstack", "keyword": "desarrollador full stack", "file": "analytics_2026_04_12.json"},
        {"slug": "dds_full", "keyword": "Desarrollador de Software", "file": "analytics_2026_04_12.json"},
    ]
    
    print("=== INICIANDO CARGA INICIAL (BOOTSTRAP) DE TABLA MAESTRA ===")
    
    for item in mappings:
        path = os.path.join("analytics", "data", item["slug"], item["file"])
        
        if os.path.exists(path):
            print(f"Procesando: {path}...")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                df = pd.DataFrame(data)
                sync_to_master(df, slug=item["slug"], keyword=item["keyword"])
            except Exception as e:
                print(f"Error procesando {item['slug']}: {e}")
        else:
            print(f"Aviso: No se encontró el archivo para {item['slug']} en {path}")

    print("=== CARGA INICIAL FINALIZADA ===")

if __name__ == "__main__":
    bootstrap()
