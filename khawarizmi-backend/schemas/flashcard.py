from typing import Literal

from pydantic import BaseModel, Field


class DrillRequest(BaseModel):
    matiere: str = "sciences_naturelles"
    nb_questions: int = Field(default=12, ge=4, le=20)


class ScheduleRequest(BaseModel):
    micro_concept_id: str
    score_percent: float = Field(ge=0.0, le=100.0)
    fsrs_state: dict | None = None


class FlashcardCreateRequest(BaseModel):
    recto: str = Field(..., min_length=1, max_length=200)
    verso: str = Field(..., min_length=1, max_length=500)
    type: Literal["definition", "formule", "processus", "exception"] = "definition"
    importance: Literal["critique", "haute", "moyenne"] = "moyenne"
    matiere: str | None = None
    chapitre: str | None = None


class FlashcardReviewRequest(BaseModel):
    rating: Literal[1, 2, 3, 4]


class DrillSubmitRequest(BaseModel):
    """Phase 2 — drill : l'élève tape sa réponse, le moteur évalue pour de vrai."""
    question_id: str = Field(..., min_length=2)
    reponse_eleve: str = Field(..., min_length=1, max_length=10000)
    tentative: int = 1
    lang: str = "ar"


class QcmSubmitRequest(BaseModel):
    """Phase 3 — drill QCM : l'élève choisit une option, correction locale."""
    qcm_id: str = Field(..., min_length=2)
    selected_idx: int = Field(..., ge=0, le=3)
