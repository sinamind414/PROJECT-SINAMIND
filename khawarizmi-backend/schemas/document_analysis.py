"""Schémas Pydantic pour Document Analysis."""

from typing import Optional, List, Literal, Any
from pydantic import BaseModel, Field


# ── Documents ──────────────────────────────────────

class DocumentData(BaseModel):
    type: Literal["bar-chart", "line-chart", "multi-line-chart", "table", "flow", "image"]
    title_ar: str
    caption_ar: Optional[str] = None
    data: Any = None


# ── Questions ──────────────────────────────────────

class QuestionSummary(BaseModel):
    id: str
    verb_slug: str
    level: Literal["L1", "L2", "L3"] = "L2"
    n: int
    title_ar: str
    skill_ar: str
    doc_ref: str
    prompt_ar: str
    placeholder_ar: Optional[str] = None


class QuestionDetail(QuestionSummary):
    model_answer_ar: Optional[str] = None
    learning_focus_ar: Optional[str] = None


# ── Scénarios ──────────────────────────────────────

class ScenarioSummary(BaseModel):
    id: str
    slug: str
    chapter_slug: Optional[str] = None
    unit_key: str
    title_ar: str
    subtitle_ar: str
    context_ar: str
    nb_documents: int = 0
    nb_questions: int = 0
    dominant_skills: List[str] = []


class ScenarioDetail(ScenarioSummary):
    documents: List[DocumentData] = []
    questions: List[QuestionSummary] = []
    mindmap_node_id: Optional[str] = None


class ScenarioCorrection(BaseModel):
    """Scénario avec model answers — envoyé APRÈS évaluation."""
    scenario_id: str
    questions: List[QuestionDetail] = []


# ── Évaluation ─────────────────────────────────────

class EvaluateAnswerInput(BaseModel):
    verb_slug: str
    answer: str = Field(..., min_length=1)
    question_id: Optional[str] = None


class EvaluateRequest(BaseModel):
    scenario_id: str
    chapter_slug: Optional[str] = None
    answers: List[EvaluateAnswerInput] = Field(..., min_length=1)


class AnswerEvaluation(BaseModel):
    question_id: str
    verb_slug: str
    score: int
    score_max: int
    percentage: int
    success: List[str] = []
    errors: List[str] = []
    missing_markers: List[str] = []
    forbidden_found: List[str] = []
    advice: str = ""
    dominant_error_code: Optional[str] = None


class EvaluateResponse(BaseModel):
    scenario_id: str
    session_id: str
    score_global: int
    nb_questions: int
    evaluations: List[AnswerEvaluation] = []
    fsrs_updated: int = 0


# ── Progression FSRS ───────────────────────────────

class DaFsrsItem(BaseModel):
    verb_slug: str
    chapter_slug: str
    stability: float
    difficulty: float
    last_score: int
    attempts: int
    est_due: bool
    prochaine_revision: Optional[str] = None
    interval_jours: float


class DaProgressResponse(BaseModel):
    user_id: str
    nb_skills: int
    dues_aujourd_hui: int
    skills: List[DaFsrsItem] = []


# ── Révision FSRS ──────────────────────────────────

class DaReviewRequest(BaseModel):
    verb_slug: str
    chapter_slug: str
    rating: Literal[1, 2, 3, 4]
    score_percentage: Optional[int] = Field(default=None, ge=0, le=100)


# ── Weak spots ─────────────────────────────────────

class WeakSpot(BaseModel):
    verb_slug: str
    chapter_slug: str
    last_score: int
    attempts: int
    est_due: bool


class WeakSpotsResponse(BaseModel):
    user_id: str
    total: int
    weak_spots: List[WeakSpot] = []
