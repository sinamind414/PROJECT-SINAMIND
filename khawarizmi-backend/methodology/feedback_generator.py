VERB_FEEDBACK_TEMPLATES = {
    "وضّح في نص علمي": {
        "strength": "Tu as bien compris le phénomène scientifique.",
        "weakness_intro": "Il manque une introduction qui pose le problème scientifique.",
        "weakness_dev": "Le développement n'est pas assez structuré. Utilise des connecteurs logiques (أولاً, ثانياً, من جهة...).",
        "weakness_conclusion": "Absence de conclusion. Termine par un résumé qui répond au problème posé.",
        "advice_structure": "Structure ta réponse en 3 parties : Introduction (problème) → Développement (explication) → Conclusion (réponse).",
    },
    "صف": {
        "strength": "Tu as identifié les éléments importants.",
        "weakness_general": "La description est trop générale. Sois plus précis et utilise les termes scientifiques appropriés.",
        "advice": "Pour le verbe 'صف', décris avec précision en utilisant le vocabulaire scientifique exact.",
    },
    "عرف": {
        "strength": "Tu as capté l'essentiel du concept.",
        "weakness": "La définition manque de précision ou contient des informations inutiles. Reste concis et donne uniquement les caractéristiques essentielles.",
        "advice": "Une définition doit être courte et précise : donne les limites exactes du concept.",
    },
    "أثبت": {
        "strength": "Tu as bien compris ce qu'il fallait démontrer.",
        "weakness_arg": "Les arguments ne sont pas assez clairs ou ne sont pas liés aux documents.",
        "weakness_conclusion": "Il manque une conclusion qui valide ou infirme l'affirmation.",
        "advice": "Structure ta réponse : présente des arguments clairs appuyés par les documents, puis conclus.",
    },
    "برّر": {
        "strength": "Tu as identifié le phénomène à justifier.",
        "weakness": "La justification n'est pas assez appuyée par des preuves scientifiques.",
        "advice": "Pour justifier, donne au moins 2 raisons scientifiques appuyées par les documents ou le cours.",
    },
    "استنتج": {
        "strength": "Bon début de raisonnement.",
        "weakness": "La conclusion n'est pas suffisamment appuyée par les documents.",
        "advice": "Ta conclusion doit découler logiquement des données fournies. Cite les éléments qui t'ont permis de conclure.",
    },
    "فسر": {
        "strength": "Tu as identifié le résultat à expliquer.",
        "weakness": "L'explication est trop descriptive. Il faut interpréter scientifiquement le résultat.",
        "advice": "Relie le résultat observé à ses causes scientifiques en utilisant tes connaissances.",
    },
    "اقترح فرضية": {
        "strength": "Tu as compris le contexte du problème.",
        "weakness": "L'hypothèse n'est pas assez scientifique ou n'est pas en lien avec le contexte.",
        "advice": "Une hypothèse doit être une proposition scientifique testable, en lien direct avec le problème posé.",
    },
    "ناقش": {
        "strength": "Tu as présenté plusieurs aspects du sujet.",
        "weakness_analysis": "L'analyse des arguments n'est pas assez équilibrée. Présente les différents points de vue.",
        "weakness_position": "Il manque une prise de position personnelle argumentée.",
        "advice": "Structure ta discussion : présente les arguments pour et contre, puis prends position clairement.",
    },
    "أنجز رسما تخطيطيا": {
        "strength": "Le schéma est globalement correct.",
        "weakness": "Le schéma manque de légendes ou n'est pas assez clair.",
        "advice": "Un bon schéma doit être clair, légendé et respecter les conventions scientifiques.",
    },
}


def generate_feedback(
    verb: dict | None,
    task_classification: dict,
    structure_result: dict | None,
    weaknesses: list[str],
) -> dict:
    if not verb:
        return {
            "feedback_principal": "Analyse méthodologique non disponible pour cette question.",
            "points_forts": [],
            "points_faibles": [],
            "recommandation": "",
        }

    verb_key = verb["arabic"]
    templates = VERB_FEEDBACK_TEMPLATES.get(verb_key, {})
    strengths = []
    feedback_lines = []
    recommendations = []

    if templates.get("strength"):
        strengths.append(templates["strength"])

    if structure_result and verb["type"] == "complex":
        if structure_result["found"] == structure_result["total"]:
            strengths.append("La réponse respecte la structure attendue pour ce type de tâche.")
        else:
            missing_parts = [p for p, found in structure_result["parts"].items() if not found]
            for part in missing_parts:
                key = f"weakness_{part}"
                if key in templates:
                    feedback_lines.append(templates[key])
            if "advice_structure" in templates:
                recommendations.append(templates["advice_structure"])

    for w in weaknesses:
        if w == "too_general" and "weakness_general" in templates:
            feedback_lines.append(templates["weakness_general"])
        elif w == "missing_conclusion" and "weakness_conclusion" in templates:
            feedback_lines.append(templates["weakness_conclusion"])
        elif w == "missing_intro" and "weakness_intro" in templates:
            feedback_lines.append(templates["weakness_intro"])
        elif w == "weak_analysis" and "weakness_analysis" in templates:
            feedback_lines.append(templates["weakness_analysis"])
        elif w == "weak_argumentation" and "weakness_arg" in templates:
            feedback_lines.append(templates["weakness_arg"])

    if templates.get("advice"):
        recommendations.append(templates["advice"])

    if not feedback_lines and "weakness" in templates:
        feedback_lines.append(templates["weakness"])

    # Si aucun feedback spécifique, message générique
    if not feedback_lines and not recommendations:
        if verb["type"] == "complex":
            feedback_lines.append("La réponse peut être améliorée sur le plan méthodologique.")
            recommendations.append("Entraîne-toi à structurer ta réponse selon les exigences du verbe d'action.")
        else:
            feedback_lines.append("La réponse est correcte mais peut être plus précise.")

    feedback_principal = " ".join(feedback_lines) if feedback_lines else "Réponse globalement correcte."

    return {
        "feedback_principal": feedback_principal,
        "points_forts": strengths,
        "points_faibles": feedback_lines,
        "recommandation": " ".join(recommendations) if recommendations else "",
    }
