"""Routes Tuteur Méthodologique — Semaine 4"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from methodology.chat_tutor import tutor_methodology_mode

router = APIRouter(prefix="/api/tutor", tags=["Tuteur Méthodologique"])


class TutorRequest(BaseModel):
    instruction: str
    student_answer: str = ""
    mode: str = "explain"


@router.post("/methodology")
async def tutor_methodology(request: TutorRequest):
    try:
        result = await tutor_methodology_mode(
            instruction=request.instruction,
            student_answer=request.student_answer,
            mode=request.mode,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
