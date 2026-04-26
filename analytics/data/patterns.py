import re

# Patrones para extracción de información en descripciones y títulos
EXP_PATTERN = re.compile(r'(\d+)\s*(?:a\s*\d+\s*)?(años?|mes(?:es)?)', re.IGNORECASE)

SENIORITY_PATTERNS = {
    "Senior": re.compile(r'\b(senior|sr|lead|arquitecto|principal)\b', re.IGNORECASE),
    "Junior": re.compile(r'\b(junior|jr|practicante|aprendiz|trainee)\b', re.IGNORECASE),
    "Mid": re.compile(r'\b(mid|semi-senior|semisenior|intermediate)\b', re.IGNORECASE),
}

CONTRACT_PATTERNS = {
    "Indefinido": re.compile(r'\bindefinido\b', re.IGNORECASE),
    "Obra y Labor": re.compile(r'\bobra\s*y\s*labor\b', re.IGNORECASE),
    "Prestación de servicios": re.compile(r'\bprestaci[oó]n\s*de\s*servicios\b', re.IGNORECASE),
    "Término Fijo": re.compile(r'\bt[eé]rmino\s*fijo\b', re.IGNORECASE),
}

ENGLISH_PATTERN = re.compile(r'\b(ingl[eé]s|english|b1|b2|c1|c2|toefl|ielts)\b', re.IGNORECASE)

EDUCATION_PATTERNS = {
    "Ingeniero": re.compile(r'\b(ingeniero|profesional|ingenier[ií]a)\b', re.IGNORECASE),
    "Tecnólogo": re.compile(r'\b(tecn[oó]logo|tecnolog[ií]a)\b', re.IGNORECASE),
    "Técnico": re.compile(r'\b(t[eé]cnico|auxiliar)\b', re.IGNORECASE),
}

COMPANY_SUFFIXES_PATTERN = re.compile(r'\b(S\.?A\.?S\.?|L\.?T\.?D\.?A\.?|S\.?A\.?|I\.?N\.?C\.?|B\.?I\.?C\.?)\b', re.IGNORECASE)

CLEAN_SPACES_PATTERN = re.compile(r'\s+', re.IGNORECASE)

AUTHORIZED_JOB_TITLES = [
    "Desarrollador de software",
    "React",
    "Full Stack"
]

# Patrones residuales extraídos de parsers
DIGITS_ONLY_PATTERN = re.compile(r'[^\d]')
PARENTHESES_CONTENT_PATTERN = re.compile(r'\((.*?)\)')
DATE_HOURS_PATTERN = re.compile(r'(\d+)\s+horas?', re.IGNORECASE)
DATE_DAYS_PATTERN = re.compile(r'(\d+)\s+días?', re.IGNORECASE)
