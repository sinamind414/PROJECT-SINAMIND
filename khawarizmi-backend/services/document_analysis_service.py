"""Service Document Analysis — évaluateur regex + intégration FSRS.

Évalue les réponses d'analyse de documents SVT en utilisant
la même logique de normalisation arabe que action_verbs_service.
"""

import re
from typing import Dict, List, Optional


# ── Normalisation arabe (identique à action_verbs_service) ──

_ARABIC_DIACRITICS = re.compile(r'[\u064B-\u0652\u0670\u0640]')
_ALEF_VARIANTS = {'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ٱ': 'ا'}
_TA_MARBUTA = re.compile(r'ة')


def normalize_arabic(text: str) -> str:
    if not text:
        return ""
    t = _ARABIC_DIACRITICS.sub('', text)
    for variant, canonical in _ALEF_VARIANTS.items():
        t = t.replace(variant, canonical)
    t = _TA_MARBUTA.sub('ه', t)
    t = t.lower().strip()
    return t


def includes_any(text: str, markers: List[str]) -> bool:
    norm = normalize_arabic(text)
    return any(normalize_arabic(m) in norm for m in markers)


def found_markers(text: str, markers: List[str]) -> List[str]:
    norm = normalize_arabic(text)
    return [m for m in markers if normalize_arabic(m) in norm]


def has_number(text: str) -> bool:
    return bool(re.search(r'[0-9\u0660-\u0669]', text))


def has_question_mark(text: str) -> bool:
    return '؟' in text or '?' in text


# ── Marqueurs par verbe ────────────────────────────

VARIATION_MARKERS = ["يزداد", "تنخفض", "ثابت", "augmente", "diminue", "يتغير",
                     "يرتفع", "ينخفض", "ارتفاع", "انخفاض"]
DOCUMENT_MARKERS = ["الوثيقة", "تمثل", "الشكل", "الجدول", "المنحنى", "الوثيقه",
                    "يمثل", "وفق"]
CAUSAL_MARKERS = ["لأن", "بسبب", "راجع", "سببه", "يفسر", "لان", "نتيجة", "نعلم"]
DEDUCTION_MARKERS = ["نستنتج", "ومنه", "يدل", "نستخلص", "اذا"]
COMPARISON_MARKERS = ["بينما", "مقارنة", "اكبر", "اقل", "مختلف", "على عكس"]
RELATION_MARKERS = ["كلما", "العلاقة", "طردية", "عكسية", "العلاقه"]
HYPOTHESIS_MARKERS = ["الفرضية", "نفترض", "قد تكون", "ربما", "الفرضيه"]
SCIENTIFIC_TEXT_MARKERS = ["نستنتج", "ومنه", "خلاصة", "في الختام", "بناء على"]


# ── Règles de scoring par verbe ────────────────────

