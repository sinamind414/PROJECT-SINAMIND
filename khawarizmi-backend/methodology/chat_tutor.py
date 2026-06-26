"""
Tuteur Méthodologique — Mode dédié dans le chat
"""

from .tutor_prompts import get_verb_explanation
from .evaluator import evaluate_methodology


async def tutor_methodology_mode(
    instruction: str,
    student_answer: str = "",
    mode: str = "explain",
) -> dict:
    verb_info = get_verb_explanation(instruction)

    if mode == "explain":
        return {
            "mode": "explain",
            "verb": instruction,
            "explanation": verb_info,
            "message": f"Le verbe '{instruction}' signifie : {verb_info['definition']}",
        }

    elif mode == "correct":
        if not student_answer:
            return {"error": "Réponse élève requise pour la correction"}
        evaluation = await evaluate_methodology(
            context="",
            instruction=instruction,
            student_answer=student_answer,
        )
        return {
            "mode": "correct",
            "evaluation": evaluation,
            "message": evaluation.get("feedback", {}).get("message", ""),
        }

    elif mode == "diagnose":
        return {
            "mode": "diagnose",
            "message": "Mode diagnostic en cours de développement",
        }

    return {"error": "Mode inconnu"}
