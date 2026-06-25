import re

INTRO_PATTERNS = [
    r"(?:يهدف|يتمثل|المشكلة|المطروح|نسأل|نطرح|يتعلق الأمر)",
    r"(?:le probl[èe]me|il s'agit|nous nous demandons|cet exercice)",
    r"(?:من خلال|بالنظر|على ضوء)",
]

DEV_PATTERNS = [
    r"(?:أولا|أولاً|ثانيا|ثانياً|ثالثا|ثالثاً|من جهة|من ناحية)",
    r"(?:d'une part|d'autre part|premièrement|deuxièmement|en premier)",
    r"(?:لأن|بسبب|راجع|يفسر|يدل|نستنتج|ومنه|بينما)",
]

CONCLUSION_PATTERNS = [
    r"(?:نستنتج|نخلص|الخلاصة|إذن|وبالتالي|نهائيا|في الأخير|أخيرا|أخيراً)",
    r"(?:en conclusion|pour conclure|finalement|ainsi|donc|par conséquent)",
    r"(?:نستنتج|ومنه نستنتج|نستخلص)",
]

ARGUMENT_PATTERNS = [
    r"(?:لأن|بسبب|حيث|بما أن|بما ان)",
    r"(?:car|parce que|puisque|étant donné)",
    r"(?:يدل|يثبت|يبرهن|يؤكد)",
]


def has_introduction(text: str) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in INTRO_PATTERNS)


def has_development(text: str) -> bool:
    score = 0
    for p in DEV_PATTERNS:
        if re.search(p, text, re.IGNORECASE):
            score += 1
    return score >= 1


def has_conclusion(text: str) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in CONCLUSION_PATTERNS)


def has_argumentation(text: str) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in ARGUMENT_PATTERNS)


def has_explanation(text: str) -> bool:
    causal = any(re.search(p, text, re.IGNORECASE) for p in CAUSAL_PATTERNS)
    sci_terms = bool(re.search(r"(?:caractérisé|constitué|formé|composé|contient|présente)", text, re.IGNORECASE))
    return causal or sci_terms


def has_analysis(text: str) -> bool:
    patterns = [
        r"(?:d'un côté|d'un autre côté|par contre|en revanche)",
        r"(?:من جهة|من ناحية أخرى|بالمقابل)",
        r"(?:cependant|toutefois|néanmoins)",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def has_position(text: str) -> bool:
    patterns = [
        r"(?:je pense|à mon avis|selon moi|nous pensons)",
        r"(?:أعتقد|برأيي|حسب رأيي|نظن)",
        r"(?:nous adoptons|notre position)",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def has_justification(text: str) -> bool:
    score = 0
    for p in ARGUMENT_PATTERNS + CAUSAL_PATTERNS:
        if re.search(p, text, re.IGNORECASE):
            score += 1
    return score >= 2


CAUSAL_PATTERNS = [r"(?:لأن|بسبب|راجع|سببه|يفسر|لان)", r"(?:car|parce que|puisque|en raison de)"]

STRUCTURE_VALIDATORS = {
    "introduction": has_introduction,
    "development": has_development,
    "conclusion": has_conclusion,
    "argumentation": has_argumentation,
    "explanation": has_explanation,
    "analysis": has_analysis,
    "position": has_position,
    "justification": has_justification,
}


def validate_structure(text: str, required_parts: list[str]) -> dict:
    results = {}
    score = 0
    total = len(required_parts) if required_parts else 1

    if not required_parts:
        return {"parts": {}, "score": 1.0, "total": 1, "found": 1}

    for part in required_parts:
        validator = STRUCTURE_VALIDATORS.get(part)
        if validator:
            found = validator(text)
            results[part] = found
            if found:
                score += 1

    return {
        "parts": results,
        "score": score / total if total > 0 else 1.0,
        "total": total,
        "found": score,
    }
