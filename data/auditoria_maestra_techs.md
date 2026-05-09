# Auditoría de Tecnologías — Compatibilidad

**106 ofertas analizadas** | Datos fuente: `data/ofertas_descripciones.txt` | Script: `scripts/auditar_techs.py`

---

## Contexto del sistema

### Flujo de registro de una tecnología

```
1. TECH_KEYWORDS        →  nombre canónico + regex (detección en texto)
2. TECH_CATEGORIES      →  asigna categoría al nombre canónico
3. user_profile.json    →  mismo nombre canónico como key en "tecnico"
4. parse_tech_stack()   →  usa IGNORECASE sobre los regex, retorna lista de nombres canónicos
5. seed_tech_registry() →  sincroniza categorías + tecnologías en la BD
6. calculate_score()    →  busca cada nombre canónico en el perfil (case‑sensitive exacta)
```

### Archivos que participan

| Archivo | Rol |
|---|---|
| `analytics/data/tech_registry.py` | `TECH_KEYWORDS` (detección) + `TECH_CATEGORIES` (agrupación) |
| `correlation/profile/user_profile.json` | Perfil del usuario: nivel 0.0–1.0 por cada tech |
| `analytics/processes/parsing.py:28-41` | `parse_tech_stack()` — matching regex → lista de nombres |
| `analytics/processes/mining.py:17-21` | `extract_tech_stack()` — llama a `parse_tech_stack` sobre el DataFrame |
| `correlation/correlator.py:5-65` | `calculate_score()` — promedia niveles del usuario contra las techs de la oferta |
| `analytics/processes/persistence.py:16-30` | `seed_tech_registry()` — sincroniza con BD |
| `analytics/processes/persistence.py:32-97` | `save_to_db()` — persiste ofertas + tecnologías detectadas |
| `database/models.py:38-54` | Modelos `CategoriaTech`, `Tecnologia`, `OfertaTecnologia` |
| `scripts/export_ofertas.py` | Exporta ofertas desde BD → `data/ofertas_descripciones.txt` |
| `scripts/auditar_techs.py` | Escanea ofertas buscando candidatas no registradas |
| `scripts/run_refresh_master.py` | Recalcula compatibilidades de todas las ofertas (refresh) |

### Reglas de normalización

- **Nombre canónico**: Capitalizado, nombre propio. `'JavaScript'`, `'Spring Boot'`, `'Microservicios'`. Puede tener espacios, puntos, `/`.
- **Regex patterns**: Con `\b` (word boundary). `re.IGNORECASE` aplicado siempre en `parse_tech_stack()`. Múltiples alias por tech (ej. `'Node.js': [r'\bnode\.js\b', r'\bnodejs\b']`).
- **Coincidencia con perfil**: Case‑sensitive exacta entre el nombre canónico y la key del `user_profile.json`. Si no existe la key, `calculate_score()` asigna `0.0`.
- **Categorías**: Cada tech DEBE pertenecer a una categoría en `TECH_CATEGORIES` para que `seed_tech_registry()` la persista. Categorías actuales: `backend`, `frontend`, `mobile`, `devops`, `cloud`, `data`, `arquitectura`.
- **Sin categoría** = la tech se detecta pero `save_to_db()` imprime `[WARN]` y no la persiste.

### Categorías vigentes (60 techs, 7 categorías)

| Categoría | Techs |
|---|---|
| `backend` | .NET, C#, Django, Express.js, Flask, Go, GraphQL, Java, JWT, Laravel, MySQL, NestJS, Node.js, Oracle, PHP, PostgreSQL, Python, Redis, REST API, Ruby, SAP, SOAP, SQL, SQL Server, Spring Boot, Symfony, Web Services |
| `frontend` | Angular, CSS, HTML, JavaScript, jQuery, Next.js, React, TypeScript, Vue.js |
| `mobile` | Android, Flutter, Ionic, Kotlin, React Native, Swift, iOS |
| `devops` | CI/CD, Docker, Git, Jira, Kubernetes, Linux |
| `cloud` | AWS, Azure, Firebase, GCP |
| `data` | Elasticsearch, ETL, MongoDB, Pandas, Power BI, Tableau |
| `arquitectura` | Microservicios |

---

## Tecnologías NO registradas (pendientes)

Ordenadas por frecuencia de aparición en las 106 ofertas.

