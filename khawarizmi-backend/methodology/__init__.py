"""
Methodology Evaluator V2 — Moteur méthodologique central
Évaluation intelligente des réponses Bac SVT Algérie.
"""
from .evaluator import evaluate_methodology
from .verb_database import get_verb, get_all_verbs, VERB_DATABASE
from .task_classifier import classify_task
from .feedback_generator import generate_feedback
from .text_structure_validator import validate_text_structure
from .diagnostic import diagnose_methodology_level, ERROR_PROFILES

__all__ = [
    "evaluate_methodology",
    "get_verb",
    "get_all_verbs",
    "VERB_DATABASE",
    "classify_task",
    "generate_feedback",
    "validate_text_structure",
    "diagnose_methodology_level",
    "ERROR_PROFILES",
]
