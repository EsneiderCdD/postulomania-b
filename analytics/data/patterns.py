import re

# Patrones para extracción de información en descripciones y títulos
EXP_PATTERN = re.compile(r'(\d+)\s*(?:(?:a|-)\s*(\d+)\s*)?(años?|mes(?:es)?)', re.IGNORECASE)

CONTRACT_PATTERNS = {
    "Indefinido": re.compile(r'\bindefinido\b', re.IGNORECASE),
    "Obra y Labor": re.compile(r'\bobra\s*y\s*labor\b', re.IGNORECASE),
    "Prestación de servicios": re.compile(r'\bprestaci[oó]n\s*de\s*servicios\b', re.IGNORECASE),
    "Término Fijo": re.compile(r'\bt[eé]rmino\s*fijo\b', re.IGNORECASE),
}

ENGLISH_PATTERN = re.compile(r'\b(ingl[eé]s|english|biling[üu]e|b1|b2|c1|c2|toefl|ielts)\b', re.IGNORECASE)

EDUCATION_PATTERNS = {
    "Ingeniero": re.compile(r'\b(ingeniero|profesional|ingenier[ií]a)\b', re.IGNORECASE),
    "Tecnólogo": re.compile(r'\b(tecn[oó]logo|tecnolog[ií]a)\b', re.IGNORECASE),
    "Técnico": re.compile(r'\b(t[eé]cnico|auxiliar)\b', re.IGNORECASE),
}

COMPANY_SUFFIXES_PATTERN = re.compile(r'\b(S\.?\s*A\.?\s*S\.?|L\.?\s*T\.?\s*D\.?\s*A\.?|S\.?\s*A\.?|I\.?\s*N\.?\s*C\.?|B\.?\s*I\.?\s*C\.?)\b', re.IGNORECASE)

CLEAN_SPACES_PATTERN = re.compile(r'\s+', re.IGNORECASE)

AUTHORIZED_JOB_TITLES = [
    "Desarrollador de software",
    "React",
    "Full Stack"
]

# Patrones residuales extraídos de parsers
DIGITS_ONLY_PATTERN = re.compile(r'[^\d]')
PARENTHESES_CONTENT_PATTERN = re.compile(r'\((.*?)\)')
DATE_MINUTES_PATTERN = re.compile(r'(\d+)\s+minutos?', re.IGNORECASE)
DATE_HOURS_PATTERN = re.compile(r'(\d+)\s+horas?', re.IGNORECASE)
DATE_DAYS_PATTERN = re.compile(r'(\d+)\s+días?', re.IGNORECASE)

CIUDAD_MAP = {
    'bogotá d.c.': ('Bogotá', 'Bogotá D.C.'),
    'bogotá dc': ('Bogotá', 'Bogotá D.C.'),
    'bogota d.c.': ('Bogotá', 'Bogotá D.C.'),
    'bogota dc': ('Bogotá', 'Bogotá D.C.'),
    'bogotá': ('Bogotá', 'Bogotá D.C.'),
    'bogota': ('Bogotá', 'Bogotá D.C.'),
    'medellín': ('Medellín', 'Antioquia'),
    'medellin': ('Medellín', 'Antioquia'),
    'cali': ('Cali', 'Valle del Cauca'),
    'barranquilla': ('Barranquilla', 'Atlántico'),
    'cartagena de indias': ('Cartagena de Indias', 'Bolívar'),
    'cartagena': ('Cartagena de Indias', 'Bolívar'),
    'bucaramanga': ('Bucaramanga', 'Santander'),
    'cúcuta': ('Cúcuta', 'Norte de Santander'),
    'cucuta': ('Cúcuta', 'Norte de Santander'),
    'neiva': ('Neiva', 'Huila'),
    'santa marta': ('Santa Marta', 'Magdalena'),
    'villavicencio': ('Villavicencio', 'Meta'),
    'ibagué': ('Ibagué', 'Tolima'),
    'ibague': ('Ibagué', 'Tolima'),
    'pereira': ('Pereira', 'Risaralda'),
    'manizales': ('Manizales', 'Caldas'),
    'armenia': ('Armenia', 'Quindío'),
    'pasto': ('Pasto', 'Nariño'),
    'popayán': ('Popayán', 'Cauca'),
    'popayan': ('Popayán', 'Cauca'),
    'montería': ('Montería', 'Córdoba'),
    'monteria': ('Montería', 'Córdoba'),
    'sincelejo': ('Sincelejo', 'Sucre'),
    'valledupar': ('Valledupar', 'Cesar'),
    'tunja': ('Tunja', 'Boyacá'),
    'yopal': ('Yopal', 'Casanare'),
    'mocoa': ('Mocoa', 'Putumayo'),
    'quibdó': ('Quibdó', 'Chocó'),
    'quibdo': ('Quibdó', 'Chocó'),
    'arauca': ('Arauca', 'Arauca'),
    'leticia': ('Leticia', 'Amazonas'),
    'inírida': ('Inírida', 'Guainía'),
    'inirida': ('Inírida', 'Guainía'),
    'san josé del guaviare': ('San José del Guaviare', 'Guaviare'),
    'san jose del guaviare': ('San José del Guaviare', 'Guaviare'),
    'san andrés': ('San Andrés', 'San Andrés y Providencia'),
    'san andres': ('San Andrés', 'San Andrés y Providencia'),
    'cota': ('Cota', 'Cundinamarca'),
    'chía': ('Chía', 'Cundinamarca'),
    'chia': ('Chía', 'Cundinamarca'),
    'funza': ('Funza', 'Cundinamarca'),
    'madrid': ('Madrid', 'Cundinamarca'),
    'mosquera': ('Mosquera', 'Cundinamarca'),
    'subachoque': ('Subachoque', 'Cundinamarca'),
    'tenjo': ('Tenjo', 'Cundinamarca'),
    'soacha': ('Soacha', 'Cundinamarca'),
    'siberia': ('Siberia', 'Cundinamarca'),
    'envigado': ('Envigado', 'Antioquia'),
    'bello': ('Bello', 'Antioquia'),
    'itagüí': ('Itagüí', 'Antioquia'),
    'itagui': ('Itagüí', 'Antioquia'),
    'rionegro': ('Rionegro', 'Antioquia'),
    'floridablanca': ('Floridablanca', 'Santander'),
    'girón': ('Girón', 'Santander'),
    'giron': ('Girón', 'Santander'),
    'piedecuesta': ('Piedecuesta', 'Santander'),
    'soledad': ('Soledad', 'Atlántico'),
    'fontibón': ('Bogotá', 'Bogotá D.C.'),
    'fontibon': ('Bogotá', 'Bogotá D.C.'),
    'siberia cota': ('Cota', 'Cundinamarca'),
}
