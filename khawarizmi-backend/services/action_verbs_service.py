"""Service Action Verbs — évaluateur Python + intégration FSRS.

Port de methodology-evaluator.ts côté backend.
"""

import re

# ── Normalisation arabe ───────────────────────────

_ARABIC_DIACRITICS = re.compile(r"[\u064B-\u0652\u0670\u0640]")
_ALEF_VARIANTS = {"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا"}
_TA_MARBUTA = re.compile(r"ة")


def normalize_arabic(text: str) -> str:
    """Normalise le texte arabe : supprime diacritiques, unifie alef, ta-marbuta→ha."""
    if not text:
        return ""
    t = _ARABIC_DIACRITICS.sub("", text)
    for variant, canonical in _ALEF_VARIANTS.items():
        t = t.replace(variant, canonical)
    t = _TA_MARBUTA.sub("ه", t)
    t = t.lower().strip()
    return t


def includes_any(text: str, markers: list[str]) -> bool:
    """Vérifie si au moins un marqueur est présent dans le texte normalisé."""
    norm = normalize_arabic(text)
    return any(normalize_arabic(m) in norm for m in markers)


def found_markers(text: str, markers: list[str]) -> list[str]:
    """Retourne les marqueurs présents dans le texte."""
    norm = normalize_arabic(text)
    return [m for m in markers if normalize_arabic(m) in norm]


def has_number(text: str) -> bool:
    return bool(re.search(r"[0-9\u0660-\u0669]", text))


def has_question_mark(text: str) -> bool:
    return "؟" in text or "?" in text


# ── Marqueurs par verbe ───────────────────────────

VARIATION_MARKERS = ["يزداد", "تنخفض", "ثابت", "augmente", "diminue", "يتغير"]
DOCUMENT_MARKERS = ["الوثيقة", "تمثل", "الشكل", "الجدول", "المنحنى", "الوثيقه"]
CAUSAL_MARKERS = ["لأن", "بسبب", "راجع", "سببه", "يفسر", "لان", "بسبب"]
DEDUCTION_MARKERS = ["نستنتج", "ومنه", "يدل", "نستخلص", "اذا"]
COMPARISON_MARKERS = ["بينما", "مقارنة", "اكبر", "اقل", "مختلف"]
RELATION_MARKERS = ["كلما", "العلاقة", "طردية", "عكسية", "العلاقه"]


# ── Évaluation ────────────────────────────────────


def evaluate_answer(
    verb: dict,
    answer: str,
) -> dict:
    """Évalue la réponse d'un élève pour un verbe donné.

    Args:
        verb: dictionnaire avec les champs de la table action_verbs
        answer: texte de la réponse de l'élève

    Returns:
        Dict avec score, percentage, errors, success, advice, etc.
    """
    if not answer or not answer.strip():
        return {
            "verb_slug": verb["slug"],
            "score": 0,
            "score_max": _compute_score_max(verb),
            "percentage": 0,
            "success": [],
            "errors": ["الإجابة فارغة. اكتب إجابتك ثم أرسلها."],
            "missing_markers": verb.get("required_markers", []),
            "forbidden_found": [],
            "advice": "اكتب إجابتك كاملة قبل الإرسال.",
            "dominant_error_code": "empty_answer",
            "allow_second_attempt": True,
        }

    required = verb.get("required_markers", [])
    forbidden = verb.get("forbidden_markers", [])
    scoring_rules = verb.get("scoring_rules", [])

    missing = [m for m in required if normalize_arabic(m) not in normalize_arabic(answer)]
    forbidden_found = [m for m in forbidden if normalize_arabic(m) in normalize_arabic(answer)]

    score = 0
    score_max = 0
    success: list[str] = []
    errors: list[str] = []

    for rule in scoring_rules:
        points = rule.get("points", 0)
        score_max += points
        check_type = rule.get("checkType", "manual")
        code = rule.get("code", "")
        label = rule.get("labelAr", code)

        passed = False

        if check_type == "keyword":
            keyword_field = rule.get("keywordField", "required_markers")
            markers = verb.get(keyword_field, required)
            passed = includes_any(answer, markers)
        elif check_type == "forbidden_absence":
            passed = len(forbidden_found) == 0
        elif check_type == "structure":
            passed = len(answer.strip()) >= 50 and not has_question_mark(answer)
        else:
            passed = len(missing) == 0

        if passed:
            score += points
            success.append(f"✅ {label} (+{points})")
        else:
            errors.append(f"❌ {label} (0/{points})")

    if forbidden_found:
        penalty = min(len(forbidden_found) * 2, score)
        score = max(0, score - penalty)
        errors.append(f"⚠️ استعملت كلمات ممنوعة: {', '.join(forbidden_found)} (-{penalty})")

    score_max = max(score_max, 1)
    percentage = round((score / score_max) * 100)

    dominant_error = _compute_dominant_error(verb, missing, forbidden_found, answer)
    advice = _build_advice(verb, missing, forbidden_found, percentage)
    allow_second = percentage < 85

    return {
        "verb_slug": verb["slug"],
        "score": score,
        "score_max": score_max,
        "percentage": percentage,
        "success": success,
        "errors": errors,
        "missing_markers": missing,
        "forbidden_found": forbidden_found,
        "advice": advice,
        "dominant_error_code": dominant_error,
        "allow_second_attempt": allow_second,
    }


def _compute_score_max(verb: dict) -> int:
    rules = verb.get("scoring_rules", [])
    return sum(r.get("points", 0) for r in rules) or 1


def _compute_dominant_error(
    verb: dict,
    missing: list[str],
    forbidden_found: list[str],
    answer: str,
) -> str | None:
    slug = verb["slug"]

    if forbidden_found and slug == "analyse":
        return "mixed_analysis_interpretation"
    if forbidden_found and slug == "interpret":
        return "wrong_scientific_causality"
    if missing and slug == "analyse":
        if not includes_any(answer, VARIATION_MARKERS) and not has_number(answer):
            return "missing_numerical_values"
        return "missing_document_presentation"
    if missing and slug == "hypothesis":
        return "weak_hypothesis"
    if missing and slug == "scientific-text":
        return "missing_problematic"
    if missing and slug == "deduce":
        return "deduction_too_long"
    if forbidden_found:
        return "mixed_analysis_interpretation"
    return None


def _build_advice(
    verb: dict,
    missing: list[str],
    forbidden_found: list[str],
    percentage: int,
) -> str:
    template = verb.get("feedback_template_ar", "")
    slug = verb["slug"]

    if percentage >= 85:
        return f"أحسنت! إجابتك تتوافق مع منهجية فعل «{verb.get('ar', slug)}». واصل التدريب على أفعال أخرى."

    parts: list[str] = []
    if missing:
        parts.append(f"أضف الكلمات المفتاحية الناقصة: {', '.join(missing[:3])}")
    if forbidden_found:
        parts.append(f"تجنب الكلمات الممنوعة: {', '.join(forbidden_found[:3])}")
    if template:
        parts.append(f"الصيغة المعيارية: {template}")

    return " | ".join(parts) if parts else "راجع منهجية الفعل وحاول مرة أخرى."


# ── Conversion score → rating FSRS ────────────────


def score_to_fsrs_rating(percentage: int) -> int:
    """Convertit un pourcentage en rating FSRS (1-4)."""
    if percentage >= 90:
        return 4  # easy
    if percentage >= 75:
        return 3  # good
    if percentage >= 50:
        return 2  # hard
    return 1  # again
