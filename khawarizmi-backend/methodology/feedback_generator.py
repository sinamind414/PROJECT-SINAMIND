"""
Générateur de feedback ultra-spécifique — Methodology Evaluator V2

Templates de feedback par verbe, avec forces, faiblesses, recommandations.
"""
from __future__ import annotations

from typing import Any

from .verb_database import get_verb


def generate_feedback(
    verb_info: dict[str, Any],
    task_type: str,
    student_answer: str,
    structure_score: int = 0,
    structure_max: int = 16,
    doc_usage_quality: str = "unknown",
) -> dict[str, Any]:
    """
    Génère un feedback structuré ultra-spécifique.

    Args:
        verb_info: Sortie de get_verb()
        task_type: "simple" ou "complex"
        student_answer: Réponse de l'élève
        structure_score: Score de structure (0-16)
        structure_max: Score max de structure
        doc_usage_quality: Qualité d'exploitation des documents

    Returns:
        dict avec keys :
            verb, task_type, score, max_score, message,
            strengths, weaknesses, recommendation
    """
    verb_arabic = verb_info.get("arabic", "inconnu")
    verb_french = verb_info.get("french", "")
    max_score = verb_info.get("max_score", 10)
    criteria = verb_info.get("criteria", [])
    common_mistakes = verb_info.get("common_mistakes", [])

    strengths: list[str] = []
    weaknesses: list[str] = []
    recommendation_parts: list[str] = []

    # --- Analyse de la structure (tâches complexes) ---
    if task_type == "complex":
        if structure_score >= 12:
            strengths.append("Bonne structuration de la réponse")
        elif structure_score >= 8:
            weaknesses.append("Structure partielle (introduction ou conclusion manquante)")
            recommendation_parts.append("Complète la structure : Introduction → Développement → Conclusion")
        else:
            weaknesses.append("Absence de structure scientifique")
            recommendation_parts.append("Pour ce type de tâche, structure ta réponse en 3 parties")

    # --- Analyse des documents ---
    if doc_usage_quality in ("excellent", "good"):
        strengths.append("Exploitation correcte des documents")
    elif doc_usage_quality in ("weak", "very_weak", "none"):
        weaknesses.append("Exploitation insuffisante des documents fournis")
        recommendation_parts.append("Relis les documents et identifie les données clés")

    # --- Évaluation du contenu ---
    answer_length = len(student_answer.split())
    if answer_length < 10:
        weaknesses.append("Réponse trop courte")
        recommendation_parts.append("Développe davantage ta réponse avec des arguments")
    elif answer_length > 100:
        strengths.append("Réponse développée")

    # --- Score final ---
    score = _compute_score(
        verb_info, task_type, structure_score, doc_usage_quality, answer_length
    )

    # --- Message principal ---
    message = _build_message(verb_arabic, task_type, score, max_score, weaknesses)

    # --- Recommandation ---
    recommendation = (
        " ; ".join(recommendation_parts)
        if recommendation_parts
        else "Continue comme ça !"
    )

    return {
        "verb": verb_arabic,
        "verb_french": verb_french,
        "task_type": task_type,
        "score": score,
        "max_score": max_score,
        "message": message,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendation": recommendation,
        "criteria": criteria,
        "common_mistakes": common_mistakes,
    }


def _compute_score(
    verb_info: dict,
    task_type: str,
    structure_score: int,
    doc_usage_quality: str,
    answer_length: int,
) -> int:
    """Calcule un score sur le max du verbe."""
    max_score = verb_info.get("max_score", 10)

    # Base : 50% si réponse non vide
    base = max_score * 0.3 if answer_length < 5 else max_score * 0.5

    # Bonus structure (tâches complexes)
    struct_bonus = 0
    if task_type == "complex":
        struct_ratio = structure_score / 16
        struct_bonus = max_score * 0.3 * struct_ratio

    # Bonus documents
    doc_map = {"excellent": 0.2, "good": 0.15, "weak": 0.05, "very_weak": 0.02, "none": 0}
    doc_bonus = max_score * doc_map.get(doc_usage_quality, 0)

    return min(max_score, int(base + struct_bonus + doc_bonus))


def _build_message(
    verb: str,
    task_type: str,
    score: int,
    max_score: int,
    weaknesses: list[str],
) -> str:
    """Construit le message principal du feedback."""
    ratio = score / max_score if max_score > 0 else 0

    if ratio >= 0.8:
        return (
            f"Excellente réponse au verbe '{verb}'. "
            f"Ta réponse est méthodologiquement solide."
        )
    if ratio >= 0.5:
        return (
            f"Bonne réponse au verbe '{verb}'. "
            f"Quelques améliorations méthodologiques sont possibles."
        )
    if weaknesses:
        return (
            f"Ta réponse au verbe '{verb}' présente des lacunes. "
            f"{' '.join(weaknesses[:2])}"
        )
    return (
        f"Ta réponse au verbe '{verb}' nécessite des améliorations."
    )
