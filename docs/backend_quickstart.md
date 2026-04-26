# Backend quickstart

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn api.main:app --reload
```

# Cerrar

```powershell
# detener backend (uvicorn)
Ctrl + C

# salir del entorno virtual
deactivate
```
