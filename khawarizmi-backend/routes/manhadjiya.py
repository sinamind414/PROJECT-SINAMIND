"""
routes/manhadjiya.py — 9 endpoints REST exposant les donnees Manhadjiya.

Tous les endpoints sont en /api/manhadjiya/* et retournent des donnees
issues des constantes du correcteur (correction_prompt, scientific_knowledge).
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from prompts.correction_prompt import (
    ANALYSIS_TERMINOLOGY,
    COMMON_BAC_ERRORS,
    MANHADJIYA_RUBRICS,
    REVISION_TIPS_AR,
    VERB_COGNITIVE_LEVELS,
    VERB_METHODOLOGY_AR,
)
from prompts.scientific_knowledge import (
    VERB_UNIT_MAP,
    get_contextual_remediation_data,
    get_practical_examples,
    get_units_for_verb,
)

router = APIRouter(prefix="/api/manhadjiya", tags=["Manhadjiya"])


@router.get("/revision-tips")
async def get_revision_tips():
    return {"data": REVISION_TIPS_AR, "count": sum(len(v) for v in REVISION_TIPS_AR.values())}


@router.get("/common-errors")
async def get_common_errors(category: str | None = Query(None, description="Filtre par categorie: methodology, knowledge, form")):
    if category:
        data = COMMON_BAC_ERRORS.get(category)
        if data is None:
            return {"error": f"Categorie '{category}' inconnue", "valid_categories": list(COMMON_BAC_ERRORS.keys())}
        return {"data": {category: data}, "count": len(data)}
    return {"data": COMMON_BAC_ERRORS, "count": sum(len(v) for v in COMMON_BAC_ERRORS.values())}


@router.get("/cognitive-levels")
async def get_cognitive_levels():
    return {"data": VERB_COGNITIVE_LEVELS, "count": sum(len(v) for v in VERB_COGNITIVE_LEVELS.values())}


@router.get("/analysis-terms")
async def get_analysis_terms():
    return {"data": ANALYSIS_TERMINOLOGY, "count": sum(len(v) for v in ANALYSIS_TERMINOLOGY.values())}


@router.get("/verbs")
async def get_verbs():
    result: list[dict[str, Any]] = []
    for slug in VERB_METHODOLOGY_AR:
        rubrics = MANHADJIYA_RUBRICS.get(slug)
        cognitive_level: str | None = None
        for level, verbs in VERB_COGNITIVE_LEVELS.items():
            for v in verbs:
                if slug in v or v.startswith(slug):
                    cognitive_level = level
                    break
        entry: dict[str, Any] = {"slug": slug, "methodology": VERB_METHODOLOGY_AR[slug]}
        if rubrics:
            entry["rubrics"] = rubrics
        if cognitive_level:
            entry["cognitive_level"] = cognitive_level
        entry["units"] = get_units_for_verb(slug)
        result.append(entry)
    return {"data": result, "count": len(result)}


@router.get("/verb/{slug}")
async def get_verb_detail(slug: str):
    methodology = VERB_METHODOLOGY_AR.get(slug)
    if methodology is None:
        return {"error": f"Verbe '{slug}' inconnu", "valid_slugs": list(VERB_METHODOLOGY_AR.keys())}
    rubrics = MANHADJIYA_RUBRICS.get(slug)
    cognitive_level: str | None = None
    for level, verbs in VERB_COGNITIVE_LEVELS.items():
        for v in verbs:
            if slug in v:
                cognitive_level = level
                break
    return {
        "slug": slug,
        "methodology": methodology,
        "rubrics": rubrics,
        "cognitive_level": cognitive_level,
        "units": get_units_for_verb(slug),
    }


@router.get("/verb-units")
async def get_verb_units():
    direct: dict[str, list[str]] = {}
    inverse: dict[str, list[str]] = {}
    for unit_id, verbs in VERB_UNIT_MAP.items():
        for verb_slug in verbs:
            direct.setdefault(verb_slug, []).append(unit_id)
            inverse.setdefault(unit_id, []).append(verb_slug)
    return {"direct": direct, "inverse": inverse}


@router.post("/contextual-remediation")
async def contextual_remediation(payload: dict[str, Any]):
    verb_slug = payload.get("verb_slug", "")
    context = payload.get("context", "")
    if not verb_slug:
        return {"error": "verb_slug requis"}
    data = get_contextual_remediation_data(verb_slug, context)
    return {"data": data}


@router.get("/practical-examples")
async def practical_examples(
    category: str | None = Query(None, description="Filtre par categorie"),
    unit: str | None = Query(None, description="Filtre par unite"),
):
    examples = get_practical_examples(category=category, unit=unit)
    return {"data": examples, "count": len(examples)}
