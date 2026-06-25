"""Methodology Local Responses — Version Enrichie (Manhajiya Bac SVT)
0 Token API - Reponses locales structurees et methodologiques
"""

from typing import Dict, Any

METHODOLOGY_RESPONSES: Dict[str, Dict[str, str]] = {

    # ============================================
    # VERBES SIMPLES (Note <= 10)
    # ============================================

    "سمّ": {
        "structure": "Donne le nom exact de l element demande.",
        "common_mistake": "Donner un nom approximatif ou incorrect.",
        "question": "Quel est le nom precis de cet element ?",
        "example": "Exemple : Nomme l enzyme qui catalyse la reaction."
    },
    "عرّف": {
        "structure": "Donne une definition precise et concise en citant les caracteristiques essentielles du concept.",
        "common_mistake": "Definition trop longue, vague ou contenant des informations inutiles.",
        "question": "Quelles sont les caracteristiques essentielles de ce concept ?",
        "example": "Exemple : Definir la photosynthese."
    },
    "صف": {
        "structure": "Decris avec precision les caracteristiques, la structure ou les proprietes de l element.",
        "common_mistake": "Reponse trop generale ou incomplete.",
        "question": "Quelles caracteristiques de l element veux-tu decrire en priorite ?",
        "example": "Exemple : Decrire la structure d une cellule eucaryote."
    },
    "ذكر": {
        "structure": "Cite les elements demandes de maniere exhaustive et organisee.",
        "common_mistake": "Oubli d elements ou ordre desordonne.",
        "question": "Quels sont les elements que tu dois citer ?",
        "example": "Exemple : Cite les organites de la cellulaire."
    },
    "عدد": {
        "structure": "Indique le nombre exact d elements demandes.",
        "common_mistake": "Compte incorrect ou oubli d elements.",
        "question": "Combien y a-t-il d elements ?",
        "example": "Exemple : Combien y a-t-il de types d ARN ?"
    },
    "رتب": {
        "structure": "Classe les elements selon un critere donne.",
        "common_mistake": "Critere absent ou ordre incorrect.",
        "question": "Selon quel critere dois-tu classer ces elements ?",
        "example": "Exemple : Classe les acides amines selon leur polarite."
    },
    "ميّز": {
        "structure": "Distingue les elements en mettant en evidence leurs differences.",
        "common_mistake": "Confusion entre les elements ou differences mal identifiees.",
        "question": "Quelle est la difference principale entre ces deux elements ?",
        "example": "Exemple : Distingue l ADN de l ARN."
    },
    "استخرج": {
        "structure": "Tire une information precise a partir du document ou des donnees fournies.",
        "common_mistake": "Information inexacte ou source non citee.",
        "question": "Quelle information du document dois-tu extraire ?",
        "example": "Exemple : Extrait la valeur de la concentration a partir du graphique."
    },
    "استنتج": {
        "structure": "Tire une conclusion logique a partir des donnees et des documents fournis.",
        "common_mistake": "Conclusion non justifiee ou hors sujet.",
        "question": "Quelle donnee du document te permet d aboutir a cette conclusion ?",
        "example": "Exemple : Conclure a partir d un graphique sur l evolution d une population."
    },

    # ============================================
    # VERBES COMPLEXES (Note >= 10)
    # ============================================

    "وضّح في نص علمي": {
        "structure": "Ta reponse doit contenir 3 parties : Introduction (poser le probleme scientifique), Developpement (explication structuree + arguments), Conclusion (reponse au probleme).",
        "common_mistake": "Reponse sous forme de liste ou description simple au lieu d un texte structure.",
        "question": "Quelle est la problematique scientifique que tu dois poser dans l introduction ?",
        "example": "Exemple : Expliquer la photosynthese en suivant les 3 parties."
    },
    "أثبت": {
        "structure": "Tu dois apporter : Arguments clairs + Preuves issues des documents + Lien explicite entre preuves et conclusion.",
        "common_mistake": "Arguments sans lien avec les documents ou conclusion sans preuves.",
        "question": "Quelles preuves du document utilises-tu pour appuyer ton argument ?",
        "example": "Exemple : Prouver que la mitose permet le maintien du caryotype."
    },
    "برّر": {
        "structure": "Tu dois expliquer le pourquoi avec des justifications scientifiques appuyees par des donnees du document.",
        "common_mistake": "Justification generale sans preuve ou sans lien avec le document.",
        "question": "Quelle donnee du document justifie ton explication ?",
        "example": "Exemple : Justifier pourquoi la temperature influence l activite enzymatique."
    },
    "فسّر": {
        "structure": "Tu dois donner une explication scientifique claire en reliant les donnees du document au phenomene observe.",
        "common_mistake": "Explication trop descriptive sans lien avec les donnees.",
        "question": "Quelle observation du document expliques-tu ?",
        "example": "Exemple : Expliquer l augmentation de la courbe sur le graphique."
    },
    "ناقش": {
        "structure": "Tu dois presenter : Les arguments POUR + Les arguments CONTRE + Ta position argumentee finale.",
        "common_mistake": "Position sans argumentation ou analyse uniquement d un seul point de vue.",
        "question": "Veux-tu que je t aide sur les arguments POUR ou CONTRE en premier ?",
        "example": "Exemple : Discuter des avantages et inconvenients des OGM."
    },
    "اقترح فرضية": {
        "structure": "Ta hypothese doit etre logique, scientifique, testable et en lien avec les donnees du document.",
        "common_mistake": "Hypothese non scientifique ou hors contexte.",
        "question": "Sur quelle observation du document bases-tu ton hypothese ?",
        "example": "Exemple : Proposer une hypothese sur l effet d un facteur sur la photosynthese."
    },
    "حلّل": {
        "structure": "Tu dois decomposer le sujet en ses elements constitutifs, les etudier separement puis synthetiser.",
        "common_mistake": "Description au lieu d analyse ou absence de synthese.",
        "question": "Quels sont les elements constitutifs que tu dois analyser ?",
        "example": "Exemple : Analyser les facteurs influencant la photosynthese."
    },
    "قيّم": {
        "structure": "Tu dois porter un jugement argumente sur la validite, la pertinence ou la qualite d un element.",
        "common_mistake": "Jugement sans argument ou absence de criteres.",
        "question": "Selon quels criteres vas-tu evaluer cet element ?",
        "example": "Exemple : Evaluer l interet des vaccins a ARN messager."
    },
    "اقارن": {
        "structure": "Tu dois mettre en parallele deux ou plusieurs elements en identifiant ressemblances et differences selon des criteres clairs.",
        "common_mistake": "Un seul element decrit ou absence de criteres de comparaison.",
        "question": "Quels criteres vas-tu utiliser pour comparer ces elements ?",
        "example": "Exemple : Comparer la mitose et la meiose."
    },
    "أنجز رسما تخطيطيا": {
        "structure": "Realise un schema clair, legende, fonctionnel et respectant les conventions scientifiques.",
        "common_mistake": "Schema illisible, legendes manquantes ou incorrectes.",
        "question": "Quelles sont les parties principales que tu dois representer ?",
        "example": "Exemple : Realiser le schema d une synapse."
    },
}


