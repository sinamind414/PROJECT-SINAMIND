"""
Diagnostic méthodologique — Methodology Evaluator V2

Détection des erreurs types, score de maturité, profils d'erreurs.
"""
from __future__ import annotations

from typing import Any

# ===== PROFILS D'ERREURS (10 types) =====
ERROR_PROFILES: list[dict[str, Any]] = [
    {
        "id": "verb_confusion",
        "name": "Confusion entre verbes d'action",
        "description": "L'élève ne distingue pas les verbes simples des verbes complexes",
        "examples": [
            "Utilise 'صف' alors que l'instruction demande 'وضّح في نص علمي'",
            "Donne une définition ('عرف') au lieu de justifier ('برّr')",
        ],
        "recommendation": "Entraîne-toi à identifier le verbe principal avant de répondre",
        "severity": "high",
    },
    {
        "id": "missing_structure",
        "name": "Absence de structure dans les tâches complexes",
        "description": "L'élève ne structure pas sa réponse en Introduction/Développement/Conclusion",
        "examples": [
            "Réponse sous forme de liste pour 'وضّح في نص علمي'",
            "Absence de conclusion pour 'أثبت'",
        ],
        "recommendation": "Pour les tâches complexes, structure toujours en 3 parties",
        "severity": "high",
    },
    {
        "id": "weak_context_reading",
        "name": "Lecture insuffisante du contexte",
        "description": "L'élève ne prend pas en compte le contexte et les documents fournis",
        "examples": [
            "Réponse générique sans référence au document",
            "Ignorer les données du contexte",
        ],
        "recommendation": "Relis le contexte et repère les mots-clés avant de répondre",
        "severity": "high",
    },
    {
        "id": "superficial_analysis",
        "name": "Analyse trop superficielle des documents",
        "description": "L'élève mentionne les documents sans les exploiter réellement",
        "examples": [
            "Cite le document sans en tirer de conclusion",
            "Pas de lien entre les données et la réponse",
        ],
        "recommendation": "Pour chaque document, identifie la donnée clé et relie-la à ta réponse",
        "severity": "medium",
    },
    {
        "id": "no_argumentation",
        "name": "Absence d'argumentation",
        "description": "L'élève donne des réponses sans les justifier",
        "examples": [
            "Affirmation sans preuve pour 'أثبت'",
            "Justification vide pour 'برّr'",
        ],
        "recommendation": "Chaque affirmation doit être suivie d'une preuve ou d'un argument",
        "severity": "high",
    },
    {
        "id": "keyword_absence",
        "name": "Absence de mots-clés scientifiques",
        "description": "L'élève n'utilise pas les termes exacts du programme",
        "examples": [
            "Utilise 'le truc qui fait' au lieu du terme scientifique",
            "Vocabulaire approximatif",
        ],
        "recommendation": "Repère les termes scientifiques dans le contexte et utilisle-les",
        "severity": "medium",
    },
    {
        "id": "confusion_description_explanation",
        "name": "Confusion entre description et explication",
        "description": "L'élève décrit au lieu d'expliquer (ou inversement)",
        "examples": [
            "Décrit les étapes sans expliquer pourquoi ('وضّح')",
            "Explique quand l'instruction demande de décrire ('صف')",
        ],
        "recommendation": "Vérifie le verbe : 'صف' = décrire, 'وضّح' = expliquer",
        "severity": "medium",
    },
    {
        "id": "incomplete_response",
        "name": "Réponse incomplète",
        "description": "L'élève ne traite qu'une partie de la question",
        "examples": [
            "Oublie un sous-question",
            "Ne répond qu'à la première partie",
        ],
        "recommendation": "Relis l'instruction et vérifie que tu as traité chaque partie",
        "severity": "medium",
    },
    {
        "id": "hors_sujet",
        "name": "Réponse hors sujet",
        "description": "L'élève répond à une question différente de celle posée",
        "examples": [
            "Répond à 'Qu'est-ce que ?' alors que l'instruction est 'Pourquoi ?'",
            "Sujet connexe mais non demandé",
        ],
        "recommendation": "Relis l'instruction et assure-toi que ta réponse correspond exactement",
        "severity": "high",
    },
    {
        "id": "no_conclusion",
        "name": "Absence de conclusion",
        "description": "L'élève termine sans synthèse pour les tâches complexes",
        "examples": [
            "Réponse qui s'arrête après le développement",
            "Pas de réponse finale à la problématique",
        ],
        "recommendation": "Termine toujours par une conclusion qui répond à la question",
        "severity": "medium",
    },
]


