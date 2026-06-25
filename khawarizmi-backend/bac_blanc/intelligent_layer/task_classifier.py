"""
Classificateur de tâches — Couche 3
Bac Blanc Intelligent V2

Classe les consignes en 'simple' ou 'complex' selon le verbe
et le contexte de l'instruction.
"""
from __future__ import annotations


# Verbes explicitement identifiés comme complexes
COMPLEX_VERBS: list[str] = [
    "وضّح في نص علمي",
    "أثبت",
    "برّر",
    "ناقش",
    "اقترح فرضية",
    "حلّل",
    "قيّم",
    "ادمج",
    "استنتج",
    "اقارن",
]

# Mots-clés indiquant une tâche complexe
COMPLEX_KEYWORDS: list[str] = [
    "نص علمي",
    "فرضية",
    "تحليل",
    "نقد",
    "مقارنة",
    "برهان",
    "استنتاج",
    "منهجية",
]


def classify_task(instruction: str, verb_info: dict | None = None) -> str:
    """
    Classe la tâche en 'simple' ou 'complex'.

    Args:
        instruction: Texte complet de la consigne
        verb_info: Sortie de detect_verb() (optionnel, pour éviter
                   de recalculer)

    Returns:
        "simple" ou "complex"
    """
    # 1. Si verb_info fourni et type déjà connu
    if verb_info and verb_info.get("type") == "complex":
        return "complex"
    if verb_info and verb_info.get("type") == "simple":
        # Vérifier quand même le contexte (un simple peut devenir
        # complexe si "نص علمi" est présent)
        pass

    normalized = instruction.strip()

    # 2. Vérifier les verbes composés complexes
    for verb in COMPLEX_VERBS:
        if verb in normalized:
            return "complex"

    # 3. Vérifier les mots-clés contextuels
    for keyword in COMPLEX_KEYWORDS:
        if keyword in normalized:
            return "complex"

    return "simple"
