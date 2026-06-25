"""
Base de données des verbes d'action Bac SVT Algérie
Source : Livre Manhajiya Bac SVT + METHODOLOGY-EVALUATOR-V2

25+ verbes avec définitions, critères, erreurs fréquentes.
"""
from __future__ import annotations

from typing import Any

VERB_DATABASE: list[dict[str, Any]] = [
    # ===== TÂCHES SIMPLEX =====
    {
        "id": 1,
        "arabic": "صف",
        "french": "Décrire / Caractériser",
        "type": "simple",
        "max_score": 10,
        "definition": "Décrire avec précision les caractéristiques, la structure ou les propriétés d'un élément.",
        "criteria": [
            "Description détaillée et précise",
            "Utilisation des termes scientifiques corrects",
            "Exhaustivité des éléments demandés",
        ],
        "common_mistakes": [
            "Réponse trop générale ou trop courte",
            "Confusion avec le verbe 'عرف'",
        ],
    },
    {
        "id": 2,
        "arabic": "عرف",
        "french": "Définir",
        "type": "simple",
        "max_score": 10,
        "definition": "Donner les limites précises d'un concept (caractéristiques essentielles).",
        "criteria": [
            "Définition concise et précise",
            "Mention des caractéristiques essentielles",
            "Absence d'informations inutiles",
        ],
        "common_mistakes": [
            "Définition trop longue ou trop vague",
            "Confusion avec le verbe 'صف'",
        ],
    },
    {
        "id": 3,
        "arabic": "اذكر",
        "french": "Citer / Énumérer",
        "type": "simple",
        "max_score": 4,
        "definition": "Lister des éléments de manière exhaustive et organisée.",
        "criteria": [
            "Liste complète",
            "Ordre logique",
            "Termes exacts",
        ],
        "common_mistakes": [
            "Éléments manquants",
            "Ordre désordonné",
        ],
    },
    {
        "id": 4,
        "arabic": "عدد",
        "french": "Dénombrer",
        "type": "simple",
        "max_score": 4,
        "definition": "Indiquer le nombre exact d'éléments.",
        "criteria": [
            "Nombre correct",
            "Énumération complète",
        ],
        "common_mistakes": [
            "Compte incorrect",
            "Oubli d'éléments",
        ],
    },
    {
        "id": 5,
        "arabic": "سمّ",
        "french": "Nommer",
        "type": "simple",
        "max_score": 2,
        "definition": "Donner le nom exact d'un élément.",
        "criteria": [
            "Nom correct et exact",
        ],
        "common_mistakes": [
            "Nom approximatif",
        ],
    },
    {
        "id": 6,
        "arabic": "حدد",
        "french": "Délimiter / Identifier",
        "type": "simple",
        "max_score": 4,
        "definition": "Repérer et délimiter précisément un élément dans un ensemble.",
        "criteria": [
            "Identification précise",
            "Localisation exacte",
        ],
        "common_mistakes": [
            "Identification vague",
        ],
    },
    {
        "id": 7,
        "arabic": "استخرج",
        "french": "Extraire",
        "type": "simple",
        "max_score": 4,
        "definition": "Tirer une information d'un document ou d'un ensemble de données.",
        "criteria": [
            "Information exacte",
            "Source identifiée",
        ],
        "common_mistakes": [
            "Information inexacte",
            "Source non citée",
        ],
    },
    {
        "id": 8,
        "arabic": "استعمل",
        "french": "Utiliser / Appliquer",
        "type": "simple",
        "max_score": 4,
        "definition": "Employer un outil, une méthode ou un concept pour résoudre un problème.",
        "criteria": [
            "Choix approprié de l'outil",
            "Application correcte",
        ],
        "common_mistakes": [
            "Outil inadapté",
            "Mauvaise application",
        ],
    },
    {
        "id": 9,
        "arabic": "رتب",
        "french": "Classer / Ordonner",
        "type": "simple",
        "max_score": 4,
        "definition": "Organiser des éléments selon un critère donné.",
        "criteria": [
            "Critère de classement identifié",
            "Ordre correct",
        ],
        "common_mistakes": [
            "Critère absent",
            "Ordre incorrect",
        ],
    },
    {
        "id": 10,
        "arabic": "استنتج",
        "french": "Conclure / Déduire",
        "type": "simple",
        "max_score": 10,
        "definition": "Tirer une conclusion logique à partir des données et des documents fournis.",
        "criteria": [
            "Conclusion logique et cohérente",
            "Appui sur les documents fournis",
        ],
        "common_mistakes": [
            "Conclusion non justifiée",
            "Conclusion hors sujet",
        ],
    },

    # ===== TÂCHES COMPLEXES =====
    {
        "id": 11,
        "arabic": "وضّح في نص علمي",
        "french": "Expliquer dans un texte scientifique",
        "type": "complex",
        "max_score": 20,
        "definition": "Rédiger un texte structuré (Introduction → Développement → Conclusion) qui explique un phénomène.",
        "criteria": [
            "Introduction qui pose le problème scientifique",
            "Développement structuré et argumenté",
            "Conclusion qui répond au problème",
            "Utilisation des mots-clés du contexte",
        ],
        "common_mistakes": [
            "Réponse sous forme de liste ou description simple",
            "Absence de conclusion",
            "Mélange des idées sans structure",
        ],
    },
    {
        "id": 12,
        "arabic": "أثبت",
        "french": "Prouver / Démontrer",
        "type": "complex",
        "max_score": 15,
        "definition": "Apporter des preuves et des arguments logiques pour valider une affirmation.",
        "criteria": [
            "Arguments clairs et logiques",
            "Exploitation pertinente des documents",
            "Lien explicite entre preuves et conclusion",
        ],
        "common_mistakes": [
            "Arguments sans lien avec les documents",
            "Conclusion sans preuves",
        ],
    },
    {
        "id": 13,
        "arabic": "برّر",
        "french": "Justifier",
        "type": "complex",
        "max_score": 15,
        "definition": "Expliquer pourquoi un phénomène se produit en apportant des justifications.",
        "criteria": [
            "Justification appuyée par des preuves",
            "Lien avec le contexte de l'exercice",
        ],
        "common_mistakes": [
            "Justification sans preuve",
            "Réponse trop générale",
        ],
    },
    {
        "id": 14,
        "arabic": "فسر",
        "french": "Expliquer / Interpréter",
        "type": "complex",
        "max_score": 15,
        "definition": "Donner une explication scientifique d'un résultat ou d'un phénomène observé.",
        "criteria": [
            "Explication scientifique claire",
            "Lien avec les données du document",
        ],
        "common_mistakes": [
            "Explication trop descriptive",
            "Absence de lien avec les données",
        ],
    },
    {
        "id": 15,
        "arabic": "اقترح فرضية",
        "french": "Proposer une hypothèse",
        "type": "complex",
        "max_score": 10,
        "definition": "Formuler une ou plusieurs hypothèses logiques et scientifiques pour expliquer un phénomène.",
        "criteria": [
            "Hypothèse logique et scientifique",
            "Cohérente avec le contexte",
        ],
        "common_mistakes": [
            "Hypothèse non scientifique",
            "Hypothèse hors contexte",
        ],
    },
    {
        "id": 16,
        "arabic": "ناقش",
        "french": "Discuter",
        "type": "complex",
        "max_score": 15,
        "definition": "Analyser différents points de vue ou arguments et prendre position de manière argumentée.",
        "criteria": [
            "Analyse équilibrée des arguments",
            "Prise de position argumentée",
        ],
        "common_mistakes": [
            "Position sans argumentation",
            "Analyse trop superficielle",
        ],
    },
    {
        "id": 17,
        "arabic": "حلّل",
        "french": "Analyser",
        "type": "complex",
        "max_score": 10,
        "definition": "Décomposer un sujet en ses éléments constitutifs pour les étudier séparément.",
        "criteria": [
            "Décomposition méthodique",
            "Étude de chaque composante",
            "Synthèse des résultats",
        ],
        "common_mistakes": [
            "Description au lieu d'analyse",
            "Pas de synthèse",
        ],
    },
    {
        "id": 18,
        "arabic": "قيّم",
        "french": "Évaluer / Apprécier",
        "type": "complex",
        "max_score": 10,
        "definition": "Porter un jugement argumenté sur la validité, la pertinence ou la qualité de quelque chose.",
        "criteria": [
            "Jugement fondé sur des critères",
            "Arguments pour et contre",
        ],
        "common_mistakes": [
            "Jugement sans argument",
            "Absence de critères",
        ],
    },
    {
        "id": 19,
        "arabic": "اقارن",
        "french": "Comparer",
        "type": "complex",
        "max_score": 10,
        "definition": "Mettre en parallel deux ou plusieurs éléments pour identifier ressemblances et différences.",
        "criteria": [
            "Critères de comparaison clairs",
            "Éléments comparés identifiés",
            "Ressemblances et différences",
        ],
        "common_mistakes": [
            "Un seul élément décrit",
            "Pas de critères de comparaison",
        ],
    },
    {
        "id": 20,
        "arabic": "أنجز رسما تخطيطيا",
        "french": "Réaliser un schéma",
        "type": "complex",
        "max_score": 10,
        "definition": "Réaliser un schéma clair, légendé et fonctionnel.",
        "criteria": [
            "Schéma clair et lisible",
            "Légendes correctes et complètes",
            "Respect des conventions",
        ],
        "common_mistakes": [
            "Schéma illisible",
            "Légendes manquantes ou incorrectes",
        ],
    },
]


def get_verb(arabic_text: str) -> dict[str, Any] | None:
    """Cherche un verbe par son texte arabe (correspondance partielle)."""
    sorted_verbs = sorted(VERB_DATABASE, key=lambda v: len(v["arabic"]), reverse=True)
    for verb in sorted_verbs:
        if verb["arabic"] in arabic_text:
            return verb
    return None


def get_verb_by_id(verb_id: int) -> dict[str, Any] | None:
    """Cherche un verbe par son ID."""
    for verb in VERB_DATABASE:
        if verb["id"] == verb_id:
            return verb
    return None


def get_all_verbs() -> list[dict[str, Any]]:
    """Retourne tous les verbes de la base."""
    return VERB_DATABASE


def get_complex_verbs() -> list[dict[str, Any]]:
    """Retourne uniquement les verbes complexes."""
    return [v for v in VERB_DATABASE if v["type"] == "complex"]


def get_simple_verbs() -> list[dict[str, Any]]:
    """Retourne uniquement les verbes simples."""
    return [v for v in VERB_DATABASE if v["type"] == "simple"]
