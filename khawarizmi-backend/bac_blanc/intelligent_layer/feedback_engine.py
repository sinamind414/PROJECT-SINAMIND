"""
Moteur de feedback ultra-spécifique — Couche 3
Bac Blanc Intelligent V2

Génère des retours ciblés, actionnables et bienveillants
en fonction de l'analyse complète de la réponse.
"""
from __future__ import annotations

from typing import Any


def generate_feedback(
    verb_info: dict[str, Any],
    task_type: str,
    structure: dict[str, Any],
    doc_usage: dict[str, Any],
    keyword_usage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Génère un feedback structuré ultra-spécifique.

    Args:
        verb_info: Sortie de detect_verb()
        task_type: "simple" ou "complex"
        structure: Sortie de analyze_text_structure()
        doc_usage: Sortie de analyze_document_usage()
        keyword_usage: Sortie de extract_keywords() (optionnel)

    Returns:
        dict avec keys :
            alert_level, message, strengths, weaknesses,
            recommendation
    """
    strengths: list[str] = []
    weaknesses: list[str] = []
    recommendation_parts: list[str] = []

    alert_level = "info"  # info | warning | danger

    verb = verb_info.get("verb", "inconnu")

    # --- Vérification 1 : Tâche complexe sans structure ---
    if task_type == "complex" and structure["structure_score"] < 10:
        alert_level = "warning"
        weaknesses.append(
            f"Réponse non structurée pour le verbe '{verb}' "
            f"(tâche complexe)"
        )
        recommendation_parts.append(
            "Structure ta réponse en 3 parties : "
            "Introduction → Développement → Conclusion"
        )

    # --- Vérification 2 : Exploitation documents faible ---
    if doc_usage["usage_quality"] in ("weak", "very_weak", "none"):
        alert_level = "danger" if alert_level == "danger" else "warning"
        weaknesses.append(
            "Exploitation insuffisante des documents fournis"
        )
        recommendation_parts.append(
            "Relis les documents et identifie les données clés "
            "à intégrer dans ta réponse"
        )

    # --- Vérification 3 : Structure correcte ---
    if structure["structure_score"] >= 12:
        strengths.append("Bonne structuration de la réponse")

    # --- Vérification 4 : Documents bien exploités ---
    if doc_usage["usage_quality"] in ("excellent", "good"):
        strengths.append("Exploitation correcte des documents")

    # --- Vérification 5 : Mots-clés ---
    if keyword_usage:
        if keyword_usage.get("keyword_quality") == "good":
            strengths.append("Utilisation des termes scientifiques")
        elif keyword_usage.get("keyword_quality") in ("weak", "none"):
            weaknesses.append("Peu de termes scientifiques utilisés")
            recommendation_parts.append(
                "Utilise les termes clés du programme : "
                + ", ".join(keyword_usage.get("missing_keywords", [])[:3])
            )

    # --- Message principal ---
    message = _build_main_message(
        verb, task_type, structure, doc_usage, alert_level
    )

    # --- Recommandation globale ---
    recommendation = (
        " ; ".join(recommendation_parts)
        if recommendation_parts
        else "Continue comme ça !"
    )

    return {
        "alert_level": alert_level,
        "message": message,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendation": recommendation,
    }


def _build_main_message(
    verb: str,
    task_type: str,
    structure: dict,
    doc_usage: dict,
    alert_level: str,
) -> str:
    """Construit le message principal du feedback."""
    if alert_level == "danger":
        return (
            f"Alerte : ta réponse au verbe '{verb}' présente "
            f"des lacunes méthodologiques importantes. "
            f"Consulte la fiche méthodologique correspondante."
        )
    if alert_level == "warning":
        return (
            f"Ta réponse au verbe '{verb}' est sur la bonne voie "
            f"mais nécessite des améliorations méthodologiques."
        )
    return (
        f"Bon travail sur le verbe '{verb}'. "
        f"Ta réponse est méthodologiquement correcte."
    )
