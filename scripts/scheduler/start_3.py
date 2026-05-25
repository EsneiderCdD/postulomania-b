import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

creationflags = subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0

print("Iniciando API...")
api_proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "api.main:app", "--reload"],
    cwd=ROOT,
    creationflags=creationflags
)

print("Iniciando scheduler _3 (4 búsquedas secuenciales, 3 días, Antioquia)...")
scheduler_proc = subprocess.Popen(
    [sys.executable, "scripts/scheduler/run_3.py"],
    cwd=ROOT,
    creationflags=creationflags
)

print(f"API (PID {api_proc.pid}) y scheduler _3 (PID {scheduler_proc.pid}) iniciados.")
print("Presiona Ctrl+C en la terminal del scheduler para detener.")
print("Para detener la API: Ctrl+C en la terminal de uvicorn.")
