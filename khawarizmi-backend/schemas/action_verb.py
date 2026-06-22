from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class MethodologyStep(BaseModel):
    titleAr: str
    descriptionAr: str
    required: bool = False


class ScoringRule(BaseModel):
    code: str
    labelAr: str
    points: int
    checkType: Literal["manual", "keyword", "forbidden_absence", "structure"] = "manual"


class VerbExample(BaseModel):
    answerAr: str
    explanationAr: str


class ActionVerbSummary(BaseModel):
    slug: str
    ar: str
    fr: str
    category: str
    priority: str


class ActionVerbDetail(BaseModel):
    slug: str
    ar: str
    fr: str
    category: str
    priority: str
    definition_ar: str
    objective_ar: str
    formula_ar: Optional[str] = None
    steps: List[MethodologyStep] = []
    required_markers: List[str] = []
    forbidden_markers: List[str] = []
    common_errors: List[str] = []
    scoring_rules: List[ScoringRule] = []
    bad_example: Optional[VerbExample] = None
    good_example: Optional[VerbExample] = None
    feedback_template_ar: Optional[str] = None


class ActionVerbExercise(BaseModel):
    id: str
    verb_slug: str
    type: Literal["identification", "application", "bac_style"] = "application"
    question_ar: str
    context_ar: Optional[str] = None
    model_answer_ar: Optional[str] = None
    difficulty: int = Field(default=3, ge=1, le=5)


class EvaluateRequest(BaseModel):
    verb_slug: str
    answer: str = Field(..., min_length=1)
    exercise_id: Optional[str] = None


class EvaluateResponse(BaseModel):
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
    allow_second_attempt: bool = True


class VerbReviewRequest(BaseModel):
    rating: Literal[1, 2, 3, 4]
    score_percentage: Optional[int] = Field(default=None, ge=0, le=100)


class VerbProgressItem(BaseModel):
    verb_slug: str
    stability: float
    difficulty: float
    last_score: int
    attempts: int
    est_due: bool
    prochaine_revision: Optional[str] = None
    interval_jours: float


class VerbProgressResponse(BaseModel):
    user_id: str
    nb_verbs: int
    dues_aujourd_hui: int
    verbs: List[VerbProgressItem] = []
