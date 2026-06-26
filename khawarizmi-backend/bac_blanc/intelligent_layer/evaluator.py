"""
Évaluateur intelligent — Point d'entrée Couche 3
Bac Blanc Intelligent V2

Orchestre l'ensemble des analyseurs pour produire
une évaluation méthodologique complète.
"""
from __future__ import annotations

from typing import Any

from .verb_detector import detect_verb
from .task_classifier import classify_task
from .text_structure_analyzer import analyze_text_structure
from .document_usage_analyzer import analyze_document_usage
from .feedback_engine import generate_feedback


def evaluate_answer(
    instruction: str,
    answer: str,
    documents: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Évalue la réponse d'un élève sur une consigne Bac Blanc.

    Pipeline Couche 3 :
        1. Détection du verbe d'action
        2. Classification de la tâche
        3. Analyse de la structure texte
        4. Analyse de l'exploitation des documents
        5. Génération du feedback ultra-spécifique

    Args:
        instruction: Texte de la consigne
        answer: Réponse de l'élève
        documents: Liste des documents fournis (optionnel)

    Returns:
        dict complet de l'évaluation méthodologique
    """
    documents = documents or []

    # Étape 1 : Détection du verbe
    verb_info = detect_verb(instruction)

    # Étape 2 : Classification de la tâche
    task_type = classify_task(instruction, verb_info)

    # Étape 3 : Analyse de la structure
    structure = analyze_text_structure(answer)

    # Étape 4 : Analyse de l'exploitation des documents
    doc_usage = analyze_document_usage(answer, documents)

    # Étape 5 : Feedback
    feedback = generate_feedback(
        verb_info=verb_info,
        task_type=task_type,
        structure=structure,
        doc_usage=doc_usage,
    )

    # Score méthodologique global (sur 100)
    methodology_score = _compute_methodology_score(
        verb_info, task_type, structure, doc_usage
    )

    return {
        "verb": verb_info,
        "task_type": task_type,
        "structure": structure,
        "document_usage": doc_usage,
        "feedback": feedback,
        "methodology_score": methodology_score,
    }


def _compute_methodology_score(
    verb_info: dict,
    task_type: str,
    structure: dict,
    doc_usage: dict,
) -> int:
    """
    Calcule un score méthodologique global sur 100.

    Répartition :
      - Structure (max 40 pts) : proportionnelle au score structure
      - Documents (max 40 pts) : selon la qualité d'exploitation
      - Adéquation verbe (max 20 pts) : bonus si la tâche est
        traitée à la bonne hauteur
    """
    # Score structure (0-40)
    struct_ratio = structure["structure_score"] / 16  # max 16
    struct_score = int(struct_ratio * 40)

    # Score documents (0-40)
    doc_quality_map = {
        "excellent": 40,
        "good": 30,
        "weak": 15,
        "very_weak": 5,
        "none": 0,
    }
    doc_score = doc_quality_map.get(doc_usage["usage_quality"], 0)

    # Score adéquation verbe (0-20)
    adequacy_score = 20  # Par défaut, la tâche est bien traitée
    if task_type == "complex" and structure["structure_score"] < 8:
        adequacy_score = 5
    elif task_type == "complex" and structure["structure_score"] < 12:
        adequacy_score = 12

    return min(100, struct_score + doc_score + adequacy_score)
