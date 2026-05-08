import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_session
from database.models import Oferta
from analytics.processes.parsing import parse_tech_stack
from analytics.data.tech_registry import TECH_KEYWORDS, TECH_CATEGORIES

OUTPUT = os.path.join("data", "auditoria_techs.md")

REGISTERED = set(TECH_KEYWORDS.keys())

# ---------------------------------------------------------------------------
# Candidatas a buscar — SOLO las que NO están ya en TECH_KEYWORDS
# ---------------------------------------------------------------------------
CANDIDATES = {
    # --- Frontend ---
    "jQuery":            [r'\bjquery\b'],
    "Bootstrap":         [r'\bbootstrap\b'],
    "Tailwind CSS":      [r'\btailwind\b'],
    "SASS/SCSS":         [r'\bsass\b', r'\bscss\b'],
    "Redux":             [r'\bredux\b'],
    "Material UI":       [r'\bmaterial[- ]?ui\b', r'\bmui\b'],
    "Webpack":           [r'\bwebpack\b'],
    "Vite":              [r'\bvite\b'],
    "Svelte":            [r'\bsvelte\b'],
    "Nuxt.js":           [r'\bnuxt\.?js\b', r'\bnuxt\b'],
    # --- Backend ---
    "FastAPI":           [r'\bfastapi\b'],
    "Hibernate":         [r'\bhibernate\b'],
    "JPA":               [r'\bjpa\b'],
    "Entity Framework":  [r'\bentity\s*framework\b', r'\bef\s*core\b'],
    "ADO.NET":           [r'\bado\.net\b'],
    "WCF":               [r'\bwcf\b'],
    "SOAP":              [r'\bsoap\b'],
    "gRPC":              [r'\bgrpc\b'],
    "Celery":            [r'\bcelery\b'],
    # --- Mobile ---
    "Xamarin":           [r'\bxamarin\b'],
    "MAUI":              [r'\bmaui\b'],
    "Blazor":            [r'\bblazor\b'],
    # --- Bases de datos ---
    "Cassandra":         [r'\bcassandra\b'],
    "SQLite":            [r'\bsqlite\b'],
    "MariaDB":           [r'\bmariadb\b'],
    "Elasticsearch":     [r'\belasticsearch\b', r'\belk\b'],
    "DynamoDB":          [r'\bdynamodb\b'],
    "Cosmos DB":         [r'\bcosmos\s*db\b'],
    # --- DevOps / Infra ---
    "Nginx":             [r'\bnginx\b'],
    "Apache":            [r'\bapache\b'],
    "Linux":             [r'\blinux\b'],
    "Terraform":         [r'\bterraform\b'],
    "Ansible":           [r'\bansible\b'],
    "Jenkins":           [r'\bjenkins\b'],
    "GitHub Actions":    [r'\bgithub\s*actions\b'],
    "GitLab CI":         [r'\bgitlab\s*ci\b'],
    "Kafka":             [r'\bkafka\b'],
    "RabbitMQ":          [r'\brabbitmq\b', r'\brabbit\s*mq\b'],
    "Prometheus":        [r'\bprometheus\b'],
    "Grafana":           [r'\bgrafana\b'],
    # --- Testing ---
    "Jest":              [r'\bjest\b'],
    "Cypress":           [r'\bcypress\b'],
    "JUnit":             [r'\bjunit\b'],
    "Mockito":           [r'\bmockito\b'],
    "Selenium":          [r'\bselenium\b'],
    "Mocha":             [r'\bmocha\b'],
    "Jasmine":           [r'\bjasmine\b'],
    # --- Analítica / Datos ---
    "NumPy":             [r'\bnumpy\b'],
    "Databricks":        [r'\bdatabricks\b'],
    "Apache Spark":      [r'\bapache\s*spark\b', r'\bspark\b(?!\s*boot)'],
    "SSIS":              [r'\bssis\b'],
    "SSRS":              [r'\bssrs\b'],
    "SSAS":              [r'\bssas\b'],
    "Metabase":          [r'\bmetabase\b'],
    "Streamlit":         [r'\bstreamlit\b'],
    # --- Herramientas / Plataformas ---
    "UiPath":            [r'\buipath\b'],
    "Power Automate":    [r'\bpower\s*automate\b'],
    "SAP":               [r'\bsap\b'],
    "Salesforce":        [r'\bsalesforce\b'],
    "Swagger/OpenAPI":   [r'\bswagger\b', r'\bopenapi\b'],
    "JWT":               [r'\bjwt\b', r'\bjson\s*web\s*token\b'],
    "OAuth":             [r'\boauth\b'],
    "Figma":             [r'\bfigma\b'],
    "Jira":              [r'\bjira\b'],
    # --- Lenguajes ---
    "Scala":             [r'\bscala\b'],
    "Rust":              [r'\brust\b'],
    "Dart":              [r'\bdart\b'],
    "VB.NET":            [r'\bvb\.?net\b'],
    # --- Otros ---
    "Microservicios":    [r'\bmicroservicios?\b', r'\bmicroservices?\b'],
    "Web Services":      [r'\bweb\s*services?\b'],
    "REST API":          [r'\brest\s*api\b', r'\brestful\b'],
}

