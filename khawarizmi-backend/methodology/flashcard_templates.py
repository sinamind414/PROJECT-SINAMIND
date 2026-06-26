"""
Templates de Flashcards Méthodologiques — FSRS
"""
from __future__ import annotations

from typing import Any


# Cartes sur les verbes d'action (30 cartes)
VERB_FLASHCARDS: list[dict[str, Any]] = [
    # --- وضّح في نص علمي (6 cartes) ---
    {
        "card_id": "verb_01",
        "type": "verb_action",
        "front": "ما معنى 'وضّح في نص علمي' ؟",
        "back": "Rédiger un texte structuré (Introduction → Développement → Conclusion) qui explique un phénomène scientifique.",
        "difficulty": "medium",
        "category": "methodology",
        "related_verb": "وضّح في نص علمي",
    },
    {
        "card_id": "verb_02",
        "type": "verb_action",
        "front": "Quelle est la structure attendue pour 'وضّح في نص علمي' ?",
        "back": "3 parties : Introduction (problème), Développement (explication structurée), Conclusion (réponse au problème).",
        "difficulty": "medium",
        "category": "methodology",
        "related_verb": "وضّح في نص علمي",
    },
    {
        "card_id": "verb_03",
        "type": "common_mistake",
        "front": "Quelle erreur fréquente avec 'وضّح في نص علمي' ?",
        "back": "Répondre sous forme de liste ou description simple au lieu d'un texte scientifique structuré.",
        "difficulty": "easy",
        "category": "methodology",
        "related_verb": "وضّح في نص علمي",
    },
    # --- صف (4 cartes) ---
    {
        "card_id": "verb_04",
        "type": "verb_action",
        "front": "ما معنى 'صف' في امتحان العلوم ؟",
        "back": "Décrire avec précision les caractéristiques, la structure ou les propriétés d'un élément.",
        "difficulty": "easy",
        "category": "methodology",
        "related_verb": "صف",
    },
    {
        "card_id": "verb_05",
        "type": "common_mistake",
        "front": "ما الفرق بين 'صف' و 'عرف' ؟",
        "back": "'صف' = décrire les caractéristiques (liste détaillée). 'عرف' = donner une définition concise.",
        "difficulty": "medium",
        "category": "methodology",
        "related_verb": "صف",
    },
    # --- عرف (3 cartes) ---
    {
        "card_id": "verb_06",
        "type": "verb_action",
        "front": "ما معنى 'عرف' في امتحان العلوم ؟",
        "back": "Donner les limites précises d'un concept (caractéristiques essentielles).",
        "difficulty": "easy",
        "category": "methodology",
        "related_verb": "عرف",
    },
    # --- أثبت (4 cartes) ---
    {
        "card_id": "verb_07",
        "type": "verb_action",
        "front": "ما معنى 'أثبت' في امتحان العلوم ؟",
        "back": "Apporter des preuves et des arguments logiques pour valider une affirmation.",
        "difficulty": "medium",
        "category": "methodology",
        "related_verb": "أثبت",
    },
    {
        "card_id": "verb_08",
        "type": "verb_action",
        "front": "Comment structurer une réponse pour 'أثبت' ?",
        "back": "Arguments clairs + Exploitation des documents + Lien explicite preuve → conclusion.",
        "difficulty": "medium",
        "category": "methodology",
        "related_verb": "أثبت",
    },
    # --- برّر (3 cartes) ---
    {
        "card_id": "verb_09",
        "type": "verb_action",
        "front": "ما الفرق بين 'أثبت' و 'برّر' ؟",
        "back": "'أثبت' = prouver avec des preuves. 'برّr' = justifier pourquoi quelque chose se produit.",
        "difficulty": "medium",
        "category": "methodology",
        "related_verb": "برّr",
    },
    # --- اقترح فرضية (3 cartes) ---
    {
        "card_id": "verb_10",
        "type": "verb_action",
        "front": "كيف تقترح فرضيةscientifique ?",
        "back": "Formuler une hypothèse logique et scientifique, cohérente avec le contexte et les données.",
        "difficulty": "medium",
        "category": "methodology",
        "related_verb": "اقترح فرضية",
    },
    # --- ناقش (3 cartes) ---
    {
        "card_id": "verb_11",
        "type": "verb_action",
        "front": "ما معنى 'ناقش' في امتحان العلوم ؟",
        "back": "Analyser différents points de vue ou arguments et prendre position de manière argumentée.",
        "difficulty": "hard",
        "category": "methodology",
        "related_verb": "ناقش",
    },
    # --- Structure (5 cartes) ---
    {
        "card_id": "struct_01",
        "type": "structure",
        "front": "ما هي أجزاء النص العلمي المنظم ؟",
        "back": "3 parties : Introduction (problème), Développement (arguments), Conclusion (réponse).",
        "difficulty": "easy",
        "category": "methodology",
    },
    {
        "card_id": "struct_02",
        "type": "structure",
        "front": "Quand faut-il structurer sa réponse en 3 parties ?",
        "back": "Pour les tâches complexes : وضّح في نص علمي, أثبت, برّر, ناقش, فسر, اقترح فرضية.",
        "difficulty": "medium",
        "category": "methodology",
    },
    # --- Erreurs fréquentes (5 cartes) ---
    {
        "card_id": "error_01",
        "type": "common_mistake",
        "front": "Quelle est l'erreur n°1 au Bac SVT ?",
        "back": "Ne pas structurer sa réponse pour les tâches complexes (liste au lieu de texte scientifique).",
        "difficulty": "easy",
        "category": "methodology",
    },
    {
        "card_id": "error_02",
        "type": "common_mistake",
        "front": "Pourquoi perd-on des points sur l'exploitation des documents ?",
        "back": "Quand on cite le document sans en tirer de donnée ou sans lier à la réponse.",
        "difficulty": "medium",
        "category": "methodology",
    },
]


def get_flashcards_by_category(category: str) -> list[dict[str, Any]]:
    """Retourne les cartes d'une catégorie donnée."""
    return [c for c in VERB_FLASHCARDS if c.get("category") == category]


def get_flashcards_by_type(card_type: str) -> list[dict[str, Any]]:
    """Retourne les cartes d'un type donné."""
    return [c for c in VERB_FLASHCARDS if c.get("type") == card_type]


def get_all_flashcards() -> list[dict[str, Any]]:
    """Retourne toutes les cartes méthodologiques."""
    return VERB_FLASHCARDS
