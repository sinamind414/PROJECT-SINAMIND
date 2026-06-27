import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db, get_openai
from rate_limit import evaluate_limit, limiter
from schemas.ai_request import EvaluateOrchestratorRequest
from services.ai_orchestrator import get_orchestrator

logger = logging.getLogger("khawarizmi.ai_evaluate")
router = APIRouter(tags=["AI Évaluation"])


@router.post("/api/ai/evaluate")
@limiter.limit(evaluate_limit)
async def ai_evaluate_unified(
    request: Request,
    body: EvaluateOrchestratorRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    openai_client=Depends(get_openai),
):
    if not body.question_id or not body.reponse_eleve:
        raise HTTPException(status_code=400, detail="question_id et reponse_eleve requis")

    return await get_orchestrator().handle_evaluation(
        body=body, user=current_user, db=db, openai_client=openai_client,
    )
