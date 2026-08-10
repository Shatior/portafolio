"""La prosa del sitio: lo que **no** depende de la última ejecución.

La frontera de este módulo es exactamente esa. Aquí vive el texto —el problema, las decisiones
de diseño, las métricas del protocolo de revisión—, y **ninguna cifra que el informe diario
produzca**. Los indicadores normalizados, las familias observadas, las que tienen entrada en
ATT&CK y el porcentaje del panorama sin describir salen de `lector.py`, del informe real.

La maqueta original las traía escritas a mano —«76%», «7.464», «68 de 90 familias»— y para
cuando se implementó el sitio ya eran otras. Una cifra fijada en el código envejece en silencio,
que es la peor forma de envejecer: sigue pareciendo una medición.
"""

from __future__ import annotations

REPO = "https://github.com/vigiabref/threat-intel-pipeline"
CORREO = "contacto@vigiabref.com"

NOMBRE = "Miguel Ángel Sabater Requena"
ROL = "Consultor en Ciberinteligencia"
LEMA = "Un CV dice lo que sabes hacer. Aquí puedes comprobarlo."

TITULO_PROYECTO = "Un sistema que convierte feeds públicos de amenazas en un informe diario para decidir."

ENTRADILLA = (
    "Las fuentes públicas publican miles de indicadores al día. Un analista que las consume "
    "recibe volumen, no criterio: listas sin priorizar, sin contexto de comportamiento y sin "
    "decir qué implican para una decisión concreta."
)

VERIFICACION = (
    "Construido con flujo de trabajo agéntico y verificado contra sí mismo: 15 de 16 pasadas de "
    "revisión sobre un mismo cambio encontraron al menos un bloqueante. El protocolo y sus "
    "límites, dentro."
)

COMPETENCIAS = (
    "Ciclo de inteligencia · CTI y OSINT · MITRE ATT&CK · STIX 2.1 · Python · Pydantic · "
    "GitHub Actions · Desarrollo agéntico con Claude Code · OPSEC"
)

PROBLEMA = (
    "El problema no es recolectar. Es que lo recolectado sostenga una afirmación que alguien "
    "pueda usar para actuar, y que esa afirmación sea auditable."
)

SOLUCION = (
    "Un pipeline que ejecuta el ciclo de inteligencia completo —recolección, normalización, "
    "enriquecimiento, análisis y difusión— sobre CISA KEV y ThreatFox, y publica cada día un "
    "informe orientado a decisión. Corre solo mediante GitHub Actions y no requiere intervención."
)

DECISIONES = [
    (
        "Un indicador no evidencia una técnica.",
        "Una dirección IP no ejecuta nada: es infraestructura observada. El mapeo va de familia "
        "de malware a objeto Software de MITRE ATT&CK y de ahí a sus técnicas, y cuando un "
        "nombre resuelve a más de un objeto el sistema se abstiene en lugar de elegir el más "
        "probable. Cada mapeo declara si es derivado de datos o inferido, y su nivel de "
        "confianza.",
    ),
    (
        "Las lagunas se declaran, nunca se rellenan.",
        "Si una fuente falla, su diferencial no se calcula. Publicar «cero indicadores nuevos» "
        "cuando no se pudo mirar convierte una ausencia de observación en una observación de "
        "ausencia. El informe declara qué no pudo calcularse y por qué, incluyendo el sesgo que "
        "eso introduce.",
    ),
    (
        "El denominador es el total, no lo que mapea.",
        "Calcular el panorama de técnicas sobre la fracción de familias que sí tienen entrada en "
        "ATT&CK produciría un retrato convincente y falso, sesgado hacia el instrumental "
        "dirigido. Los porcentajes se calculan sobre el total de familias observadas y el "
        "informe lo declara en cada tabla.",
    ),
]

METRICAS = [
    (
        "No hubo convergencia, hubo agotamiento.",
        "15 de 16 pasadas de revisión sobre un mismo cambio encontraron al menos un bloqueante, "
        "y la serie no decae de forma extrapolable.",
    ),
    (
        "Casi un tercio de las correcciones introdujo un defecto propio.",
        "De forma sostenida: corregir es una zona de riesgo comparable a implementar.",
    ),
    (
        "El coste por defecto grave cayó de 25,1 a 3,7 minutos.",
        "Al acotar el corpus que lee el revisor. Es cota inferior, no medida exacta: las "
        "revisiones más caóticas no registraron duración.",
    ),
    (
        "El instrumento no se audita solo.",
        "En la última revisión, dos de cinco defectos estaban en artefactos escritos "
        "precisamente para vigilar defectos.",
    ),
]

DEFECTOS_EVITADOS = (
    "Cinco defectos detectados por este protocolo habrían llegado a producción sin fallar nunca: "
    "entre ellos, un informe declarando la desaparición del catálogo completo de vulnerabilidades "
    "explotadas activamente, y una clave de API que podía acabar escrita en un repositorio "
    "público."
)

VERIFICACION_HUMANA = (
    "Las decisiones analíticas y de diseño son humanas; la implementación la ejecutan agentes. "
    "Ese reparto solo es sostenible con verificación independiente de lo verificado."
)

#: Cifras del repositorio que **no** dependen de la ejecución diaria. Se revisan a mano cuando
#: cambian, y por eso son pocas y de grano grueso: una cifra que envejece rápido no vive aquí,
#: vive en el informe.
CIFRAS_PROYECTO = [
    ("467", "pruebas automatizadas"),
    ("2 · 1 · 0", "fuentes públicas · informe diario · intervenciones manuales"),
]

PIE = (
    "Este sitio no usa analítica, formularios ni recursos de terceros; las tipografías se sirven "
    "desde vigiabref.com y los indicadores se publican defanged."
)
