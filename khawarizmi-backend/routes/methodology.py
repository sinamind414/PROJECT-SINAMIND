"""POST /api/evaluate/methodology — GELÉ. Plus de 2ᵉ cerveau regex.

Sans question_id L0 → 422 ungraded. Jamais evaluate_methodology().
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from services.grade_adapter import grade_or_none, to_verb_eval, ungraded_http
from services.local_grader import TRAINING_BANNER_AR

router = APIRouter(prefix="/api/evaluate", tags=["Methodology"])


class MethodologyRequest(BaseModel):
    context: str = ""
    instruction: str = ""
    student_answer: str = ""
    documents: list[dict] | None = None
    question_id: str | None = None


@router.post("/methodology")
async def evaluate_methodology_endpoint(req: MethodologyRequest):
    """0 LLM. Sans Rubric L0 → ungraded. Pas de fallback VERB_RULES."""
    qid = (req.question_id or "").strip() or "methodology"
    if qid != "methodology":
        result = grade_or_none(qid, req.student_answer)
        if result is not None:
            payload = to_verb_eval(result)
            payload["banner_ar"] = TRAINING_BANNER_AR
            return payload
    return JSONResponse(status_code=422, content=ungraded_http(qid))
