"""Plan d'action personnalise — Bac Blanc Intelligent"""

from typing import Dict, Any, List


def generate_personalized_action_plan(
    maturity_level: str,
    error_profiles: List[dict],
    weak_verbs: List[str] = None
) -> Dict[str, Any]:
    plan = {
        "level": maturity_level,
        "priority_actions": [],
        "recommended_exercises": [],
        "focus_areas": []
    }

    if maturity_level == "Debutant":
        plan["priority_actions"].append("Travailler la structure Introduction -> Developpement -> Conclusion")
        plan["recommended_exercises"].append("Exercices de structuration de texte scientifique")
    elif maturity_level == "Intermediaire":
        plan["priority_actions"].append("Ameliorer l'exploitation des documents")
        plan["recommended_exercises"].append("Exercices avec documents")
    elif maturity_level == "Avance":
        plan["priority_actions"].append("Travailler les verbes complexes (ناقش, أثبت)")
    else:
        plan["priority_actions"].append("Maintenir le niveau et varier les types de taches")

    for profile in error_profiles:
        plan["focus_areas"].append(profile.get("recommendation", ""))

    return plan
