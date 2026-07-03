"""
Methodology Evaluator V2 — Moteur méthodologique central
Évaluation intelligente des réponses Bac SVT Algérie.
"""
from .diagnostic import ERROR_PROFILES, diagnose_methodology_level
from .evaluator import evaluate_methodology
from .feedback_generator import generate_feedback
from .task_classifier import classify_task
from .text_structure_validator import validate_text_structure
from .verb_database import VERB_DATABASE, get_all_verbs, get_verb

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