def get_local_methodology_response(verb: str, message: str = "") -> Dict[str, Any]:
    verb_data = METHODOLOGY_RESPONSES.get(verb)

    if not verb_data:
        return {
            "reponse": "Peux-tu reformuler ta question en utilisant un verbe d action clair (وضّح، أثبت، برّر، ناقش...) ?",
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
    message_lower = message.lower()

    verb_mapping = {
        "وضّح": "وضّح في نص علمي",
        "وضح": "وضّح في نص علمي",
        "أثبت": "أثبت",
        "اثبت": "أثبت",
        "برّر": "برّر",
        "برر": "برّر",
        "ناقش": "ناقش",
        "فسّر": "فسّر",
        "فسر": "فسّر",
        "اقترح": "اقترح فرضية",
        "صف": "صف",
        "عرّف": "عرّف",
        "عرف": "عرّف",
        "استنتج": "استنتج",
        "سمّ": "سمّ",
        "سم": "سمّ",
        "ذكر": "ذكر",
        "عدد": "عدد",
        "رتب": "رتب",
        "ميّز": "ميّز",
        "ميز": "ميّز",
        "حلّل": "حلّل",
        "حلل": "حلّل",
        "قيّم": "قيّم",
        "قيم": "قيّم",
        "اقارن": "اقارن",
        "استخرج": "استخرج",
        "أنجز": "أنجز رسما تخطيطيا",
    }

    for key, verb in verb_mapping.items():
        if key in message_lower:
            return verb

    return None
