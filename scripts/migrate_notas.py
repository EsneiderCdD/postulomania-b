"""Migration: create notas table."""
from database.db import engine, Base
from database.models import Nota

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine, tables=[Nota.__table__])
    print("Tabla 'notas' creada (si no existía).")
