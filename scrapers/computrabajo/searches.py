# Configuración de búsquedas de Computrabajo.
# Fuente única de verdad para tests y scheduler.
#
# Formato de cada tupla: (search_term, location, slug, apply_filter, days)

DDS_3 = ("Desarrollador de Software", "Antioquia", "dds_antioquia_3", True, 3)
DESARROLLADOR_SOFTWARE_ANTIOQUIA = ("Desarrollador de Software", "Antioquia", "desarrollador_software_antioquia", False, 1)
BACKEND_3 = ("Desarrollador Backend", "Antioquia", "backend_antioquia_3", True, 3)
BACKEND_TODAS = ("Desarrollador Backend", "Antioquia", "backend_antioquia_todas", False, 1)
FRONTEND_3 = ("Desarrollador Frontend", "Antioquia", "frontend_antioquia_3", True, 3)
FRONTEND_TODAS = ("Desarrollador Frontend", "Antioquia", "frontend_antioquia_todas", False, 1)
FULLSTACK_3 = ("Desarrollador FullStack", "Antioquia", "fullstack_antioquia_3", True, 3)
FULLSTACK_TODAS = ("Desarrollador FullStack", "Antioquia", "fullstack_antioquia_todas", False, 1)

COMPUTRABAJO_SEARCHES = [
    DDS_3,
    DESARROLLADOR_SOFTWARE_ANTIOQUIA,
    BACKEND_3,
    BACKEND_TODAS,
    FRONTEND_3,
    FRONTEND_TODAS,
    FULLSTACK_3,
    FULLSTACK_TODAS,
]
