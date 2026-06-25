"""Lesson Explanation Mode — Explication structuree de lecon
Mode "Explication de lecon" (0 token quand possible)
"""

from typing import Dict, Any

LESSON_EXPLANATIONS: Dict[str, Dict[str, Any]] = {

    "proteines": {
        "title": "Les Proteines",
        "introduction": "Les proteines sont des macromolecules essentielles a la vie. Elles sont formees d'acides amines et jouent des roles structuraux, enzymatiques, de transport et de signalisation.",
        "key_points": [
            "Structure des proteines : primaire, secondaire, tertiaire, quaternaire",
            "Role des proteines : enzymes, anticorps, transport (hemoglobine), structure (collagene)",
            "Synthese des proteines : transcription + traduction",
            "Denaturation et facteurs influencant la structure"
        ],
        "bac_verbs": [
            "وضّح في نص علمي : Expliquer la structure d une proteine",
            "أثبت : Prouver le role d une proteine dans une reaction",
            "برّر : Justifier pourquoi la structure tertiaire est importante",
            "فسّر : Expliquer l effet d une mutation sur une proteine"
        ],
        "common_mistakes": [
            "Confondre structure primaire et tertiaire",
            "Oublier le role des liaisons hydrogene et ponts disulfure",
            "Ne pas lier la structure a la fonction"
        ],
        "methodological_advice": "Dans une question sur les proteines, commence toujours par definir ce qu est une proteine, puis developpe sa structure avant d aborder sa fonction.",
        "next_question": "Veux-tu que je t explique plus en detail la structure des proteines ou leur synthese ?"
    },

    "mitose": {
        "title": "La Mitose",
        "introduction": "La mitose est un processus de division cellulaire qui permet la repartition egale du materiel genetique entre deux cellules filles.",
        "key_points": [
            "Phases de la mitose : Prophase, Metaphase, Anaphase, Telophase",
            "Role : Croissance, reparation des tissus, reproduction asexuee",
            "Maintien du caryotype (2n -> 2n)",
            "Difference avec la meiose"
        ],
        "bac_verbs": [
            "وضّح في نص علمي : Decrire les etapes de la mitose",
            "أثبت : Prouver que la mitose maintient le caryotype",
            "قارن : Comparer mitose et meiose"
        ],
        "common_mistakes": [
            "Confondre les phases de la mitose",
            "Oublier que la mitose conserve le nombre de chromosomes",
            "Melanger mitose et meiose"
        ],
        "methodological_advice": "Pour une question sur la mitose, structure ta reponse en decrivant les phases dans l ordre chronologique avec les evenements cles de chaque phase.",
        "next_question": "Veux-tu que je t explique les differences entre mitose et meiose ?"
    }
}


def get_lesson_explanation(lesson_key: str) -> Dict[str, Any]:
    lesson = LESSON_EXPLANATIONS.get(lesson_key.lower())

    if not lesson:
        return {
            "reponse": "Desole, je n ai pas encore d explication structuree pour cette lecon. Peux-tu preciser le chapitre ?",
            "type": "lesson_not_found",
            "fallback_active": False
        }

    response = (
        f"**{lesson['title']}**\n\n"
        f"**Introduction :**\n{lesson['introduction']}\n\n"
        f"**Points cles :**\n" + "\n".join([f"- {p}" for p in lesson['key_points']]) + "\n\n"
        f"**Verbes du Bac souvent utilises :**\n" + "\n".join([f"- {v}" for v in lesson['bac_verbs']]) + "\n\n"
        f"**Conseil methodologique :**\n{lesson['methodological_advice']}\n\n"
        f"-> {lesson['next_question']}"
    )

    return {
        "reponse": response,
        "type": "lesson_explanation",
        "lesson": lesson_key,
        "fallback_active": False
    }


def detect_lesson_request(message: str) -> str | None:
    message_lower = message.lower()

    lesson_keywords = {
        "proteine": "proteines",
        "proteines": "proteines",
        "mitose": "mitose",
        "meiose": "meiose",
        "photosynthese": "photosynthese",
        "respiration": "respiration",
        "adn": "adn",
        "cellule": "cellule",
    }

    for keyword, lesson in lesson_keywords.items():
        if keyword in message_lower:
            if any(word in message_lower for word in ["explique", "cours", "lecon", "chapitre", "resume"]):
                return lesson

    return None
