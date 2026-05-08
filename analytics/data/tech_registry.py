
TECH_KEYWORDS = {
    # Lenguajes
    'JavaScript': [r'\bjavascript\b', r'\bjs\b'],
    'TypeScript': [r'\btypescript\b', r'\bts\b'],
    'Node.js': [r'\bnode\.js\b', r'\bnodejs\b'],
    'Python': [r'\bpython\b'],
    'Java': [r'\bjava\b(?!script)'],
    'C#': [r'\bc\#'],
    '.NET': [r'\b\.net\b', r'\basp\.net\b', r'\bdotnet\b'],
    'PHP': [r'\bphp\b'],
    'Ruby': [r'\bruby\b'],
    'Go': [r'\bgolang\b'],
    'HTML': [r'\bhtml\b', r'\bhtml5\b'],
    'CSS': [r'\bcss\b', r'\bcss3\b'],
    
    # Frameworks / Librerias
    'React': [r'\breact\b', r'\breactjs\b'],
    'Angular': [r'\bangular\b'],
    'Vue.js': [r'\bvue\b', r'\bvuejs\b'],
    'Laravel': [r'\blaravel\b'],
    'Symfony': [r'\bsymfony\b'],
    'Django': [r'\bdjango\b'],
    'Flask': [r'\bflask\b'],
    'Express.js': [r'\bexpress\.?js\b', r'\bexpressjs\b'],
    'Next.js': [r'\bnext\.?js\b', r'\bnextjs\b'],
    'NestJS': [r'\bnest\.?js\b', r'\bnestjs\b'],
    'Spring Boot': [r'\bspring\s*boot\b', r'\bspringboot\b'],
    'GraphQL': [r'\bgraphql\b'],
    
    # Bases de Datos
    'SQL': [r'\bsql\b'],
    'MySQL': [r'\bmysql\b'],
    'PostgreSQL': [r'\bpostgresql\b', r'\bpostgre\b'],
    'SQL Server': [r'\bsqlserver\b', r'\bt-sql\b'],
    'Oracle': [r'\boracle\b'],
    'MongoDB': [r'\bmongodb\b', r'\bmongo\b'],
    'Redis': [r'\bredis\b'],
    
    # Cloud
    'AWS': [r'\baws\b', r'\bamazon web services\b'],
    'Azure': [r'\bazure\b'],
    'GCP': [r'\bgcp\b', r'\bgoogle cloud\b'],
    'Firebase': [r'\bfirebase\b'],
    
    # DevOps & Herramientas
    'Docker': [r'\bdocker\b'],
    'Kubernetes': [r'\bkubernetes\b', r'\bk8s\b'],
    'Git': [r'\bgit\b', r'\bgithub\b', r'\bgitlab\b'],
    'CI/CD': [r'\bci/cd\b', r'\bjenkins\b'],
    
    # Mobile
    'Flutter': [r'\bflutter\b'],
    'React Native': [r'\breact native\b'],
    'Ionic': [r'\bionic\b'],
    'iOS': [r'\bios\b'],
    'Swift': [r'\bswift\b'],
    'Android': [r'\bandroid\b'],
    'Kotlin': [r'\bkotlin\b'],
    
    # Analítica
    'Power BI': [r'\bpower bi\b'],
    'Tableau': [r'\btableau\b'],
    'Pandas': [r'\bpandas\b'],
    'ETL': [r'\betl\b'],
    
    # Arquitectura / Conceptos
    'Microservicios': [r'\bmicroservicios?\b', r'\bmicroservices?\b'],
}
TECH_CATEGORIES = {
    'backend': [
        'Python', 'Java', 'C#', '.NET', 'PHP', 'Ruby', 'Go', 'Node.js', 
        'Laravel', 'Symfony', 'Django', 'Flask', 'Express.js', 'NestJS',
        'Spring Boot', 'GraphQL', 'SQL', 'MySQL', 'PostgreSQL', 'SQL Server', 'Oracle', 'Redis'
    ],
    'frontend': [
        'JavaScript', 'TypeScript', 'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Next.js'
    ],
    'mobile': [
        'Flutter', 'React Native', 'Ionic', 'iOS', 'Swift', 'Android', 'Kotlin'
    ],
    'devops': [
        'Docker', 'Kubernetes', 'Git', 'CI/CD'
    ],
    'cloud': [
        'AWS', 'Azure', 'GCP', 'Firebase'
    ],
    'data': [
        'MongoDB', 'Power BI', 'Tableau', 'Pandas', 'ETL'
    ],
    'arquitectura': [
        'Microservicios',
    ]
}
