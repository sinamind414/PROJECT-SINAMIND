"""Methodology Local Responses — 0 Token API"""

from typing import Dict, Any

METHODOLOGY_RESPONSES: Dict[str, Dict[str, str]] = {
    "وضّح في نص علمي": {
        "structure": "Ta reponse doit contenir 3 parties : Introduction (poser le probleme scientifique), Developpement (explication structuree + arguments), Conclusion (reponse au probleme).",
        "common_mistake": "Tu as fait une simple description ou une liste au lieu d'un texte structure.",
        "question": "Quelle est la problematique scientifique que tu dois poser dans l'introduction ?",
        "example": "Exemple : Expliquer la photosynthese en suivant les 3 parties."
    },
    "أثبت": {
        "structure": "Tu dois apporter : Arguments clairs + Preuves issues des documents + Lien entre preuves et conclusion.",
        "common_mistake": "Arguments sans lien avec les documents ou conclusion sans preuves.",
        "question": "Quelles preuves du document utilises-tu pour appuyer ton argument ?",
        "example": "Exemple : Prouver que la mitose permet le maintien du caryotype."
    },
    "برّر": {
        "structure": "Tu dois expliquer le 'pourquoi' avec des justifications scientifiques appuyees par des donnees.",
        "common_mistake": "Justification generale sans preuve ou sans lien avec le document.",
        "question": "Quelle donnee du document justifie ton explication ?",
        "example": "Exemple : Justifier pourquoi la temperature influence l'activite enzymatique."
    },
    "ناقش": {
        "structure": "Tu dois presenter : Les arguments POUR + Les arguments CONTRE + Ta position argumentee finale.",
        "common_mistake": "Position sans argumentation ou analyse uniquement d'un seul point de vue.",
        "question": "Veux-tu que je t aide sur les arguments POUR ou CONTRE en premier ?",
        "example": "Exemple : Discuter des avantages et inconvenients des OGM."
    },
    "فسر": {
        "structure": "Tu dois donner une explication scientifique claire en reliant les donnees du document au phenomene observe.",
        "common_mistake": "Explication trop descriptive sans lien avec les donnees.",
        "question": "Quelle observation du document expliques-tu ?",
        "example": "Exemple : Expliquer l'augmentation de la courbe sur le graphique."
    },
    "اقترح فرضية": {
        "structure": "Ta hypothese doit etre logique, scientifique et en lien avec les donnees du document.",
        "common_mistake": "Hypothese non scientifique ou hors contexte.",
        "question": "Sur quelle observation du document bases-tu ton hypothese ?",
        "example": "Exemple : Proposer une hypothese sur l'effet d'un facteur sur la photosynthese."
    },
    "صف": {
        "structure": "Decris avec precision les caracteristiques, la structure ou les proprietes de l'element demande.",
        "common_mistake": "Reponse trop generale ou incomplete.",
        "question": "Quelles caracteristiques de l'element veux-tu decrire en priorite ?",
        "example": "Exemple : Decrire la structure d'une cellule eucaryote."
    },
    "عرف": {
        "structure": "Donne une definition precise et concise en citant les caracteristiques essentielles du concept.",
        "common_mistake": "Definition trop longue, vague ou contenant des informations inutiles.",
        "question": "Quelles sont les caracteristiques essentielles de ce concept ?",
        "example": "Exemple : Definir la photosynthese."
    },
    "استنتج": {
        "structure": "Tire une conclusion logique a partir des donnees et des documents fournis.",
        "common_mistake": "Conclusion non justifiee ou hors sujet.",
        "question": "Quelle donnee du document te permet d aboutir a cette conclusion ?",
        "example": "Exemple : Conclure a partir d'un graphique sur l'evolution d'une population."
    },
}


def get_local_methodology_response(verb: str) -> Dict[str, Any]:
    verb_data = METHODOLOGY_RESPONSES.get(verb)

    if not verb_data:
        return {
            "reponse": "Peux-tu reformuler ta question en utilisant un verbe d'action clair (وضّح، أثبت، برّر، ناقش...) ?",
            "type": "methodology_local",
            "verb": "unknown",
            "fallback_active": False,
        }

    response_text = (
        f"{verb_data['structure']}\n\n"
        f"Erreur frequente : {verb_data['common_mistake']}\n\n"
        f" -> {verb_data['question']}"
    )

    return {
        "reponse": response_text,
        "type": "methodology_local",
        "verb": verb,
        "question_suivante": verb_data["question"],
        "fallback_active": False,
    }


def detect_verb_from_message(message: str) -> str | None:
    verb_mapping = {
        "وضّح": "وضّح في نص علمي",
        "وضح": "وضّح في نص علمي",
        "أثبت": "أثبت",
        "اثبت": "أثبت",
        "برّر": "برّر",
        "برر": "برّر",
        "ناقش": "ناقش",
        "فسر": "فسر",
        "اقترح": "اقترح فرضية",
        "صف": "صف",
        "عرف": "عرف",
        "استنتج": "استنتج",
    }

    for key, verb in verb_mapping.items():
        if key in message:
            return verb

    return None
