"""Guidage en temps reel — Bac Blanc Intelligent (Semaine 6)"""

from typing import Dict, Any, List

GUIDANCE_TEMPLATES = {
    "وضّح في نص علمي": {
        "before": "Rappelle-toi : tu dois structurer ta reponse en 3 parties (Introduction -> Developpement -> Conclusion).",
        "during": "Verifie que tu as bien pose le probleme scientifique dans l'introduction.",
        "after": "As-tu termine par une conclusion qui repond au probleme ?"
    },
    "أثبت": {
        "before": "Tu dois apporter des preuves et arguments. Pense a exploiter les documents.",
        "during": "Chaque argument doit etre lie a un document ou une donnee precise.",
        "after": "As-tu fait le lien entre tes preuves et ta conclusion ?"
    },
    "برّر": {
        "before": "Explique le 'pourquoi' avec des justifications scientifiques.",
        "during": "Appuie chaque justification par des donnees du document.",
        "after": "Ta justification est-elle complete ?"
    },
    "ناقش": {
        "before": "Analyse les deux points de vue avant de prendre position.",
        "during": "Presente les arguments pour et contre de maniere equilibree.",
        "after": "As-tu clairement exprime ta position finale ?"
    }
}


def get_guidance(verb: str, phase: str = "before") -> str:
    template = GUIDANCE_TEMPLATES.get(verb, {})
    return template.get(phase, "Respecte la methodologie du verbe demande.")


def generate_real_time_guidance(
    instruction: str,
    current_text: str,
    verb_info: dict
) -> Dict[str, Any]:
    verb = verb_info.get("arabic", "")

    guidance = {
        "verb": verb,
        "phase": "during",
        "message": get_guidance(verb, "during"),
        "tips": []
    }

    if "مقدمة" not in current_text and "المشكل" not in current_text:
        guidance["tips"].append("Pense a commencer par une introduction claire.")

    if len(current_text.split()) < 30 and verb in ["وضّح في نص علمي", "أثبت"]:
        guidance["tips"].append("Developpe davantage ton argumentation.")

    return guidance
