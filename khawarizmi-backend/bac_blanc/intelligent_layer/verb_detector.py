"""
Détecteur de verbes d'action — Couche 3
Bac Blanc Intelligent V2
"""
from __future__ import annotations

from typing import Any

# Base de données des verbes Bac SVT Algérie
# type: "simple" | "complex"
# max_score: score maximal attribué à ce verbe dans l'exercice
VERB_DATABASE: list[dict[str, Any]] = [
    # === TÂCHES SIMPLES ===
    {"arabic": "عدّل", "french": "décrire", "type": "simple", "max_score": 4},
    {"arabic": "أكمل", "french": "compléter", "type": "simple", "max_score": 4},
    {"arabic": " سمّ", "french": "nommer", "type": "simple", "max_score": 2},
    {"arabic": " حدد", "french": "délimiter", "type": "simple", "max_score": 4},
    {"arabic": "استخرج", "french": "extraire", "type": "simple", "max_score": 4},
    {"arabic": "اعتبر", "french": "considérer", "type": "simple", "max_score": 2},
    {"arabic": "استعمل", "french": "utiliser", "type": "simple", "max_score": 4},
    {"arabic": "ذكّر", "french": "rappeler", "type": "simple", "max_score": 2},
    {"arabic": "ree", "french": "classer", "type": "simple", "max_score": 4},
    {"arabic": "ree", "french": "ordonner", "type": "simple", "max_score": 4},
    # === TÂCHES COMPLEXES ===
    {"arabic": "وضّح", "french": "expliquer", "type": "complex", "max_score": 8},
    {"arabic": "وضّح في نص علمي", "french": "expliquer dans un texte scientifique", "type": "complex", "max_score": 10},
    {"arabic": "أثبت", "french": "démontrer", "type": "complex", "max_score": 8},
    {"arabic": "برّر", "french": "justifier", "type": "complex", "max_score": 8},
    {"arabic": "ناقش", "french": "discuter", "type": "complex", "max_score": 10},
    {"arabic": "اقترح", "french": "proposer", "type": "complex", "max_score": 8},
    {"arabic": "اقترح فرضية", "french": "proposer une hypothèse", "type": "complex", "max_score": 10},
    {"arabic": "حلّل", "french": "analyser", "type": "complex", "max_score": 10},
    {"arabic": "قيّم", "french": "évaluer", "type": "complex", "max_score": 10},
    {"arabic": "استنتج", "french": "conclure", "type": "complex", "max_score": 8},
    {"arabic": "اقارن", "french": "comparer", "type": "complex", "max_score": 8},
    {"arabic": "ادمج", "french": "intégrer", "type": "complex", "max_score": 10},
]


def detect_verb(instruction: str) -> dict[str, Any]:
    """
    Détecte le verbe d'action principal dans l'instruction.

    Args:
        instruction: Texte de la consigne de l'exercice

    Returns:
        dict avec keys: verb, type, max_score
    """
    normalized = instruction.strip()

    # Priorité aux verbes composés (plus longs d'abord)
    sorted_verbs = sorted(VERB_DATABASE, key=lambda v: len(v["arabic"]), reverse=True)

    for verb in sorted_verbs:
        if verb["arabic"] in normalized:
            return {
                "verb": verb["arabic"],
                "type": verb["type"],
                "max_score": verb["max_score"],
            }

    return {"verb": "unknown", "type": "unknown", "max_score": 0}
