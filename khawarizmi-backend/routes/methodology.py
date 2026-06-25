"""routes/methodology.py — Endpoint évaluation méthodologique"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from methodology.evaluator import evaluate_methodology

router = APIRouter(prefix="/api/evaluate", tags=["Methodology"])


class MethodologyRequest(BaseModel):
    context: str = ""
    instruction: str
    student_answer: str
    documents: list[dict] | None = []


@router.post("/methodology")
async def evaluate_methodology_endpoint(req: MethodologyRequest):
    try:
        result = await evaluate_methodology(
            context=req.context,
            instruction=req.instruction,
            student_answer=req.student_answer,
            documents=req.documents or [],
        )
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
