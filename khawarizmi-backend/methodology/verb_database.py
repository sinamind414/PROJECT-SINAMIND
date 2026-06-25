VERB_DATABASE = {
    "وضّح في نص علمي": {
        "id": 1,
        "arabic": "وضّح في نص علمي",
        "french": "Expliquer dans un texte scientifique",
        "type": "complex",
        "max_score": 20,
        "priority": "P0",
        "definition": "Rédiger un texte structuré (Introduction → Développement → Conclusion) qui explique un phénomène scientifique.",
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
        "required_structure": ["introduction", "development", "conclusion"],
        "structure_labels": {
            "introduction": "Introduction : poser le problème scientifique",
            "development": "Développement : explication structurée et argumentée",
            "conclusion": "Conclusion : répondre au problème posé",
        },
    },
    "صف": {
        "id": 2,
        "arabic": "صف",
        "french": "Décrire / Caractériser",
        "type": "simple",
        "max_score": 10,
        "priority": "P0",
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
        "required_structure": [],
        "structure_labels": {},
    },
    "عرف": {
        "id": 3,
        "arabic": "عرف",
        "french": "Définir",
        "type": "simple",
        "max_score": 10,
        "priority": "P0",
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
        "required_structure": [],
        "structure_labels": {},
    },
    "أثبت": {
        "id": 4,
        "arabic": "أثبت",
        "french": "Prouver / Démontrer",
        "type": "complex",
        "max_score": 15,
        "priority": "P0",
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
        "required_structure": ["argumentation", "conclusion"],
        "structure_labels": {
            "argumentation": "Argumentation : présenter les preuves et arguments",
            "conclusion": "Conclusion : valider ou infirmer l'affirmation",
        },
    },
    "برّر": {
        "id": 5,
        "arabic": "برّر",
        "french": "Justifier",
        "type": "complex",
        "max_score": 15,
        "priority": "P1",
        "definition": "Expliquer pourquoi un phénomène se produit en apportant des justifications.",
        "criteria": [
            "Justification appuyée par des preuves",
            "Lien avec le contexte de l'exercice",
        ],
        "common_mistakes": [
            "Justification sans preuve",
            "Réponse trop générale",
        ],
        "required_structure": ["justification"],
        "structure_labels": {
            "justification": "Justification : expliquer les causes avec des preuves",
        },
    },
    "استنتج": {
        "id": 6,
        "arabic": "استنتج",
        "french": "Conclure / Déduire",
        "type": "simple",
        "max_score": 10,
        "priority": "P1",
        "definition": "Tirer une conclusion logique à partir des données et des documents fournis.",
        "criteria": [
            "Conclusion logique et cohérente",
            "Appui sur les documents fournis",
        ],
        "common_mistakes": [
            "Conclusion non justifiée",
            "Conclusion hors sujet",
        ],
        "required_structure": [],
        "structure_labels": {},
    },
    "فسر": {
        "id": 7,
        "arabic": "فسر",
        "french": "Expliquer / Interpréter",
        "type": "complex",
        "max_score": 15,
        "priority": "P1",
        "definition": "Donner une explication scientifique d'un résultat ou d'un phénomène observé.",
        "criteria": [
            "Explication scientifique claire",
            "Lien avec les données du document",
        ],
        "common_mistakes": [
            "Explication trop descriptive",
            "Absence de lien avec les données",
        ],
        "required_structure": ["explanation"],
        "structure_labels": {
            "explanation": "Explication : interpréter scientifiquement les données",
        },
    },
    "اقترح فرضية": {
        "id": 8,
        "arabic": "اقترح فرضية",
        "french": "Proposer une hypothèse",
        "type": "complex",
        "max_score": 10,
        "priority": "P1",
        "definition": "Formuler une ou plusieurs hypothèses logiques et scientifiques pour expliquer un phénomène.",
        "criteria": [
            "Hypothèse logique et scientifique",
            "Cohérente avec le contexte",
        ],
        "common_mistakes": [
            "Hypothèse non scientifique",
            "Hypothèse hors contexte",
        ],
        "required_structure": [],
        "structure_labels": {},
    },
    "ناقش": {
        "id": 9,
        "arabic": "ناقش",
        "french": "Discuter",
        "type": "complex",
        "max_score": 15,
        "priority": "P2",
        "definition": "Analyser différents points de vue ou arguments et prendre position de manière argumentée.",
        "criteria": [
            "Analyse équilibrée des arguments",
            "Prise de position argumentée",
        ],
        "common_mistakes": [
            "Position sans argumentation",
            "Analyse trop superficielle",
        ],
        "required_structure": ["analysis", "position"],
        "structure_labels": {
            "analysis": "Analyse : présenter les différents arguments",
            "position": "Position : prendre position de manière argumentée",
        },
    },
    "أنجز رسما تخطيطيا": {
        "id": 10,
        "arabic": "أنجز رسما تخطيطيا",
        "french": "Réaliser un schéma",
        "type": "simple",
        "max_score": 10,
        "priority": "P2",
        "definition": "Réaliser un schéma clair, légendé et fonctionnel.",
        "criteria": [
            "Schéma clair et lisible",
            "Légendes correctes et complètes",
            "Respect des conventions scientifiques",
        ],
        "common_mistakes": [
            "Schéma illisible",
            "Légendes manquantes ou incorrectes",
        ],
        "required_structure": [],
        "structure_labels": {},
    },
}


def get_verb(arabic: str) -> dict | None:
    for key, data in VERB_DATABASE.items():
        if key == arabic:
            return data
    return None


def get_all_verbs() -> list[dict]:
    return list(VERB_DATABASE.values())


_ARABIC_DIACRITICS = str.maketrans(
    {
        chr(0x064B): "",
        chr(0x064C): "",
        chr(0x064D): "",
        chr(0x064E): "",
        chr(0x064F): "",
        chr(0x0650): "",
        chr(0x0651): "",
        chr(0x0652): "",
        chr(0x0670): "",
        chr(0x0640): "",
    }
)
_ALEF_MAP = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا"})
_TA_MAP = str.maketrans({"ة": "ه"})


def _normalize(text: str) -> str:
    t = text.translate(_ARABIC_DIACRITICS)
    t = t.translate(_ALEF_MAP)
    t = t.translate(_TA_MAP)
    return t.strip()


def identify_verb(instruction: str) -> dict | None:
    norm_instruction = _normalize(instruction)
    for verb_key in VERB_DATABASE:
        norm_verb = _normalize(verb_key)
        if norm_verb in norm_instruction:
            return VERB_DATABASE[verb_key]
    return None