VERB_RULES: Dict[str, Dict] = {
    "analyse": {
        "required": DOCUMENT_MARKERS + VARIATION_MARKERS,
        "forbidden": CAUSAL_MARKERS + DEDUCTION_MARKERS,
        "rules": [
            {"code": "doc_ref", "labelAr": "الإشارة إلى الوثيقة", "points": 2, "checkType": "keyword", "keywordField": "required_markers"},
            {"code": "variation", "labelAr": "ذكر التغيرات", "points": 2, "checkType": "keyword", "keywordField": "required_markers"},
            {"code": "no_causal", "labelAr": "عدم التفسير (تحليل فقط)", "points": 2, "checkType": "forbidden_absence"},
            {"code": "structure", "labelAr": "إجابة منظمة", "points": 1, "checkType": "structure"},
        ],
    },
    "interpret": {
        "required": CAUSAL_MARKERS + DOCUMENT_MARKERS,
        "forbidden": [],
        "rules": [
            {"code": "causal", "labelAr": "استعمال روابط السببية", "points": 3, "checkType": "keyword", "keywordField": "required_markers"},
            {"code": "doc_ref", "labelAr": "الإشارة إلى الوثيقة", "points": 1, "checkType": "keyword", "keywordField": "required_markers"},
            {"code": "structure", "labelAr": "إجابة منظمة", "points": 1, "checkType": "structure"},
        ],
    },
    "deduce": {
        "required": DEDUCTION_MARKERS,
        "forbidden": [],
        "rules": [
            {"code": "deduction", "labelAr": "استعمال أدوات الاستنتاج", "points": 3, "checkType": "keyword", "keywordField": "required_markers"},
            {"code": "concise", "labelAr": "إجابة مختصرة", "points": 2, "checkType": "structure"},
        ],
    },
    "justify": {
        "required": CAUSAL_MARKERS + DOCUMENT_MARKERS,
        "forbidden": [],
        "rules": [
            {"code": "causal", "labelAr": "استعمال روابط السببية", "points": 3, "checkType": "keyword", "keywordField": "required_markers"},
            {"code": "doc_ref", "labelAr": "الإشارة إلى الوثيقة", "points": 2, "checkType": "keyword", "keywordField": "required_markers"},
        ],
    },
    "hypothesis": {
        "required": HYPOTHESIS_MARKERS,
        "forbidden": [],
        "rules": [
            {"code": "hypothesis", "labelAr": "صياغة فرضية واضحة", "points": 3, "checkType": "keyword", "keywordField": "required_markers"},
            {"code": "structure", "labelAr": "إجابة منظمة", "points": 2, "checkType": "structure"},
        ],
    },
    "validate-hypothesis": {
        "required": DEDUCTION_MARKERS + CAUSAL_MARKERS,
        "forbidden": [],
        "rules": [
            {"code": "deduction", "labelAr": "استنتاج واضح", "points": 2, "checkType": "keyword", "keywordField": "required_markers"},
            {"code": "causal", "labelAr": "تعليل علمي", "points": 2, "checkType": "keyword", "keywordField": "required_markers"},
            {"code": "structure", "labelAr": "إجابة منظمة", "points": 1, "checkType": "structure"},
        ],
    },
    "discuss": {
        "required": COMPARISON_MARKERS + CAUSAL_MARKERS,
        "forbidden": [],
        "rules": [
            {"code": "comparison", "labelAr": "مقارنة وجهات النظر", "points": 3, "checkType": "keyword", "keywordField": "required_markers"},
            {"code": "causal", "labelAr": "تعليل", "points": 2, "checkType": "keyword", "keywordField": "required_markers"},
        ],
    },
    "scientific-text": {
        "required": SCIENTIFIC_TEXT_MARKERS + DEDUCTION_MARKERS,
        "forbidden": [],
        "rules": [
            {"code": "synthesis", "labelAr": "تكوين نص منسق", "points": 3, "checkType": "keyword", "keywordField": "required_markers"},
            {"code": "structure", "labelAr": "نص منظم وطويل", "points": 2, "checkType": "structure"},
        ],
    },
    "compare": {
        "required": COMPARISON_MARKERS,
        "forbidden": [],
        "rules": [
            {"code": "comparison", "labelAr": "استعمال أدوات المقارنة", "points": 3, "checkType": "keyword", "keywordField": "required_markers"},
            {"code": "structure", "labelAr": "إجابة منظمة", "points": 2, "checkType": "structure"},
        ],
    },
    "relationship": {
        "required": RELATION_MARKERS + VARIATION_MARKERS,
        "forbidden": [],
        "rules": [
            {"code": "relation", "labelAr": "تحديد نوع العلاقة", "points": 3, "checkType": "keyword", "keywordField": "required_markers"},
            {"code": "variation", "labelAr": "ذكر التغيرات", "points": 2, "checkType": "keyword", "keywordField": "required_markers"},
        ],
    },
}


# ── Évaluation ────────────────────────────────────