| # | Tecnología | Ofertas | % | Estado |
|---|---|---|---|---|
| 1 | ~~Microservicios~~ | 10 | 9.4% | Hecho |
| 2 | ~~REST API~~ | 9 | 8.5% | Hecho |
| 3 | ~~Web Services~~ | 8 | 7.5% | Hecho |
| 4 | ~~Linux~~ | 6 | 5.7% | Hecho |
| 5 | ~~jQuery~~ | 5 | 4.7% | Hecho |
| 6 | ~~SOAP~~ | 5 | 4.7% | Hecho |
| 7 | ~~JWT~~ | 4 | 3.8% | Hecho |
| 8 | ~~Jira~~ | 4 | 3.8% | Hecho |
| 9 | ~~Elasticsearch~~ | 3 | 2.8% | Hecho |
| 10 | ~~SAP~~ | 3 | 2.8% | Hecho |
| 11 | Bootstrap | 2 | 1.9% | Pendiente |
| 12 | Entity Framework | 2 | 1.9% | Pendiente |
| 13 | Nginx | 2 | 1.9% | Pendiente |
| 14 | Apache | 2 | 1.9% | Pendiente |
| 15 | GitHub Actions | 2 | 1.9% | Pendiente |
| 16 | Jest | 2 | 1.9% | Pendiente |
| 17 | Selenium | 2 | 1.9% | Pendiente |
| 18 | Power Automate | 2 | 1.9% | Pendiente |
| 19 | Dart | 2 | 1.9% | Pendiente |
| 20 | Tailwind CSS | 1 | 0.9% | Pendiente |
| 21 | SASS/SCSS | 1 | 0.9% | Pendiente |
| 22 | Celery | 1 | 0.9% | Pendiente |
| 23 | Blazor | 1 | 0.9% | Pendiente |
| 24 | Cassandra | 1 | 0.9% | Pendiente |
| 25 | MariaDB | 1 | 0.9% | Pendiente |
| 26 | GitLab CI | 1 | 0.9% | Pendiente |
| 27 | Kafka | 1 | 0.9% | Pendiente |
| 28 | RabbitMQ | 1 | 0.9% | Pendiente |
| 29 | Cypress | 1 | 0.9% | Pendiente |
| 30 | JUnit | 1 | 0.9% | Pendiente |
| 31 | Mockito | 1 | 0.9% | Pendiente |
| 32 | Jasmine | 1 | 0.9% | Pendiente |
| 33 | NumPy | 1 | 0.9% | Pendiente |
| 34 | Databricks | 1 | 0.9% | Pendiente |
| 35 | SSIS | 1 | 0.9% | Pendiente |
| 36 | Metabase | 1 | 0.9% | Pendiente |
| 37 | Streamlit | 1 | 0.9% | Pendiente |
| 38 | UiPath | 1 | 0.9% | Pendiente |
| 39 | Salesforce | 1 | 0.9% | Pendiente |
| 40 | Swagger/OpenAPI | 1 | 0.9% | Pendiente |
| 41 | Figma | 1 | 0.9% | Pendiente |

---

## Fórmula de Compatibilidad (WMS)

### Archivos clave

| Archivo | Rol |
|---|---|
| `correlation/correlator.py:5-65` | `calculate_score()` — motor de puntuación |
| `correlation/profile/user_profile.json` | Perfil del usuario: niveles técnicos (0.0-1.0), experiencia (años), inglés (0.0-1.0), nivel educativo (0-3) |
| `analytics/data/tech_registry.py` | `TECH_KEYWORDS` (51 techs canónicas) + `TECH_CATEGORIES` (7 categorías) |
| `analytics/processes/parsing.py:28-41` | `parse_tech_stack()` — regex → lista de nombres canónicos detectados en la oferta |
| `analytics/processes/parsing.py:86-139` | `parse_english()`, `parse_education()`, `parse_experience()` — extraen requisitos no-técnicos |
| `scripts/run_refresh_master.py` | Recalcula compatibilidades de todas las ofertas en BD |

### Regla de mantenimiento

**Cada vez que se agrega una tecnología a `TECH_KEYWORDS`, debe agregarse también como key en `user_profile.json → "tecnico"` (así sea en 0.0).** El perfil debe contener las 51 techs registradas. Si una key no existe, `calculate_score()` le asigna 0.0 por defecto, pero es una omisión, no un dato.

### Variables de entrada

| Variable | Fuente | Tipo | Descripción |
|---|---|---|---|
| `tech_stack` | Oferta (vía `parse_tech_stack`) | `list[str]` | Nombres canónicos detectados en la descripción |
| `experiencia_anios` | Oferta (vía `parse_experience`) | `float` o `NaN` | Años de experiencia requeridos |
| `requiere_ingles` | Oferta (vía `parse_english`) | `bool` | `True` si la descripción menciona inglés |
| `educacion_requerida` | Oferta (vía `parse_education`) | `str` | `"Ingeniero"`, `"Tecnólogo"`, `"Técnico"`, `"No especificado"` |
| `perfil["tecnico"]` | `user_profile.json` | `dict[str → float]` | Nivel del usuario por tecnología (0.0 a 1.0) |
| `perfil["experiencia"]` | `user_profile.json` | `float` | Años de experiencia del usuario |
| `perfil["idiomas"]["ingles"]` | `user_profile.json` | `float` | Nivel de inglés del usuario (0.0 a 1.0) |
| `perfil["nivel_educativo"]` | `user_profile.json` | `int` | 0: sin, 1: Técnico, 2: Tecnólogo, 3: Ingeniero |

