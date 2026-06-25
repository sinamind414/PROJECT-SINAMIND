"""
Classificateur de tâches — Methodology Evaluator V2

Classe les consignes en 'simple' ou 'complex' selon le verbe
et le contexte de l'instruction.
"""
from __future__ import annotations

from .verb_database import get_verb, get_complex_verbs

# Mots-clés indiquant une tâche complexe (hors verbes)
COMPLEX_KEYWORDS: list[str] = [
    "نص علمي",
    "فرضية",
    "تحليل",
    "نقد",
    "مقارنة",
    "برهان",
    "استنتاج",
    "منهجية",
    " TEXT",
    "schema",
]


def classify_task(instruction: str, verb_info: dict | None = None) -> str:
    """
    Classe la tâche en 'simple' ou 'complex'.

    Args:
        instruction: Texte complet de la consigne
        verb_info: Sortie de get_verb() (optionnel)

    Returns:
        "simple" ou "complex"
    """
    # 1. Si verb_info fourni et type déjà connu
    if verb_info and verb_info.get("type") == "complex":
        return "complex"

    # 2. Chercher le verbe dans l'instruction
    found_verb = get_verb(instruction)
    if found_verb and found_verb["type"] == "complex":
        return "complex"

    # 3. Vérifier les mots-clés contextuels
    for keyword in COMPLEX_KEYWORDS:
        if keyword in instruction:
            return "complex"

    return "simple"