# Sanity check: ninguna candidata debe estar ya registrada
overlap = set(CANDIDATES.keys()) & REGISTERED
if overlap:
    print(f"ERROR: Estas ya estan registradas y sobran en CANDIDATES: {overlap}")
    sys.exit(1)

# ---------------------------------------------------------------------------
def run():
    session = get_session()
    try:
        offers = session.query(Oferta).order_by(Oferta.id).all()
    finally:
        session.close()

    if not offers:
        print("Sin ofertas.")
        return

    # 1. Contar frecuencias de candidatas
    candidate_freq = {}
    for name, patterns in CANDIDATES.items():
        compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
        count = 0
        offers_with = []
        for o in offers:
            desc = o.descripcion or ""
            if any(cp.search(desc) for cp in compiled):
                count += 1
                offers_with.append(o.id_oferta)
        if count > 0:
            candidate_freq[name] = {"count": count, "offers": offers_with}

    # 2. Por oferta: capturado vs no capturado
    per_offer = []
    for o in offers:
        desc = o.descripcion or ""
        captured = parse_tech_stack(desc)
        missed = []
        for name, patterns in CANDIDATES.items():
            compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
            if any(cp.search(desc) for cp in compiled):
                missed.append(name)
        per_offer.append({
            "id": o.id_oferta,
            "titulo": o.titulo or "",
            "captured": captured,
            "missed": missed,
        })

    # 3. Generar Markdown
    L = []
    L.append("# Auditoría de Tecnologías — Compatibilidad")
    L.append("")
    L.append(f"- **Ofertas analizadas:** {len(offers)}")
    L.append(f"- **Techs registradas actualmente:** {len(REGISTERED)}")
    L.append(f"- **Candidatas NO registradas encontradas:** {len(candidate_freq)}")
    L.append("")

    L.append("---")
    L.append("")
    L.append("## 1. Tecnologías YA registradas (para referencia)")
    L.append("")
    for cat, techs in TECH_CATEGORIES.items():
        L.append(f"- **{cat}**: {', '.join(sorted(techs))}")
    L.append("")

    L.append("---")
    L.append("")
    L.append("## 2. Tecnologías NO registradas — encontradas en las ofertas")
    L.append("")
    L.append("| # | Tecnología | Ofertas | % | Primeros id_oferta |")
    L.append("|---|---|---|---|---|")
    for i, (name, info) in enumerate(sorted(candidate_freq.items(), key=lambda x: -x[1]["count"]), 1):
        pct = round(info["count"] / len(offers) * 100, 1)
        sample = ", ".join(f"`{x[:12]}…`" for x in info["offers"][:3])
        L.append(f"| {i} | **{name}** | {info['count']} | {pct}% | {sample} |")

    L.append("")
    L.append("---")
    L.append("")
    L.append("## 3. PROPUESTA: Techs a agregar (≥ 3 ofertas, ~3%)")
    L.append("")

    min_freq = 3
    propuestas = {k: v for k, v in candidate_freq.items() if v["count"] >= min_freq}

    # Agrupar propuestas
    grupos = {
        "Frontend":       ["jQuery", "Bootstrap", "Tailwind CSS", "SASS/SCSS", "Redux", "Material UI", "Webpack", "Vite", "Svelte", "Nuxt.js"],
        "Backend":        ["FastAPI", "Hibernate", "JPA", "Entity Framework", "WCF", "SOAP", "gRPC", "Celery"],
        "Mobile":         ["Xamarin", "MAUI", "Blazor"],
        "Bases de Datos": ["Cassandra", "SQLite", "MariaDB", "Elasticsearch", "DynamoDB", "Cosmos DB"],
        "DevOps / Infra": ["Nginx", "Apache", "Linux", "Terraform", "Ansible", "Jenkins", "GitHub Actions", "GitLab CI", "Kafka", "RabbitMQ", "Prometheus", "Grafana"],
        "Testing":        ["Jest", "Cypress", "JUnit", "Mockito", "Selenium", "Mocha", "Jasmine"],
        "Datos / BI":     ["NumPy", "Databricks", "Apache Spark", "SSIS", "SSRS", "SSAS", "Metabase", "Streamlit"],
        "Plataformas":    ["UiPath", "Power Automate", "SAP", "Salesforce", "Swagger/OpenAPI", "JWT", "OAuth", "Figma", "Jira"],
        "Lenguajes":      ["Scala", "Rust", "Dart", "VB.NET"],
    }

    for grupo, names in grupos.items():
        items = [(n, propuestas[n]["count"]) for n in names if n in propuestas]
        if not items:
            continue
        L.append(f"### {grupo}")
        for name, cnt in sorted(items, key=lambda x: -x[1]):
            L.append(f"- [ ] **{name}** — aparece en **{cnt}** ofertas")
        L.append("")

    # También mostrar las que aparecen 1-2 veces (para que el usuario decida)
    L.append("### Baja frecuencia (1-2 ofertas) — no prioritarias")
    bajas = {k: v for k, v in candidate_freq.items() if v["count"] < min_freq}
    for name, info in sorted(bajas.items(), key=lambda x: -x[1]["count"]):
        L.append(f"- [ ] **{name}** — {info['count']} oferta(s)")
    L.append("")

    L.append("---")
    L.append("")
    L.append("## 4. Muestra: primeras 20 ofertas con más techs sin capturar")
    L.append("")
    per_offer_sorted = sorted(per_offer, key=lambda x: -len(x["missed"]))
    for po in per_offer_sorted[:20]:
        L.append(f"### {po['titulo'][:90]}")
        L.append(f"`{po['id']}`")
        L.append(f"- **Capturado ({len(po['captured'])})**: {', '.join(po['captured']) if po['captured'] else '—'}")
        L.append(f"- **NO capturado ({len(po['missed'])})**: {', '.join(po['missed']) if po['missed'] else '—'}")
        L.append("")

    L.append("---")
    L.append(f"*Reporte generado automáticamente — {len(offers)} ofertas — {len(REGISTERED)} techs registradas*")
    L.append("")

    content = "\n".join(L)
    os.makedirs("data", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Reporte: {OUTPUT}")
    print(f"   Techs registradas: {len(REGISTERED)}")
    print(f"   Candidatas encontradas en ofertas: {len(candidate_freq)}")
    print(f"   Propuestas (>={min_freq} ofertas): {len(propuestas)}")

if __name__ == "__main__":
    run()
