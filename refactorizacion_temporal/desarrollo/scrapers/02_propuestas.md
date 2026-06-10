# Propuestas — Arquitectura de scrapers

| ✓ | Tema | Subtema | Qué requiere | Preguntas abiertas |
|---|------|---------|-------------|---------------------|
| [ ] | Estructura de carpetas | Ubicación de cada scraper | Definir `scrapers/<fuente>/` como estándar. Cada fuente replica la estructura interna de Computrabajo (main.py + processes/). | ¿Hay excepciones donde un scraper no deba seguir este patrón? |
| [ ] | | Carpeta `processes/` por scraper | Estandarizar que todo scraper tenga al menos `search.py` y `extraction.py`. `popups.py` y `persistence.py` según necesidad. | ¿Conviene un `__init__.py` en `processes/` aunque no se use como paquete? |
| [ ] | Contrato del scraper | Columnas obligatorias | Definir el conjunto mínimo que todo scraper debe entregar al pipeline: `id_oferta`, `titulo`, `enlace`, `descripcion`, `empresa`. | ¿Debe ser `empresa` obligatoria? Hay ofertas anónimas. |
| [ ] | | Columnas opcionales | `ubicacion`, `salario`, `valoracion`, `modalidad`, `tiempo`. El pipeline las procesa si existen, las ignora si no. | ¿Cómo manejar campos con nombre distinto según la fuente (ej. `location` vs `ubicacion`)? |
| [ ] | | Formato de salida | Definir si el scraper entrega `list[dict]` o `pd.DataFrame`. Hoy Computrabajo entrega `list[dict]` y el pipeline lo convierte. | |
| [ ] | | Metadatos de origen | Cada registro debe incluir `origen_proceso` (slug de la fuente) y `keyword` (término de búsqueda). | |
| [ ] | Testing vs. automatización | Scripts de prueba visual | Cada scraper debe tener sus propios scripts de test con navegador abierto (headless=False). Propuesta: `scrapers/<fuente>/tests/`. | ¿Nomenclatura: `test_<busqueda>.py`? ¿Otra? |
| [ ] | | Scripts headless (producción) | El scheduler invoca al scraper en modo headless=True. No necesita scripts separados por búsqueda. | ¿El scheduler llama a `main.py` de cada fuente o a una función común? |
| [ ] | | Carpeta `scripts/` post-limpieza | Debe quedar solo con herramientas transversales: scheduler, reset_db, migraciones cumplidas. | ¿Las migraciones (`migrate_*.py`) se borran o se archivan? |
| [ ] | Scheduler | Generalización multi-fuente | El scheduler debe iterar fuentes y búsquedas desde configuración, no hardcodeadas. | ¿El estado por fuente va en un solo JSON o en archivos separados? |
| [ ] | | Configuración por fuente | Cada fuente define su lista de búsquedas, frecuencia y ubicación. Propuesta: array `sources` en `scheduler_state.json`. | ¿Frecuencia global o por fuente? ¿Jitter global o por fuente? |
| [ ] | | Ciclo del scheduler | Hoy: scraper → pipeline → sync → refresh scores. Este ciclo debe ser idéntico para toda fuente. | ¿Se corre todo el ciclo para cada fuente o se agrupa (todos los scrapers primero, luego un solo refresh)? |
