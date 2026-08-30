"""POST /api/evaluate/methodology — GELÉ. Plus de 2ᵉ cerveau regex.

Sans question_id L0 → 422 ungraded. Jamais evaluate_methodology().
S36 (audit 2026-08-30 F8) : auth requise + même quota que /api/grade
(avant : surface anonyme qui bypassait le budget 15/h).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from deps import get_current_user
from rate_limit import enforce_evaluate_quota
from services.grade_adapter import grade_or_none, to_verb_eval, ungraded_http
from services.grade_quota import should_count_quota
from services.local_grader import TRAINING_BANNER_AR

router = APIRouter(prefix="/api/evaluate", tags=["Methodology"])


class MethodologyRequest(BaseModel):
    context: str = ""
    instruction: str = ""
    student_answer: str = ""
    documents: list[dict] | None = None
    question_id: str | None = None


@router.post("/methodology")
async def evaluate_methodology_endpoint(
    request: Request,
    req: MethodologyRequest,
    current_user: dict = Depends(get_current_user),
):
    """0 LLM. Auth requise (S36). Sans Rubric L0 → ungraded. Pas de fallback VERB_RULES."""
    _ = current_user
    qid = (req.question_id or "").strip() or "methodology"
    if qid != "methodology":
        result = grade_or_none(qid, req.student_answer)
        if result is not None:
            if should_count_quota(sanity_code=result.sanity_code, from_cache=False):
                # S38 : réponse 429 directe (jamais une levée → handler → 500).
                over_quota = enforce_evaluate_quota(request)
                if over_quota is not None:
                    return over_quota
            payload = to_verb_eval(result)
            payload["banner_ar"] = TRAINING_BANNER_AR
            return payload
    return JSONResponse(status_code=422, content=ungraded_http(qid))
