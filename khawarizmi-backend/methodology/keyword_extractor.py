import re

SCIENCE_KEYWORDS = {
    "sciences_naturelles": [
        "cellule",
        "ADN",
        "ARN",
        "gène",
        "chromosome",
        "mitose",
        "méiose",
        "division",
        "repli",
        "protéine",
        "enzyme",
        "métabolisme",
        "écosystème",
        "biodiversité",
        "évolution",
        "immunité",
        "anticorps",
        "antigène",
        "photosynthèse",
        "respiration cellulaire",
    ],
    "physique": [
        "énergie",
        "force",
        "vitesse",
        "accélération",
        "tension",
        "courant",
        "résistance",
        "onde",
        "fréquence",
        "amplitude",
        "rayonnement",
        "radioactivité",
    ],
    "chimie": [
        "molécule",
        "atome",
        "ion",
        "réaction",
        "équilibre",
        "catalyseur",
        "pH",
        "oxydation",
        "réduction",
    ],
}

CONTEXTUAL_KEYWORDS = [
    "يهدف",
    "نستنتج",
    "نخلص",
    "نلاحظ",
    "المشكل",
    "الفرضية",
    "التجربة",
    "النتيجة",
    "le problème",
    "la conclusion",
    "l'hypothèse",
]


def extract_keywords(text: str, domain: str | None = None) -> dict:
    if not text:
        return {
            "found": [],
            "count": 0,
            "domains_detected": [],
            "completeness": 0,
        }

    found = []
    detected_domains = []

    if domain and domain in SCIENCE_KEYWORDS:
        keywords = SCIENCE_KEYWORDS[domain]
        for kw in keywords:
            if re.search(re.escape(kw), text, re.IGNORECASE):
                found.append(kw)
        detected_domains.append(domain)
    else:
        for dom, keywords in SCIENCE_KEYWORDS.items():
            dom_found = 0
            for kw in keywords:
                if re.search(re.escape(kw), text, re.IGNORECASE):
                    found.append(kw)
                    dom_found += 1
            if dom_found > 0:
                detected_domains.append(dom)

    contextual = 0
    for kw in CONTEXTUAL_KEYWORDS:
        if kw in text:
            contextual += 1

    total_possible = len(SCIENCE_KEYWORDS.get(domain or "", [])) or sum(len(v) for v in SCIENCE_KEYWORDS.values())

    return {
        "found": found,
        "count": len(found),
        "contextual_markers": contextual,
        "domains_detected": detected_domains,
        "completeness": round(len(found) / total_possible * 100, 1) if total_possible else 0,
    }


def extract_keywords_from_context(instruction: str, context: str = "") -> dict:
    full_text = f"{instruction} {context}".strip()
    return extract_keywords(full_text)
