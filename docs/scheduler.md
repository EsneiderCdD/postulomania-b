# Scheduler

## Descripción

El scheduler ejecuta el scraper de `run_antioquia_1` de forma automática y periódica mientras el servidor FastAPI está corriendo. Cada ciclo:

1. Scrapea `Desarrollador de Software` en `Antioquia` con filtro `pubdate=1` (hoy)
2. Corre el pipeline de analytics (limpieza, normalización, minería)
3. Sincroniza ofertas nuevas a PostgreSQL (`sync_to_master`)
4. Refresca los scores de compatibilidad de todas las ofertas (equivale a `run_refresh_master`)
5. Lanza notificación desktop si encontró ofertas nuevas

El navegador se ejecuta en modo `headless` (sin ventana gráfica).

---

## Comandos

```powershell
# Iniciar API + scheduler (ambos como subprocesos)
python -m scripts.scheduler.start

# Ver estado del scheduler
python -m scripts.scheduler.status

# Desactivar scraping (API sigue corriendo)
python -m scripts.scheduler.stop

# Detener todo
Ctrl + C en las ventanas de uvicorn y del scheduler
```

**Requisito previo**: PostgreSQL debe estar corriendo. El puerto 8000 debe estar libre (el script lo verifica).

---

## Arquitectura

```
scripts/scheduler/start.py
    │
    ├── subprocess 1: uvicorn api.main:app --reload   (puerto 8000)
    └── subprocess 2: scripts/scheduler/run.py
                           │
                           └── modules/scheduler.py::start()
                                  │
                                  └── loop infinito:
                                       1. Lee config/scheduler_state.json
                                       2. Si enabled=false → sale
                                       3. Si enabled=true:
                                          a. run_computrabajo(headless=True)
                                          b. run_pipeline()
                                          c. sync_to_master()
                                          d. Re-score global (apply_correlation + update_db_scores)
                                          e. notify()
                                       4. asyncio.sleep((freq + jitter) * 60)
```

### Archivos involucrados

| Archivo | Rol |
|---|---|
| `config/scheduler_state.json` | Estado y configuración en caliente (JSON) |
| `modules/scheduler.py` | Core del loop asyncio |
| `scripts/scheduler/start.py` | CLI: lanza API + scheduler como subprocesos |
| `scripts/scheduler/stop.py` | CLI: escribe `enabled: false` en el state file |
| `scripts/scheduler/status.py` | CLI: lee y muestra el estado actual |
| `scripts/scheduler/run.py` | Entry point del scheduler: configura asyncio y arranca `start()` |
| `modules/notifier.py` | Notificaciones desktop (plyer) |
| `modules/browser.py` | Inicialización de Playwright/Chromium |

### Flujo de datos por ciclo

```
run_computrabajo(search_term, location, headless=True)
    → raw_data (list[dict])
run_pipeline(raw_data)
    → df_cleaned (DataFrame)
sync_to_master(df, slug, keyword)
    → apply_correlation() + save_to_db()  (solo ofertas nuevas)
session.query(Oferta).all()
    → apply_correlation() + update_db_scores()  (todas las ofertas)
notify()
```

---

## Archivo de estado (`config/scheduler_state.json`)

```json
{
  "enabled": true,
  "frequency_minutes": 60,
  "jitter_minutes": 15,
  "last_run": null,
  "last_offers_count": 0,
  "search_term": "Desarrollador de Software",
  "location": "Antioquia"
}
```

| Campo | Tipo | Descripción |
|---|---|---|
| `enabled` | bool | `true` ejecuta scraping, `false` pausa el scheduler en el próximo ciclo |
| `frequency_minutes` | int | Minutos base entre ciclos |
| `jitter_minutes` | int | Minutos extra aleatorios (0 a N) para evitar patrón detectable |
| `last_run` | string | ISO timestamp de la última ejecución completada |
| `last_offers_count` | int | Ofertas encontradas en el último ciclo |
| `search_term` | string | Término de búsqueda en Computrabajo |
| `location` | string | Filtro de ubicación geográfica |

Los scripts CLI y el scheduler leen/escriben este archivo sin necesidad de reiniciar procesos. Para cambiar frecuencia, término o ubicación se edita el JSON directamente.

---

## Comparación con ejecución manual

| Acción | Manual | Scheduler |
|---|---|---|
| Scrape + pipeline | `python -m scripts.run_antioquia_1` | Automático |
| Guardar ofertas nuevas | Incluido en el comando anterior | Automático |
| Re-score global | `python -m scripts.run_refresh_master` | Automático en cada ciclo |
| Repetición | Manual (volver a ejecutar) | Automática cada `frequency + jitter` minutos |

---

## Dependencias

- `playwright` — automatización de navegador (Chromium)
- `plyer` — notificaciones desktop
- `pandas` — manipulación de datos
- `sqlalchemy` — ORM para PostgreSQL
- No se usan frameworks externos de scheduling (APScheduler, Celery, etc.)

---

## Comportamiento en Windows

- `scripts/scheduler/run.py` configura explícitamente `WindowsProactorEventLoopPolicy` para compatibilidad asyncio.
- `scripts/scheduler/start.py` usa `subprocess.CREATE_NEW_CONSOLE` para lanzar API y scheduler en ventanas separadas.
- `api/main.py` también configura `WindowsProactorEventLoopPolicy`.

---

## Problemas conocidos

1. **Dos ventanas de consola en Windows** — `start.py` usa `CREATE_NEW_CONSOLE`, lo que abre ventanas separadas para API y scheduler. Si se cierra la ventana del scheduler, el proceso muere sin que `start.py` lo detecte (ya terminó su ejecución). La API queda viva pero sin scraping periódico.

2. **Sin verificación de arranque** — `start.py` lanza los subprocesos y sale inmediatamente. No confirma que uvicorn o el scheduler iniciaron correctamente.

3. **Notificación de depuración al iniciar** — `modules/scheduler.py:45` emite `"Hola Mundo — scheduler activo"` al arrancar. No es un mensaje productivo.

4. **`stop.py` y `status.py` sin guard `if __name__`** — si se importaran desde otro módulo, su código se ejecutaría inmediatamente. Actualmente no son importados, por lo que no es un bug activo.

5. **Inconsistencia doc vs. archivo real** — la documentación anterior mostraba `"enabled": false` como estado inicial, pero el archivo `config/scheduler_state.json` tiene `"enabled": true`.

6. **Sin supervisión de procesos** — si el scheduler crashea, no hay mecanismo de reinicio automático. No se usa ningún process manager (systemd, supervisor, etc.).

7. **Condición de carrera en `start.py`** — escribe `enabled: true` al state file antes de lanzar los subprocesos. Si el script muere entre el write y el spawn, el state queda como "activado" pero no hay scheduler corriendo.

8. **Re-score global duplica lógica** — el bloque de refresco de scores en `modules/scheduler.py:75-92` es idéntico a `api/routes/scraper.py:67-91` (endpoint `/scraper/refresh`) y a `scripts/run_refresh_master.py`. Cambios en uno deben replicarse en los otros.
