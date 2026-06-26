"""Feedback structure apres exercice — Bac Blanc Intelligent"""

from typing import Dict, Any
from .evaluator import evaluate_methodology
from .diagnostic import generate_diagnostic_report


async def generate_bac_blanc_structured_feedback(
    context: str,
    instruction: str,
    student_answer: str,
    documents: list = None,
    previous_answers: list = None
) -> Dict[str, Any]:
    if documents is None:
        documents = []
    if previous_answers is None:
        previous_answers = []

    methodo = await evaluate_methodology(
        context=context,
        instruction=instruction,
        student_answer=student_answer,
        documents=documents
    )

    diagnostic = generate_diagnostic_report(
        verb=methodo.get("verb", ""),
        task_type=methodo.get("task_type", "simple"),
        structure=methodo.get("structure", {}),
        doc_usage=methodo.get("document_usage", {}),
        student_answer=student_answer,
        previous_answers=previous_answers
    )

    return {
        "verb": methodo.get("verb"),
        "score_methodologie": methodo.get("score"),
        "max_score": methodo.get("max_score"),
        "structure_feedback": methodo.get("feedback", {}).get("message", ""),
        "document_feedback": diagnostic.get("document_usage", {}),
        "error_profiles": diagnostic.get("error_profiles", []),
        "maturity_level": diagnostic.get("maturity_level"),
        "recommendations": diagnostic.get("recommendations", []),
        "detailed_feedback": methodo.get("feedback", {})
    }
