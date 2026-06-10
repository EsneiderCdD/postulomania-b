# Planificación Global

| ✓ | Fase | Tema | Subtema | Qué hay que definir / Hitos |
|---|------|------|---------|-----------------------------|
| [x] | 1 — Definiciones previas | Arquitectura de scrapers | Ubicación | ¿Carpeta por fuente? ¿Estructura interna común? ¿Dónde vive cada scraper nuevo? |
| [~] | | | Contrato del scraper | ¿Qué columnas mínimas entrega un scraper al pipeline? ¿Qué metadatos? |
| [ ] | | | Común vs. específico | ¿Qué lógica comparten todos los scrapers y qué es propio de cada fuente? |
| [ ] | | Pipeline de analytics | Separación scraping / analytics | ¿Dónde termina la extracción y dónde empieza la limpieza? |
| [ ] | | | Reusabilidad | ¿Qué etapas del pipeline son genéricas y cuáles dependen del origen? |
| [ ] | | | Formato de entrada | ¿Qué estructura de datos espera el pipeline? ¿DataFrame con qué columnas? |
| [ ] | | Testing vs. automatización | Scripts visuales | ¿Dónde viven los scripts con navegador abierto? ¿Nomenclatura? |
| [ ] | | | Scripts headless | ¿Dónde viven los scripts del scheduler? ¿Cómo se invocan? |
| [ ] | | | Convivencia o separación | ¿Ambos tipos de script en la misma carpeta o en carpetas distintas? |
| [ ] | | Scheduler | Generalización | ¿Se vuelve genérico para múltiples fuentes o se mantiene acoplado? |
| [ ] | | | Configuración | ¿Cómo se define qué buscar por fuente? ¿Estado y frecuencia por fuente? |
| [ ] | | Convenciones | Nomenclatura | Convención para archivos, carpetas, funciones, clases. |
| [ ] | | | Estilo | Imports, docstrings, typing, comentarios. |
| [ ] | | Base de datos | Modelos actuales | ¿Soportan multi-origen sin cambios? |
| [ ] | | | Longitudes y constraints | ¿Campos VARCHAR suficientes? ¿Índices y constraints pendientes? |
| [ ] | 2 — Auditoría por carpeta | `scrapers/computrabajo/` | `processes/search.py` | ¿Acoplado a Computrabajo? ¿Lógica reutilizable? |
| [ ] | | | `processes/extraction.py` | ¿Selectores CSS genéricos o específicos? ¿Datos extraídos vs. necesarios? |
| [ ] | | | `processes/popups.py` | ¿Propio de Computrabajo o reutilizable? |
| [ ] | | | `processes/persistence.py` | Archivo de persistencia JSON legado. ¿Se borra? |
| [ ] | | | `processes/__init__.py` | ¿Realmente es un paquete? |
| [ ] | | | `main.py` | ¿Orquestador genérico o acoplado? |
| [ ] | | `analytics/` | `pipeline.py` | ¿Columnas asumidas? ¿Acoplado a estructura de Computrabajo? |
| [ ] | | | `processes/cleaning.py` | ¿Depende de columnas específicas? |
| [ ] | | | `processes/normalization.py` | ¿Funciones asumen campos de Computrabajo (ubicacion, salario, tiempo)? |
| [ ] | | | `processes/mining.py` | ¿Extracción atada a descripciones en español? |
| [ ] | | | `processes/parsing.py` | ¿Regex solo en español? ¿Soporta otros idiomas? |
| [ ] | | | `processes/persistence.py` | `save_to_db` y `update_db_scores` — ¿duplicados en otros lados? |
| [ ] | | | `data/tech_registry.py` | ¿Tecnologías pendientes de registrar? ¿Categorías completas? |
| [ ] | | | `data/patterns.py` | `CIUDAD_MAP` solo Colombia. ¿Patrones reutilizables fuera de Computrabajo? |
| [ ] | | | `master_sync.py` | ¿Hace más de lo que debería? ¿Acoplado? |
| [ ] | | | `bootstrap_master.py` | ¿Migración inicial ya cumplida? ¿Se borra? |
| [ ] | | `scripts/` | `run_antioquia_1.py` | ¿Se usa activamente? |
| [ ] | | | `run_dds.py` | ¿Se usa activamente? |
| [ ] | | | `run_dds_full.py` | ¿Se usa activamente? |
| [ ] | | | `run_fullstack.py` | ¿Se usa activamente? |
| [ ] | | | `run_fullstack_3.py` | ¿Se usa activamente? |
| [ ] | | | `run_backend_1.py` | ¿Se usa activamente? |
| [ ] | | | `run_backend_3.py` | ¿Se usa activamente? |
| [ ] | | | `run_frontend_1.py` | ¿Se usa activamente? |
| [ ] | | | `run_frontend_3.py` | ¿Se usa activamente? |
| [ ] | | | `run_desarrollador_software.py` | ¿Se usa activamente? |
| [ ] | | | `run_dds_antioquia.py` | ¿Se usa activamente? |
| [ ] | | | `run_dds_3.py` | ¿Se usa activamente? |
| [ ] | | | `run_refresh_master.py` | Lógica duplicada con scheduler y API. ¿Consolidar? |
| [ ] | | | `reset_db.py` | ¿Se usa activamente? |
| [ ] | | | `migrate_notas.py` | ¿Migración ya cumplida? ¿Se borra? |
| [ ] | | | `migrate_perfil.py` | ¿Migración ya cumplida? ¿Se borra? |
| [ ] | | | `scheduler/run.py` | Punto de entrada del scheduler. |
| [ ] | | | `scheduler/run_3.py` | ¿Variante obsoleta? |
| [ ] | | | `scheduler/start.py` | ¿Lógica de arranque aún válida con nueva arquitectura? |
| [ ] | | | `scheduler/start_3.py` | ¿Variante obsoleta? |
| [ ] | | | `scheduler/stop.py` | ¿Sigue siendo necesario? |
| [ ] | | | `scheduler/status.py` | ¿Sigue siendo necesario? |
| [ ] | | | `semantic/` | `export_descriptions.py` y `.txt`. ¿Auditoría puntual o herramienta activa? |
| [ ] | | `modules/` | `browser.py` | ¿Inicialización de Playwright reutilizable para otros scrapers? |
| [ ] | | | `scheduler.py` | Refresh de scores duplicado. ¿Consolidar? ¿Búsquedas fijas o configurables? |
| [ ] | | | `notifier.py` | ¿Notificaciones necesarias? ¿Acoplado a plyer? |
| [ ] | | `database/` | `db.py` | Conexión. ¿Pool de sesiones adecuado? |
| [ ] | | | `models.py` | Revisar constraints, tipos de datos, índices faltantes, longitud de VARCHAR. |
| [ ] | | `api/` | Estructura de routers | ¿Escala con nuevas fuentes? ¿Nuevos endpoints necesarios? |
| [ ] | | | `routes/scraper.py` | Endpoints fijos (dds, dds-full, fullstack). ¿Deberían ser genéricos? |
| [ ] | | | `routes/stats.py` | Stats actuales. ¿Se necesitan nuevas métricas multi-fuente? |
| [ ] | | | `routes/ofertas.py` | CRUD actual. ¿Filtros por origen contemplados? |
| [ ] | | | `main.py` | Registro de routers. |
| [ ] | | `correlation/` | `correlator.py` | ¿Bien aislado? ¿Dependencias externas? |
| [ ] | | | `profile/user_profile.json` | Archivo vacío. ¿Vestigio? ¿Se lee de BD? |
| [ ] | | | `docs/correlation_model.md` | Documentación del modelo WMS. |
| [ ] | | `config/` | `scheduler_state.json` | ¿Debe vivir en `config/` o en otra carpeta? ¿Formato adecuado para multi-fuente? |
| [ ] | | `data/` | Archivos sueltos | `auditoria_maestra_techs.md`, `computrabajo_snapshot.txt`, `ofertas_descripciones.txt`. ¿Activos o históricos? |
| [ ] | | `docs/` | Documentación existente | `scheduler.md`, `backend_quickstart.md`. ¿Actualizados? ¿Falta documentación? |
| [ ] | | `notebooks/` | `contactar/conclusiones.ipynb` | ¿Se usa? ¿Herramienta activa o exploración puntual? |
| [ ] | | `mining_stats/` | `metrics.py` | ¿Funciones usadas por la API? ¿Alguna sin uso? |
| [ ] | | | `reports/` | Carpeta vacía (solo readme). |
| [ ] | | `main.py` | Raíz del proyecto | Punto de entrada directo a Computrabajo. ¿Debe existir o se elimina? |
| [ ] | 3 — Cierre | Contrato del pipeline | Documentación | Documentar la interfaz exacta que un scraper debe cumplir para enchufarse. |
| [ ] | | Convenciones finales | Documentación | Un documento de referencia con todas las convenciones adoptadas. |
| [ ] | | Validación | Scheduler | Verificar que el scheduler funciona con la nueva estructura. |
| [ ] | | Validación | API | Verificar que todos los endpoints responden correctamente. |
| [ ] | | Cierre de carpeta temporal | `refactorizacion_temporal/` | Revisar que todo lo documentado esté completo y eliminar la carpeta. |
