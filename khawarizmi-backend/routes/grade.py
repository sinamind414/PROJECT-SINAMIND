"""POST /api/grade — S2. 0 LLM. Sans Rubric → 422 ungraded. Jamais VERB_RULES / L2."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from deps import get_current_user
from services.local_grader import TRAINING_BANNER_AR, UngradedError, grade_question
from services.rubric_store import list_question_ids, load

router = APIRouter(prefix="/api/grade", tags=["Grade"])


class GradeIn(BaseModel):
    question_id: str = Field(min_length=1, max_length=200)
    answer: str = Field(default="", max_length=20000)
    surface: Literal["da", "verb", "bac"] = "da"


def _public_grade_dict(result) -> dict:
    """Jamais model_answer, jamais variants."""
    diag = result.diagnosis
    return {
        "grader_version": result.grader_version,
        "rubric_id": result.rubric_id,
        "rubric_version": result.rubric_version,
        "verb_slug": result.verb_slug,
        "method_points": result.method_points,
        "method_points_max": result.method_points_max,
        "method_percent": result.method_percent,
        "method_label_ar": result.method_label_ar,
        "order_ok": result.order_ok,
        "science_status": result.science_status,
        "science_flags": result.science_flags,
        "science_capped": result.science_capped,
        "sanity_code": result.sanity_code,
        "stuffing_suspected": result.stuffing_suspected,
        "diagnosis": {"code": diag.code, "label_ar": diag.label_ar} if diag else None,
        "praise_ar": result.praise_ar,
        "next_step_ar": result.next_step_ar,
        "phrase_ar": result.phrase_ar,
        "criteria": [
            {
                "id": c.id,
                "status": c.status,
                "points_earned": c.points_earned,
                "points_max": c.points_max,
                "label_ar": c.label_ar,
            }
            for c in result.criteria
        ],
        "overall_training_percent": result.overall_training_percent,
        "source": "local_rubric",
        "banner_ar": TRAINING_BANNER_AR,
        "ungraded": False,
    }


@router.post("")
async def post_grade(
    body: GradeIn,
    current_user: dict = Depends(get_current_user),
):
    """Note une copie. ENABLE_EXTERNAL_LLM ignoré. user_id hors clé (équité)."""
    _ = current_user
    try:
        result = grade_question(body.question_id, body.answer)
    except UngradedError:
        return JSONResponse(
            status_code=422,
            content={
                "code": "ungraded",
                "erreur": "ungraded",
                "question_id": body.question_id,
                "status": 422,
                "banner_ar": TRAINING_BANNER_AR,
            },
        )
    return _public_grade_dict(result)


@router.get("/questions")
async def list_gradable(
    current_user: dict = Depends(get_current_user),
):
    _ = current_user
    return {"question_ids": list_question_ids(), "banner_ar": TRAINING_BANNER_AR}


@router.get("/rubric/{question_id}")
async def get_rubric_public(
    question_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Labels + steps. JAMAIS variants, model_answer, keypoints.values."""
    _ = current_user
    packed = load(question_id)
    if packed is None:
        return JSONResponse(
            status_code=422,
            content={
                "code": "ungraded",
                "erreur": "ungraded",
                "question_id": question_id,
                "status": 422,
            },
        )
    r = packed.rubric
    return {
        "rubric_id": r.rubric_id,
        "version": r.version,
        "verb_slug": r.verb_slug,
        "total_points": r.total_points,
        "criteria": [{"id": c.id, "label_ar": c.label_ar, "points": c.points} for c in r.criteria],
        "method_graph_steps": list(r.method_graph.steps) if r.method_graph else [],
        "banner_ar": TRAINING_BANNER_AR,
    }
