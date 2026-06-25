"""
Mindmaps Méthodologiques — Templates pour la Couche Mindmap
"""
from __future__ import annotations

from typing import Any

METHODOLOGY_MINDMAPS: list[dict[str, Any]] = [
    {
        "id": "mm_01",
        "title": "Comment répondre à une instruction ouverte ?",
        "description": "Processus de résolution pour les tâches complexes",
        "nodes": [
            {"id": 1, "text": "Identifier le verbe d'action", "level": 0},
            {"id": 2, "text": "Déterminer le type de tâche", "level": 0},
            {"id": 3, "text": "Simple → Réponse courte et précise", "level": 1, "parent": 2},
            {"id": 4, "text": "Complexe → Texte structuré 3 parties", "level": 1, "parent": 2},
            {"id": 5, "text": "Introduction : Poser le problème", "level": 1, "parent": 4},
            {"id": 6, "text": "Développement : Arguments et preuves", "level": 1, "parent": 4},
            {"id": 7, "text": "Conclusion : Synthèse et réponse", "level": 1, "parent": 4},
            {"id": 8, "text": "Exploiter les documents", "level": 0},
            {"id": 9, "text": "Utiliser les mots-clés du contexte", "level": 0},
        ],
        "links": [
            {"source": 1, "target": 2, "relation": "dépend de"},
            {"source": 8, "target": 6, "relation": "alimente"},
            {"source": 9, "target": 6, "relation": "enrichit"},
        ],
    },
    {
        "id": "mm_02",
        "title": "Structure d'un texte scientifique",
        "description": "Les 3 parties obligatoires d'une réponse complexe",
        "nodes": [
            {"id": 1, "text": "Introduction", "level": 0},
            {"id": 2, "text": "Formuler la problématique", "level": 1, "parent": 1},
            {"id": 3, "text": "Annoncer le plan", "level": 1, "parent": 1},
            {"id": 4, "text": "Développement", "level": 0},
            {"id": 5, "text": "Arguments scientifiques", "level": 1, "parent": 4},
            {"id": 6, "text": "Exploitation des documents", "level": 1, "parent": 4},
            {"id": 7, "text": "Mots-clés du contexte", "level": 1, "parent": 4},
            {"id": 8, "text": "Conclusion", "level": 0},
            {"id": 9, "text": "Répondre au problème", "level": 1, "parent": 8},
            {"id": 10, "text": "Synthèse des résultats", "level": 1, "parent": 8},
        ],
        "links": [
            {"source": 1, "target": 4, "relation": "suit"},
            {"source": 4, "target": 8, "relation": "suit"},
        ],
    },
    {
        "id": "mm_03",
        "title": "Comment analyser un document ?",
        "description": "Méthode d'exploitation des documents Bac SVT",
        "nodes": [
            {"id": 1, "text": "Lire le document", "level": 0},
            {"id": 2, "text": "Identifier le type de document", "level": 1, "parent": 1},
            {"id": 3, "text": "Repérer les données clés", "level": 1, "parent": 1},
            {"id": 4, "text": "Analyser les données", "level": 0},
            {"id": 5, "text": "Extraire les résultats", "level": 1, "parent": 4},
            {"id": 6, "text": "Relier au contexte", "level": 1, "parent": 4},
            {"id": 7, "text": "Intégrer dans la réponse", "level": 0},
            {"id": 8, "text": "Citer le document", "level": 1, "parent": 7},
            {"id": 9, "text": "Expliquer la donnée", "level": 1, "parent": 7},
        ],
        "links": [
            {"source": 1, "target": 4, "relation": "suit"},
            {"source": 4, "target": 7, "relation": "suit"},
        ],
    },
    {
        "id": "mm_04",
        "title": "Tâche simple vs Tâche complexe",
        "description": "Distinction fondamentale pour le Bac SVT",
        "nodes": [
            {"id": 1, "text": "Identifier le verbe", "level": 0},
            {"id": 2, "text": "Tâche simple", "level": 1, "parent": 1},
            {"id": 3, "text": "صف, عرف, اذكر, عدد, سمّ", "level": 2, "parent": 2},
            {"id": 4, "text": "Réponse courte et précise", "level": 2, "parent": 2},
            {"id": 5, "text": "Tâche complexe", "level": 1, "parent": 1},
            {"id": 6, "text": "وضّح, أثبت, برّر, ناقش", "level": 2, "parent": 5},
            {"id": 7, "text": "Texte structuré 3 parties", "level": 2, "parent": 5},
        ],
        "links": [
            {"source": 2, "target": 5, "relation": "opposition"},
        ],
    },
    {
        "id": "mm_05",
        "title": "Étapes du raisonnement scientifique",
        "description": "Démarche scientifique pour le Bac SVT",
        "nodes": [
            {"id": 1, "text": "Observation", "level": 0},
            {"id": 2, "text": "Relever les faits", "level": 1, "parent": 1},
            {"id": 3, "text": "Problématique", "level": 0},
            {"id": 4, "text": "Formuler la question", "level": 1, "parent": 3},
            {"id": 5, "text": "Hypothèse", "level": 0},
            {"id": 6, "text": "Proposer une explication", "level": 1, "parent": 5},
            {"id": 7, "text": "Vérification", "level": 0},
            {"id": 8, "text": "Exploiter les documents", "level": 1, "parent": 7},
            {"id": 9, "text": "Conclusion", "level": 0},
            {"id": 10, "text": "Valider ou réfuter", "level": 1, "parent": 9},
        ],
        "links": [
            {"source": 1, "target": 3, "relation": "suit"},
            {"source": 3, "target": 5, "relation": "suit"},
            {"source": 5, "target": 7, "relation": "suit"},
            {"source": 7, "target": 9, "relation": "suit"},
        ],
    },
    {
        "id": "mm_06",
        "title": "Erreurs méthodologiques fréquentes au Bac",
        "description": "Pièges à éviter absolument",
        "nodes": [
            {"id": 1, "text": "Erreurs de verbe", "level": 0},
            {"id": 2, "text": "Confondre صف et وضّح", "level": 1, "parent": 1},
            {"id": 3, "text": "Confondre عرف et صف", "level": 1, "parent": 1},
            {"id": 4, "text": "Erreurs de structure", "level": 0},
            {"id": 5, "text": "Absence de conclusion", "level": 1, "parent": 4},
            {"id": 6, "text": "Liste au lieu de texte", "level": 1, "parent": 4},
            {"id": 7, "text": "Erreurs de documents", "level": 0},
            {"id": 8, "text": "Documents non exploités", "level": 1, "parent": 7},
            {"id": 9, "text": "Citation sans analyse", "level": 1, "parent": 7},
        ],
        "links": [
            {"source": 1, "target": 4, "relation": "indépendant"},
            {"source": 4, "target": 7, "relation": "indépendant"},
        ],
    },
]


