import json
import os

STATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config",
    "scheduler_state.json"
)

state = {"enabled": False}
with open(STATE_PATH, "r", encoding="utf-8") as f:
    state = json.load(f)

state["enabled"] = False

with open(STATE_PATH, "w", encoding="utf-8") as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print("Scheduler desactivado. El scheduler se detendra en el proximo ciclo.")
print("Para detener la API: Ctrl+C en la terminal donde corre uvicorn.")
