import json
import os
import socket
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(ROOT, "config", "scheduler_state.json")
PORT = 8000


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


if __name__ == "__main__":
    if is_port_in_use(PORT):
        print(f"Ya hay un servidor corriendo en el puerto {PORT}. Detenelo antes de iniciar otro.")
        sys.exit(1)

    state = {"enabled": False}
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        state = json.load(f)

    state["enabled"] = True

    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    print(f"Scheduler activado. Frecuencia: {state['frequency_minutes']} min "
          f"(+-{state['jitter_minutes']} jitter)")
    print(f"Termino: {state['search_term']} | Ubicacion: {state['location']}")

    creationflags = subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0

    print("Iniciando API...")
    api_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--reload"],
        cwd=ROOT,
        creationflags=creationflags
    )

    print("Iniciando scheduler...")
    scheduler_proc = subprocess.Popen(
        [sys.executable, "scheduler/run.py"],
        cwd=ROOT,
        creationflags=creationflags
    )

    print(f"API (PID {api_proc.pid}) y scheduler (PID {scheduler_proc.pid}) iniciados.")
    print("Para detener el scheduler: python scheduler/stop.py")
    print("Para detener la API: cierra la ventana de uvicorn (Ctrl+C).")