### Fórmula completa

```
1. AFINIDAD TÉCNICA (70% del base_score)
   tech_score = Σ(perfil["tecnico"][tech]) / len(tech_stack)
   Si tech_stack está vacío → tech_score = 0.5

2. FACTOR DE EXPERIENCIA (30% del base_score)
   req_exp = oferta.experiencia_anios
   user_exp = perfil["experiencia"]

   Si req_exp es NaN o 0        → exp_factor = 1.0
   Si user_exp >= req_exp       → exp_factor = 1.0
   Sino                         → exp_factor = user_exp / req_exp

3. BASE SCORE
   base_score = (tech_score × 0.7) + (exp_factor × 0.3)

4. MULTIPLICADOR DE INGLÉS
   Si requiere_ingles            → english_multiplier = perfil["idiomas"]["ingles"]
   Sino                         → english_multiplier = 1.0

5. MULTIPLICADOR DE EDUCACIÓN
   edu_map = {"Ingeniero": 3, "Tecnólogo": 2, "Técnico": 1, "No especificado": 0}
   req_edu = edu_map[oferta.educacion_requerida]
   user_edu = perfil["nivel_educativo"]

   effective_edu = user_edu
   Si user_exp >= 5             → effective_edu += 2
   Si user_exp >= 3             → effective_edu += 1

   Si effective_edu < req_edu   → edu_penalty = 0.9
   Sino                         → edu_penalty = 1.0

6. PUNTAJE FINAL
   final_score = base_score × english_multiplier × edu_penalty
   Redondeado a 4 decimales. Rango: [0.0, 1.0]
```

### Notas sobre la fórmula

- **tech_score**: es un promedio simple. Cada tecnología pedida por la oferta y no sabida (0.0) diluye el promedio al sumar 0 pero contar en el divisor. No es un match de cobertura, es profundidad × cobertura implícita.
- **exp_factor**: castigo lineal por no alcanzar los años requeridos. Sin requisito explícito, factor neutro (1.0).
- **english_multiplier**: filtro de protección. Multiplica directamente el score. Un nivel 0.0 en inglés vuelve invisibles las ofertas que lo requieren.
- **edu_penalty**: castigo fijo del 10%. La experiencia (≥3 o ≥5 años) eleva el nivel educativo efectivo y puede anular la penalización. No depende del requisito de la oferta, solo de la experiencia acumulada.

### Ejemplos

**Perfil de referencia:**
```
tecnicas: HTML=0.7, CSS=0.7, JavaScript=0.4
experiencia: 0.8 años
inglés: 0.3
educación: 1 (Técnico)
```

**Ejemplo 1 — Oferta frontend junior sin inglés**
```
tech_stack = ["HTML", "CSS", "JavaScript"]
experiencia = 1 año
requiere_ingles = false
educación = "Técnico"

tech_score  = (0.7 + 0.7 + 0.4) / 3 = 0.6
exp_factor  = 1.0  (1 ≥ 1)
base_score  = 0.6 × 0.7 + 1.0 × 0.3 = 0.72

english     = 1.0  (no requiere)
edu         = 1.0  (Técnico 1 ≥ Técnico 1)

final       = 0.72 × 1.0 × 1.0 = 0.72
```

**Ejemplo 2 — Oferta fullstack con inglés y educación superior**
```
tech_stack = ["HTML", "CSS", "JavaScript", "React", "Node.js", "SQL"]
experiencia = 3 años
requiere_ingles = true
educación = "Tecnólogo"

tech_score  = (0.7 + 0.7 + 0.4 + 0.4 + 0.1 + 0.1) / 6 = 2.4 / 6 = 0.4
exp_factor  = 0.8 / 3 = 0.267
base_score  = 0.4 × 0.7 + 0.267 × 0.3 = 0.28 + 0.08 = 0.36

english     = 0.3  (requiere, nivel usuario = 0.3)
effective_edu = 1 + 0 = 1  (0.8 años < 3, sin bonus)
edu_penalty = 0.9  (1 < 2)

final       = 0.36 × 0.3 × 0.9 = 0.0972 → 0.0972
```
