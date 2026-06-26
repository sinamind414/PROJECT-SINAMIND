"""
Analyseur de structure texte scientifique — Couche 3
Bac Blanc Intelligent V2

Vérifie si l'élève a structuré sa réponse en parties
(logique Introduction → Développement → Conclusion).
"""
from __future__ import annotations

# Mots-indicateurs de chaque partie structurelle
_INTRO_MARKERS: list[str] = [
    "مقدمة",
    "المشكل",
    "المشكلة",
    "يهدف",
    "الهدف من",
    "نقرأ في",
    "وفقاً لـ",
    "بناءً على",
]

_DEV_MARKERS: list[str] = [
    "عرض",
    "تطوير",
    "من خلال",
    "بواسطة",
    "نجد أن",
    "نلاحظ",
    "تشير البيانات",
    "تبين النتائج",
    "حسب الوثيقة",
    "بناءً على",
]

_CONCLUSION_MARKERS: list[str] = [
    "خاتمة",
    "إذن",
    "نستنتج",
    "نتيجة",
    "النتيجة",
    "归纳",
    "باختصار",
    "مما سبق",
]


def _has_marker(text: str, markers: list[str]) -> bool:
    """Vérifie si au moins un marqueur est présent dans le texte."""
    return any(marker in text for marker in markers)


def analyze_text_structure(answer: str) -> dict:
    """
    Analyse la structure du texte scientifique de la réponse.

    Score maximum = 16 points :
      - Introduction : 4 pts
      - Développement : 8 pts
      - Conclusion : 4 pts

    Args:
        answer: Réponse textuelle de l'élève

    Returns:
        dict avec keys :
            structure_score, has_intro, has_development,
            has_conclusion, feedback
    """
    has_intro = _has_marker(answer, _INTRO_MARKERS)
    has_development = _has_marker(answer, _DEV_MARKERS)
    has_conclusion = _has_marker(answer, _CONCLUSION_MARKERS)

    score = 0
    if has_intro:
        score += 4
    if has_development:
        score += 8
    if has_conclusion:
        score += 4

    return {
        "structure_score": score,
        "has_intro": has_intro,
        "has_development": has_development,
        "has_conclusion": has_conclusion,
        "feedback": _generate_structure_feedback(
            has_intro, has_development, has_conclusion
        ),
    }


def _generate_structure_feedback(
    has_intro: bool,
    has_development: bool,
    has_conclusion: bool,
) -> str:
    """Génère un feedback ciblé sur les lacunes structurelles."""
    missing: list[str] = []
    if not has_intro:
        missing.append("une introduction claire (problématique ou objectif)")
    if not has_development:
        missing.append("un développement structuré (analyse / preuves)")
    if not has_conclusion:
        missing.append("une conclusion (synthèse ou résultat)")

    if not missing:
        return "Structure méthodologiquement correcte."

    return (
        "Ta réponse manque de : " + ", ".join(missing) + ". "
        "Pour les tâches complexes, la structure "
        "Introduction → Développement → Conclusion est indispensable."
    )
