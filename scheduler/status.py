import json
import os
from datetime import datetime

STATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config",
    "scheduler_state.json"
)

state = {}
with open(STATE_PATH, "r", encoding="utf-8") as f:
    state = json.load(f)

print("=" * 50)
print(" SCHEDULER STATUS")
print("=" * 50)
print(f" Estado:    {'ACTIVO' if state.get('enabled') else 'DETENIDO'}")
print(f" Búsqueda: {state.get('search_term', '-')}")
print(f" Ubicación: {state.get('location', '-')}")
print(f" Frecuencia: {state.get('frequency_minutes', 60)} min")
print(f" Jitter:    ±{state.get('jitter_minutes', 15)} min")
print(f" Última ejecución: {state.get('last_run') or 'Nunca'}")
print(f" Últimas ofertas:  {state.get('last_offers_count', '-')}")
print("=" * 50)

last = state.get("last_run")
if last:
    try:
        last_dt = datetime.fromisoformat(last)
        freq = state.get("frequency_minutes", 60)
        jitter = state.get("jitter_minutes", 15)
        from datetime import timedelta, timezone
        now = datetime.now(timezone.utc).replace(tzinfo=None) if last_dt.tzinfo else datetime.now()
        elapsed = now - last_dt.replace(tzinfo=None) if last_dt.tzinfo else now - last_dt
        next_min = max(0, (freq + jitter) - elapsed.total_seconds() / 60)
        if state.get("enabled"):
            print(f" Próxima ejecución estimada: en ~{int(next_min)} min")
        print(f" Última hace: {int(elapsed.total_seconds() / 60)} min")
    except:
        pass
print("=" * 50)