def diagnose_methodology_level(
    scores: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Calcule le niveau de maturité méthodologique d'un élève
    à partir de son historique de réponses.

    Args:
        scores: Liste de résultats d'évaluation, chacun avec
                'verb', 'task_type', 'score', 'max_score',
                'structure_score', 'feedback'

    Returns:
        dict avec keys :
            level, level_label, score_moyen, error_profiles,
            strengths, recommendations
    """
    if not scores:
        return {
            "level": "beginner",
            "level_label": "Débutant",
            "score_moyen": 0,
            "error_profiles": [],
            "strengths": [],
            "recommendations": ["Commence par les exercices fondamentaux"],
        }

    # Score moyen pondéré
    total_score = 0
    total_max = 0
    for s in scores:
        total_score += s.get("score", 0)
        total_max += s.get("max_score", 10)
    score_moyen = (total_score / total_max * 100) if total_max > 0 else 0

    # Détection des erreurs dominantes
    detected_errors: list[str] = []
    for s in scores:
        feedback = s.get("feedback", {})
        if isinstance(feedback, dict):
            for w in feedback.get("weaknesses", []):
                error_id = _match_error(w)
                if error_id and error_id not in detected_errors:
                    detected_errors.append(error_id)

    # Niveau
    level, level_label = _compute_level(score_moyen, detected_errors)

    # Recommandations
    recommendations = _generate_recommendations(level, detected_errors)

    return {
        "level": level,
        "level_label": level_label,
        "score_moyen": round(score_moyen, 1),
        "error_profiles": [
            _get_error_profile(eid) for eid in detected_errors
        ],
        "recommendations": recommendations,
    }


def _compute_level(score: float, errors: list[str]) -> tuple[str, str]:
    """Détermine le niveau basé sur le score et les erreurs."""
    high_severity = [
        e for e in errors
        if _get_error_profile(e).get("severity") == "high"
    ]
    if score >= 80 and len(high_severity) == 0:
        return "expert", "Expert"
    if score >= 60:
        return "advanced", "Avancé"
    if score >= 40:
        return "intermediate", "Intermédiaire"
    return "beginner", "Débutant"


def _match_error(faiblesse_text: str) -> str | None:
    """Matche un texte de faiblesse avec un profil d'erreur."""
    mapping = {
        "verb_confusion": ["verbe", "confusion"],
        "missing_structure": ["structure", "structurer", "Introduction"],
        "weak_context_reading": ["contexte", "document"],
        "superficial_analysis": ["exploitation", "document"],
        "no_argumentation": ["argument", "preuve"],
        "keyword_absence": ["mot-clé", "terme"],
        "incomplete_response": ["incomplet", "partie"],
        "no_conclusion": ["conclusion"],
    }
    for error_id, keywords in mapping.items():
        for kw in keywords:
            if kw.lower() in faiblesse_text.lower():
                return error_id
    return None


def _get_error_profile(error_id: str) -> dict[str, Any]:
    """Retourne le profil d'erreur par son ID."""
    for profile in ERROR_PROFILES:
        if profile["id"] == error_id:
            return profile
    return {"id": error_id, "name": error_id, "severity": "unknown"}


def _generate_recommendations(level: str, errors: list[str]) -> list[str]:
    """Génère des recommandations selon le niveau et les erreurs."""
    recs: list[str] = []

    if level == "beginner":
        recs.append("Commence par les exercices simples ( vocab, definition )")
        recs.append("Apprends à identifier le verbe d'action avant de répondre")

    if "missing_structure" in errors:
        recs.append("Entraîne-toi à structurer en Introduction → Développement → Conclusion")
    if "verb_confusion" in errors:
        recs.append("Révise la différence entre les verbes simples et complexes")
    if "weak_context_reading" in errors:
        recs.append("Relis le contexte 2 fois avant de répondre et souligne les mots-clés")
    if "no_argumentation" in errors:
        recs.append("Chaque affirmation doit être suivie d'une preuve")

    if not recs:
        recs.append("Continue comme ça !")

    return recs


# ═════════════════════════════════════════════
# Semaine 3 — Nouvelles fonctions Couche 3
# ═════════════════════════════════════════════

import json
from pathlib import Path

_PROFILES_PATH = Path(__file__).parent / "error_profiles.json"

with open(_PROFILES_PATH, "r", encoding="utf-8") as _f:
    _ERROR_PROFILES_JSON = json.load(_f)["profiles"]


def _find_profile(profile_id: str) -> dict[str, Any]:
    for p in _ERROR_PROFILES_JSON:
        if p["id"] == profile_id:
            return p
    # fallback vers ERROR_PROFILES hardcodé
    for p in ERROR_PROFILES:
        if p["id"] == profile_id:
            return p
    return {"id": profile_id, "name": profile_id, "recommendation": ""}


def detect_verb_confusion(instruction: str, verb_detected: str) -> bool:
    complex_verbs = ["وضّح في نص علمي", "أثبت", "برّر", "فسر", "ناقش"]
    simple_verbs = ["صف", "عرف", "استنتج"]
    if any(v in instruction for v in complex_verbs) and verb_detected in simple_verbs:
        return True
    return False


def detect_error_profiles(
    verb: str,
    task_type: str,
    structure: dict,
    doc_usage: dict,
    student_answer: str,
) -> list[dict[str, Any]]:
    detected = []
    if detect_verb_confusion(verb, verb):
        detected.append(_find_profile("verb_confusion"))
    if task_type == "complex" and structure.get("structure_score", 0) < 8:
        detected.append(_find_profile("weak_structure"))
    if doc_usage.get("usage_quality") in ("weak", "very_weak", "none"):
        detected.append(_find_profile("poor_document_usage"))
    if task_type == "complex" and not structure.get("has_conclusion"):
        detected.append(_find_profile("no_conclusion"))
    return detected


def calculate_methodology_maturity(answers: list[dict]) -> dict[str, Any]:
    if not answers:
        return {"level": "Débutant", "score": 0, "total_answers": 0}
    total_score = sum(a.get("structure_score", 0) for a in answers)
    avg_score = total_score / len(answers)
    if avg_score >= 14:
        level = "Expert"
    elif avg_score >= 11:
        level = "Avancé"
    elif avg_score >= 7:
        level = "Intermédiaire"
    else:
        level = "Débutant"
    return {"level": level, "score": round(avg_score, 1), "total_answers": len(answers), "max_possible": 16}


def generate_diagnostic_report(
    verb: str,
    task_type: str,
    structure: dict,
    doc_usage: dict,
    student_answer: str,
    previous_answers: list[dict] | None = None,
) -> dict[str, Any]:
    if previous_answers is None:
        previous_answers = []
    error_profiles = detect_error_profiles(verb, task_type, structure, doc_usage, student_answer)
    maturity = calculate_methodology_maturity(previous_answers + [{"structure_score": structure.get("structure_score", 0)}])
    return {
        "verb": verb,
        "task_type": task_type,
        "error_profiles": error_profiles,
        "maturity_level": maturity["level"],
        "maturity_score": maturity["score"],
        "recommendations": [p["recommendation"] for p in error_profiles],
        "structure_analysis": structure,
        "document_usage": doc_usage,
    }