def evaluate_answer(
    verb_slug: str,
    answer: str,
    model_answer: Optional[str] = None,
) -> Dict:
    """Évalue une réponse d'analyse de document.

    Args:
        verb_slug: le verbe d'action (analyse, interpret, deduce, etc.)
        answer: texte de la réponse de l'élève
        model_answer: réponse modèle (pour comparaison future avec Gemini)

    Returns:
        Dict avec score, percentage, errors, success, advice, etc.
    """
    if not answer or not answer.strip():
        return {
            "question_id": "",
            "verb_slug": verb_slug,
            "score": 0,
            "score_max": _compute_score_max(verb_slug),
            "percentage": 0,
            "success": [],
            "errors": ["الإجابة فارغة. اكتب إجابتك ثم أرسلها."],
            "missing_markers": _get_required(verb_slug),
            "forbidden_found": [],
            "advice": "اكتب إجابتك كاملة قبل الإرسال.",
            "dominant_error_code": "empty_answer",
        }

    rules_def = VERB_RULES.get(verb_slug, VERB_RULES["analyse"])
    required = rules_def["required"]
    forbidden = rules_def["forbidden"]
    scoring_rules = rules_def["rules"]

    missing = [m for m in required if normalize_arabic(m) not in normalize_arabic(answer)]
    forbidden_found = [m for m in forbidden if normalize_arabic(m) in normalize_arabic(answer)]

    score = 0
    score_max = 0
    success: List[str] = []
    errors: List[str] = []

    for rule in scoring_rules:
        points = rule.get("points", 0)
        score_max += points
        check_type = rule.get("checkType", "manual")
        code = rule.get("code", "")
        label = rule.get("labelAr", code)

        passed = False

        if check_type == "keyword":
            keyword_field = rule.get("keywordField", "required_markers")
            markers = rules_def.get(keyword_field, required)
            passed = includes_any(answer, markers)
        elif check_type == "forbidden_absence":
            passed = len(forbidden_found) == 0
        elif check_type == "structure":
            min_len = 80 if verb_slug == "scientific-text" else 40
            passed = len(answer.strip()) >= min_len and not has_question_mark(answer)
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

    dominant_error = _compute_dominant_error(verb_slug, missing, forbidden_found, answer)
    advice = _build_advice(verb_slug, missing, forbidden_found, percentage)

    return {
        "question_id": "",
        "verb_slug": verb_slug,
        "score": score,
        "score_max": score_max,
        "percentage": percentage,
        "success": success,
        "errors": errors,
        "missing_markers": missing,
        "forbidden_found": forbidden_found,
        "advice": advice,
        "dominant_error_code": dominant_error,
    }


def _get_required(verb_slug: str) -> List[str]:
    rules_def = VERB_RULES.get(verb_slug, VERB_RULES["analyse"])
    return rules_def["required"]


def _compute_score_max(verb_slug: str) -> int:
    rules_def = VERB_RULES.get(verb_slug, VERB_RULES["analyse"])
    return sum(r.get("points", 0) for r in rules_def["rules"]) or 1


def _compute_dominant_error(
    verb_slug: str,
    missing: List[str],
    forbidden_found: List[str],
    answer: str,
) -> Optional[str]:
    if forbidden_found and verb_slug == "analyse":
        return "mixed_analysis_interpretation"
    if forbidden_found:
        return "forbidden_markers_used"
    if missing and verb_slug == "analyse":
        if not includes_any(answer, VARIATION_MARKERS) and not has_number(answer):
            return "missing_numerical_values"
        return "missing_document_presentation"
    if missing and verb_slug == "hypothesis":
        return "weak_hypothesis"
    if missing and verb_slug == "scientific-text":
        return "missing_synthesis"
    if missing and verb_slug == "deduce":
        return "deduction_too_long"
    if missing:
        return "missing_required_markers"
    return None


def _build_advice(
    verb_slug: str,
    missing: List[str],
    forbidden_found: List[str],
    percentage: int,
) -> str:
    if percentage >= 85:
        return "أحسنت! إجابتك تتوافق مع منهجية تحليل الوثائق. واصل التدريب."

    parts: List[str] = []
    if missing:
        parts.append(f"أضف الكلمات المفتاحية الناقصة: {', '.join(missing[:3])}")
    if forbidden_found:
        parts.append(f"تجنب الكلمات الممنوعة: {', '.join(forbidden_found[:3])}")
    if not parts:
        parts.append("راجع منهجية الفعل وحاول مرة أخرى.")

    return " | ".join(parts)


# ── Conversion score → rating FSRS ────────────────

def score_to_fsrs_rating(percentage: int) -> int:
    """Convertit un pourcentage en rating FSRS (1-4)."""
    if percentage >= 90:
        return 4
    if percentage >= 75:
        return 3
    if percentage >= 50:
        return 2
    return 1
