"""Route Dual Coding — Évaluation de schémas manuscrits.

GET  /api/dual-coding/schemas              → liste des schémas disponibles
GET  /api/dual-coding/schemas/{chapitre}   → schémas d'un chapitre
POST /api/dual-coding/evaluate             → évalue une photo de schéma
"""

import logging

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from deps import get_current_user, get_dual_coding
from rate_limit import evaluate_limit, limiter

logger = logging.getLogger("khawarizmi.api")
router = APIRouter(prefix="/api/dual-coding", tags=["Dual Coding"])


class EvaluateSchemaRequest(BaseModel):
    image_base64: str
    schema_id: str


class SchemaSummary(BaseModel):
    id: str
    nom: str


class EvaluateSchemaResponse(BaseModel):
    score: int = 0
    fleches_correctes: bool | None = None
    vocabulaire_exact: bool | None = None
    ordre_correct: bool | None = None
    elements_manquants: list[str] = []
    feedback: str = ""
    question_socratique: str = ""
    erreur: str | None = None


@router.get("/schemas", response_model=list[SchemaSummary])
async def list_schemas(
    current_user: dict = Depends(get_current_user),
    svc=Depends(get_dual_coding),
):
    """Liste tous les schémas disponibles pour le dual coding."""
    return [SchemaSummary(id=sid, nom=s["nom"]) for sid, s in svc.schemas.items()]


@router.get("/schemas/{chapitre}", response_model=list[SchemaSummary])
async def list_schemas_by_chapter(
    chapitre: str,
    current_user: dict = Depends(get_current_user),
    svc=Depends(get_dual_coding),
):
    """Liste les schémas d'un chapitre donné."""
    return [SchemaSummary(id=sid, nom=s["nom"]) for sid, s in svc.schemas.items() if s.get("chapitre") == chapitre]


@router.post("/evaluate", response_model=EvaluateSchemaResponse)
@limiter.limit(evaluate_limit)
async def evaluate_schema(
    request: Request,
    body: EvaluateSchemaRequest,
    current_user: dict = Depends(get_current_user),
    svc=Depends(get_dual_coding),
):
    """Évalue la photo d'un schéma manuscrit par Vision IA."""
    result = await svc.evaluer_schema_photo(
        image_base64=body.image_base64,
        schema_id=body.schema_id,
    )

    if isinstance(result, dict) and result.get("erreur"):
        return EvaluateSchemaResponse(
            score=0,
            erreur=result["erreur"],
            feedback=result.get("feedback", ""),
        )

    import json

    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            return EvaluateSchemaResponse(
                score=0,
                erreur="Réponse IA illisible",
                feedback="Une erreur technique est survenue. Réessaie.",
            )

    return EvaluateSchemaResponse(**result)
