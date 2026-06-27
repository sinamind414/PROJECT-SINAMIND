"""Routes Tuteur Méthodologique — Semaine 4"""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from methodology.chat_tutor import tutor_methodology_mode

logger = logging.getLogger("khawarizmi.tutor")
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
    except NotImplementedError:
        raise HTTPException(status_code=503, detail="Moteur méthodologique non initialisé")
    except Exception as e:
        logger.error(f"Erreur tutor methodology: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du moteur méthodologique")
