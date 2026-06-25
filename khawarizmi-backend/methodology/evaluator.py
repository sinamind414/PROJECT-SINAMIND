"""
Évaluateur méthodologique principal — Methodology Evaluator V2

Orchestre l'ensemble des moteurs pour une évaluation complète.
"""
from __future__ import annotations

from typing import Any

from .verb_database import get_verb, get_verb_by_id
from .task_classifier import classify_task
from .text_structure_validator import validate_text_structure
from .feedback_generator import generate_feedback


async def evaluate_methodology(
    context: str,
    instruction: str,
    student_answer: str,
    documents: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Évalue la réponse d'un élève sur une consigne Bac Blanc.

    Pipeline Methodology Evaluator V2 :
        1. Identifier le verbe principal
        2. Classifier la tâche (simple/complexe)
        3. Valider la structure (si tâche complexe)
        4. Analyser l'exploitation des documents
        5. Générer le feedback ultra-spécifique

    Args:
        context: Contexte de l'exercice
        instruction: Instruction donnée à l'élève
        student_answer: Réponse de l'élève
        documents: Documents fournis (optionnel)

    Returns:
        dict complet de l'évaluation méthodologique
    """
    documents = documents or []

    # 1. Identifier le verbe principal
    verb_info = get_verb(instruction)
    if not verb_info:
        verb_info = {
            "arabic": "unknown",
            "french": "inconnu",
            "type": "simple",
            "max_score": 10,
            "criteria": [],
            "common_mistakes": [],
        }

    # 2. Classifier la tâche
    task_type = classify_task(instruction, verb_info)

    # 3. Valider la structure (tâches complexes)
    structure = {"structure_score": 0, "has_intro": False, "has_development": False, "has_conclusion": False}
    if task_type == "complex":
        structure = validate_text_structure(student_answer)

    # 4. Analyser l'exploitation des documents
    doc_usage = _analyze_doc_usage(student_answer, documents)

    # 5. Générer le feedback
    feedback = generate_feedback(
        verb_info=verb_info,
        task_type=task_type,
        student_answer=student_answer,
        structure_score=structure["structure_score"],
        doc_usage_quality=doc_usage["usage_quality"],
    )

    return {
        "verb": verb_info["arabic"],
        "verb_info": verb_info,
        "task_type": task_type,
        "structure": structure,
        "document_usage": doc_usage,
        "score": feedback["score"],
        "max_score": feedback["max_score"],
        "feedback": feedback,
    }


def _analyze_doc_usage(
    answer: str,
    documents: list[dict[str, Any]],
) -> dict[str, Any]:
    """Analyse l'exploitation des documents fournis."""
    if not documents:
        return {"documents_used": 0, "total_documents": 0, "usage_quality": "none"}

    refs = 0
    for doc in documents:
        if doc.get("id") and str(doc["id"]) in answer:
            refs += 1
        if doc.get("key_element") and doc["key_element"] in answer:
            refs += 1

    ratio = refs / len(documents) if documents else 0
    if ratio >= 1.5:
        quality = "excellent"
    elif ratio >= 1.0:
        quality = "good"
    elif ratio >= 0.5:
        quality = "weak"
    else:
        quality = "very_weak" if ratio > 0 else "none"

    return {
        "documents_used": sum(1 for d in documents if d.get("key_element", "") in answer),
        "total_documents": len(documents),
        "usage_quality": quality,
    }