def generate_methodology_mindmap(verb: str | None = None, map_id: str | None = None) -> dict[str, Any] | None:
    """Génère une mindmap méthodologique selon le verbe ou l'ID."""
    if map_id:
        for mm in METHODOLOGY_MINDMAPS:
            if mm["id"] == map_id:
                return mm
        return None

    if verb:
        verb_map = _get_map_for_verb(verb)
        if verb_map:
            return verb_map

    return METHODOLOGY_MINDMAPS[0]


def _get_map_for_verb(verb: str) -> dict[str, Any] | None:
    """Retourne une mindmap adaptée au verbe."""
    simple_verbs = ["صف", "عرف", " اذكر", "عدد", "سمّ", "حدد"]
    complex_verbs = ["وضّح", "وضّح في نص علمي", "أثبت", "برّر", "فسر", "ناقش", "اقترح فرضية"]

    if verb in complex_verbs:
        return METHODOLOGY_MINDMAPS[1]  # Structure d'un texte scientifique
    if verb in simple_verbs:
        return METHODOLOGY_MINDMAPS[3]  # Simple vs Complexe

    return None


def get_all_mindmaps() -> list[dict[str, Any]]:
    """Retourne toutes les mindmaps méthodologiques."""
    return METHODOLOGY_MINDMAPS
