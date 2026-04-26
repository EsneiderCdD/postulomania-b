from analytics.processes.persistence import reset_db

if __name__ == "__main__":
    confirm = input("¿Estás seguro de que deseas ELIMINAR TODOS LOS DATOS de las tablas? (s/n): ")
    if confirm.lower() == 's':
        reset_db()
    else:
        print("Operación cancelada.")
