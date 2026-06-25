"""routes/diagnostic.py — Endpoint diagnostic méthodologique"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from deps import get_current_user
from methodology.diagnostic import diagnose_methodology_level, ERROR_PROFILES, generate_diagnostic_report

router = APIRouter(prefix="/api/diagnostic", tags=["Diagnostic"])


class DiagnosticRequest(BaseModel):
    scores: list[dict]


class ProfileResponse(BaseModel):
    id: str
    name: str
    description: str
    severity: str
    recommendation: str


class DiagnosticResponse(BaseModel):
    level: str
    level_label: str
    score_moyen: float
    error_profiles: list[ProfileResponse]
    recommendations: list[str]


@router.post("/methodology", response_model=DiagnosticResponse)
async def diagnostic_methodology(
    req: DiagnosticRequest,
    _user=Depends(get_current_user),
):
    result = diagnose_methodology_level(req.scores)
    return DiagnosticResponse(
        level=result["level"],
        level_label=result["level_label"],
        score_moyen=result["score_moyen"],
        error_profiles=[
            ProfileResponse(
                id=p["id"],
                name=p["name"],
                description=p["description"],
                severity=p.get("severity", "unknown"),
                recommendation=p.get("recommendation", ""),
            )
            for p in result.get("error_profiles", [])
        ],
        recommendations=result.get("recommendations", []),
    )


class ReportRequest(BaseModel):
    verb: str
    task_type: str
    structure: dict
    doc_usage: dict
    student_answer: str
    previous_answers: list[dict] | None = []


@router.post("/report")
async def get_diagnostic_report(req: ReportRequest):
    try:
        return generate_diagnostic_report(
            verb=req.verb,
            task_type=req.task_type,
            structure=req.structure,
            doc_usage=req.doc_usage,
            student_answer=req.student_answer,
            previous_answers=req.previous_answers or [],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles")
async def list_error_profiles():
    return {
        "profiles": [
            {
                "id": p["id"],
                "name": p["name"],
                "description": p["description"],
                "severity": p.get("severity", "unknown"),
                "recommendation": p.get("recommendation", ""),
            }
            for p in ERROR_PROFILES
        ]
    }
