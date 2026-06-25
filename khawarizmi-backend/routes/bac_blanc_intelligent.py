"""Routes Bac Blanc Intelligent — Semaine 6"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from methodology.bac_blanc_guidance import generate_real_time_guidance
from methodology.bac_blanc_feedback import generate_bac_blanc_structured_feedback
from methodology.action_plan import generate_personalized_action_plan

router = APIRouter(prefix="/api/bac-blanc", tags=["Bac Blanc Intelligent"])


class BacBlancRequest(BaseModel):
    context: str
    instruction: str
    student_answer: str
    documents: Optional[list] = []
    previous_answers: Optional[list] = []


@router.post("/feedback")
async def get_structured_feedback(request: BacBlancRequest):
    try:
        feedback = await generate_bac_blanc_structured_feedback(
            context=request.context,
            instruction=request.instruction,
            student_answer=request.student_answer,
            documents=request.documents,
            previous_answers=request.previous_answers
        )
        return feedback
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/action-plan")
async def get_action_plan(request: BacBlancRequest):
    try:
        feedback = await generate_bac_blanc_structured_feedback(
            context=request.context,
            instruction=request.instruction,
            student_answer=request.student_answer,
            documents=request.documents,
            previous_answers=request.previous_answers
        )
        plan = generate_personalized_action_plan(
            maturity_level=feedback.get("maturity_level", "Debutant"),
            error_profiles=feedback.get("error_profiles", [])
        )
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
