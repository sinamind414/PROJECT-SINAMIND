"""
Feedback Engine Ultra-Spécifique — Couche 3
Génère des feedbacks nommés et actionnables par verbe
"""

def generate_detailed_feedback(
    verb: str,
    task_type: str,
    structure: dict,
    doc_usage: dict,
) -> str:
    feedback_parts = []

    if task_type == "complex":
        if structure["structure_score"] < 8:
            missing = []
            if not structure["has_intro"]:
                missing.append("Introduction")
            if not structure["has_development"]:
                missing.append("Développement")
            if not structure["has_conclusion"]:
                missing.append("Conclusion")
            feedback_parts.append(
                f"Structure insuffisante. Il manque : {', '.join(missing)}."
            )
        elif structure["structure_score"] < 12:
            feedback_parts.append(
                "Structure partiellement correcte. Améliore le développement ou la conclusion."
            )
        else:
            feedback_parts.append("Bonne structure du texte scientifique.")

    if doc_usage["usage_quality"] == "none":
        feedback_parts.append("Tu n'as pas exploité les documents fournis.")
    elif doc_usage["usage_quality"] == "very_weak":
        feedback_parts.append("Tu as très peu exploité les documents.")
    elif doc_usage["usage_quality"] == "weak":
        feedback_parts.append("Tu as peu exploité les documents fournis.")

    if not feedback_parts:
        return "Réponse méthodologiquement correcte."

    return " ".join(feedback_parts)
