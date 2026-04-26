import asyncio
import sys
import os

# Punto entrada
from scrapers.computrabajo.main import run_computrabajo

async def main():
    print("Iniciando Postulomaniaco...")
    # Ejecutar computrabajo
    await run_computrabajo()

if __name__ == "__main__":
    asyncio.run(main())
