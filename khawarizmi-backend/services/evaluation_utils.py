_MANDATORY_CONCEPTS = [
    "ARN polymerase", "polimerase", "بوليميراز",
    "brin transcrit", "الخيط المنقول", "القالب",
    "liaison peptidique", "الرابطة الببتيدية",
    "replication", "تضاعف",
    "mitose", "انقسام خيطي",
]


def is_mandatory(concept: str) -> bool:
    c = concept.lower().strip()
    return any(m.lower() in c for m in _MANDATORY_CONCEPTS)


def normalize_result(result: dict) -> dict:
    manquant = result.get("manquant", [])
    mandatory_missing = [m for m in manquant if is_mandatory(m)]

    if mandatory_missing and result.get("statut") == "CORRECT":
        result["statut"] = "PARTIEL"
        result["score"] = min(result.get("score", 10), 6)
        result["feedback"] = result.get("feedback", "").replace("Excellent", "Bien")

    if result.get("score", 0) == 0 and result.get("statut") != "FAUX":
        result["statut"] = "FAUX"

    return result


def safe_json_fallback() -> dict:
    return {
        "score": 0,
        "statut": "ERREUR",
        "feedback": (
            "L'algorithme de Khawarizmi est en cours de mise à jour. "
            "Réessaie dans quelques secondes."
        ),
        "manquant": [],
        "source": "FALLBACK_L3",
    }
