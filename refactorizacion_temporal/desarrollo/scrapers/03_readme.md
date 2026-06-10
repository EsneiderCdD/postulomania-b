## Estructura de carpetas

Cada scraper vive en `scrapers/<fuente>/`, donde `<fuente>` es el nombre del portal (ej. `computrabajo`).

Internamente sigue una organización por procesos: `main.py` como orquestador y una carpeta `processes/` con funciones especializadas por responsabilidad (búsqueda, extracción, etc.). Este patrón, informalmente llamado _pipeline steps as modules_, mantiene separado cada paso del ciclo del scraper.

Agregar un nuevo portal es replicar esa estructura: crear la carpeta, implementar su `main.py` y los procesos que requiera.
