from sqlalchemy.ext.asyncio import AsyncSession

from methodology.verb_database import get_verb


def enrich_node(node: dict, detected_verbs: list[str]) -> None:
    label = node.get("label", "")
    verb = get_verb(label)
    if verb:
        node["methodology"] = {
            "verbe": verb["arabic"],
            "type": verb["type"],
            "max_score": verb["max_score"],
            "conseil": verb.get("common_mistakes", [""])[0] if verb.get("common_mistakes") else "",
        }
        if verb["arabic"] not in detected_verbs:
            detected_verbs.append(verb["arabic"])
    for child in node.get("enfants", []):
        enrich_node(child, detected_verbs)


async def enrich_mindmap_with_methodology(mindmap_data: dict) -> dict:
    enriched = mindmap_data.copy()
    detected_verbs: list[str] = []

    enriched["methodology"] = {
        "verbes_detectes": [],
        "structure_recommandee": "Introduction → Développement → Conclusion",
        "points_methodologie": 0,
    }

    if "racine" in enriched:
        enrich_node(enriched["racine"], detected_verbs)
    enriched["methodology"]["verbes_detectes"] = detected_verbs
    enriched["methodology"]["points_methodologie"] = len(detected_verbs) * 15

    return enriched


async def generate_methodological_mindmap(
    matiere: str,
    chapitre: str,
    filiere: str,
    user_id: int,
    db: AsyncSession,
    openai_client,
) -> dict:
    from services.mindmap_service import generate_mindmap

    base_mindmap = await generate_mindmap(
        matiere=matiere,
        chapitre=chapitre,
        filiere=filiere,
        niveau_detail="détaillé",
        user_id=str(user_id),
        db=db,
        openai_client=openai_client,
    )

    mindmap_data = base_mindmap.get("mindmap", {})
    enriched = await enrich_mindmap_with_methodology(mindmap_data)

    return {"status": "success", "mindmap": enriched, **{k: v for k, v in base_mindmap.items() if k not in ("status", "mindmap")}}


async def award_mindmap_methodology_points(user_id: int, mindmap_data: dict, db: AsyncSession) -> dict:
    verbs_used = mindmap_data.get("methodology", {}).get("verbes_detectes", [])
    points = len(verbs_used) * 15
    complex_keywords = ["وضّح", "أثبت", "برّر"]
    complex_verbs = [v for v in verbs_used if any(k in v for k in complex_keywords)]
    if len(complex_verbs) >= 2:
        points += 30

    return {
        "points": points,
        "message": f"+{points} points pour l'utilisation de {len(verbs_used)} verbes méthodologiques",
    }
