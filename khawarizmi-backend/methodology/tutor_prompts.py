"""
Prompts du Tuteur Méthodologique — Semaine 4
Explications des 10 verbes prioritaires + réponses types
"""

VERB_EXPLANATIONS = {
    "وضّح في نص علمي": {
        "definition": "Rédiger un texte structuré (Introduction → Développement → Conclusion) qui explique un phénomène scientifique.",
        "structure": "Introduction (poser le problème) → Développement (explication détaillée) → Conclusion (réponse au problème)",
        "example": "Exemple : Expliquer la photosynthèse en 3 parties claires.",
        "common_mistake": "Faire une simple liste ou description au lieu d'un texte structuré.",
    },
    "صف": {
        "definition": "Décrire avec précision les caractéristiques d'un élément.",
        "structure": "Description détaillée et précise des caractéristiques.",
        "example": "Décrire la structure d'une cellule végétale.",
        "common_mistake": "Donner une réponse trop générale ou trop courte.",
    },
    "عرف": {
        "definition": "Donner les limites précises d'un concept.",
        "structure": "Définition concise avec les caractéristiques essentielles.",
        "example": "Définir la photosynthèse.",
        "common_mistake": "Faire une définition trop longue ou vague.",
    },
    "أثبت": {
        "definition": "Apporter des preuves et arguments logiques pour valider une affirmation.",
        "structure": "Arguments clairs + exploitation des documents + lien preuve → conclusion.",
        "example": "Prouver que la photosynthèse nécessite de la lumière.",
        "common_mistake": "Arguments sans lien avec les documents.",
    },
    "برّر": {
        "definition": "Expliquer pourquoi un phénomène se produit.",
        "structure": "Justification appuyée par des preuves scientifiques.",
        "example": "Justifier pourquoi les plantes ont besoin de lumière.",
        "common_mistake": "Justification sans preuve.",
    },
    "استنتج": {
        "definition": "Tirer une conclusion logique à partir des données.",
        "structure": "Conclusion claire et cohérente.",
        "example": "Conclure à partir d'un graphique.",
        "common_mistake": "Conclusion non justifiée.",
    },
    "فسر": {
        "definition": "Donner une explication scientifique d'un résultat.",
        "structure": "Explication scientifique claire avec lien aux données.",
        "example": "Expliquer pourquoi la courbe augmente.",
        "common_mistake": "Explication trop descriptive.",
    },
    "اقترح فرضية": {
        "definition": "Formuler des hypothèses logiques et scientifiques.",
        "structure": "Hypothèse claire et testable.",
        "example": "Proposer une hypothèse sur l'effet de la température.",
        "common_mistake": "Hypothèse non scientifique.",
    },
    "ناقش": {
        "definition": "Analyser différents points de vue et prendre position.",
        "structure": "Analyse équilibrée + prise de position argumentée.",
        "example": "Discuter des avantages et inconvénients d'une technique.",
        "common_mistake": "Position sans argumentation.",
    },
    "أنجز رسما تخطيطيا": {
        "definition": "Réaliser un schéma clair et légendé.",
        "structure": "Schéma lisible + légendes correctes.",
        "example": "Dessiner le schéma d'une cellule.",
        "common_mistake": "Schéma illisible ou sans légende.",
    },
}


def get_verb_explanation(verb_arabic: str) -> dict:
    return VERB_EXPLANATIONS.get(verb_arabic, {
        "definition": "Verbe non reconnu dans la base.",
        "structure": "Consulte le manuel méthodologique.",
        "example": "",
        "common_mistake": "",
    })
