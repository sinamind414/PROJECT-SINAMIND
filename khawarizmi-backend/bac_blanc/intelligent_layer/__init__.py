"""
Bac Blanc Intelligent — Couche 3
Évaluation méthodologique intelligente pour le Bac SVT.
"""
from .evaluator import evaluate_answer
from .verb_detector import detect_verb
from .task_classifier import classify_task
from .text_structure_analyzer import analyze_text_structure
from .document_usage_analyzer import analyze_document_usage
from .feedback_engine import generate_feedback

__all__ = [
    "evaluate_answer",
    "detect_verb",
    "classify_task",
    "analyze_text_structure",
    "analyze_document_usage",
    "generate_feedback",
]
