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
        if not student_answer:
            return {"error": "Réponse élève requise pour le diagnostic"}
        evaluation = await evaluate_methodology(
            context="",
            instruction=instruction,
            student_answer=student_answer,
        )
        verb_info = get_verb_explanation(instruction)
        return {
            "mode": "diagnose",
            "verb": instruction,
            "verb_expected": verb_info,
            "task_type": evaluation.get("task_type", "unknown"),
            "structure": evaluation.get("structure", {}),
            "document_usage": evaluation.get("document_usage", {}),
            "score": evaluation.get("score", 0),
            "max_score": evaluation.get("max_score", 10),
            "feedback": evaluation.get("feedback", {}),
            "message": (
                f"Diagnostic du verbe '{instruction}' — "
                f"Score : {evaluation.get('score', 0)}/{evaluation.get('max_score', 10)}"
            ),
        }

    return {"error": "Mode inconnu"}
