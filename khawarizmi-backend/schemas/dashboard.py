from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ProgressConceptPayload(BaseModel):
    matiere: str
    chapitre_id: str
    stability: float
    difficulty: float
    retrievability: float
    prochaine_revision: str | None
    interval_jours: int | None
    est_due: bool
    statut_revision: Literal["a_revoir_aujourdhui", "bientot", "stable"] | None = None
    priority: Literal["urgente", "haute", "normale"] | None = None


class BacPredictionDetailPayload(BaseModel):
    note: float
    coefficient: int
    nb_concepts: int
    retrievability: float


class BacPredictionPayload(BaseModel):
    note_globale: float
    par_matiere: dict[str, BacPredictionDetailPayload]
    points_forts: list[str] = []
    points_faibles: list[str] = []
    mention: str | None = None


class ProgressPayload(BaseModel):
    user_id: int | str | None = None
    nb_concepts: int
    dues_aujourd_hui: int
    prediction_bac: BacPredictionPayload | None = None
    concepts: list[ProgressConceptPayload]
    message: str | None = None


class OrientationRecommendationPayload(BaseModel):
    priorite: int
    type: Literal["cours", "action_verb", "document_analysis", "flashcards", "mindmap", "annales"]
    chapitre_slug: str | None
    chapitre_ar: str | None
    raison: str
    action: str
    score_priorite: int


class OrientationDuesPayload(BaseModel):
    flashcards: int
    action_verbs: int
    document_analysis: int


class OrientationPayload(BaseModel):
    prediction_bac: int | None = None
    dues_aujourd_hui: OrientationDuesPayload
    recommendations: list[OrientationRecommendationPayload]
    message: str


class WeekDayActivityPayload(BaseModel):
    date: str
    day_index: int
    dues_count: int
    reviewed_count: int
    status: Literal["done", "active", "missed", "planned"]
    primary_task: str | None = None
    primary_chapter: str | None = None
    load: Literal[0, 1, 2, 3]


class WeekActivityPayload(BaseModel):
    user_id: int | str | None = None
    week_start: str
    days: list[WeekDayActivityPayload]
    streak_days: int
    total_dues_this_week: int
    total_reviewed_this_week: int


class DueCardPayload(BaseModel):
    id: str
    micro_concept_id: str | None = None
    concept_id: str | None = None
    chapter: str | None = None
    difficulty: float | None = None
    stability: float | None = None
    state: int | str | None = None
    due_date: str | None = None
    next_review: str | None = None
    interval_jours: int | None = None


class DueCardsPayload(BaseModel):
    cards: list[DueCardPayload]
    total: int


class PriorityActionPayload(BaseModel):
    title: str
    reason: str
    href: str
    cta: str
    badge: str
    tone: Literal["danger", "mint", "amber"]
    source: Literal["orientation", "fsrs", "fallback"]


class ContinueCardPayload(BaseModel):
    title: str
    subtitle: str
    href: str
    cta: str
    source: Literal["orientation", "fsrs", "fallback"]


class StrategicChapterPayload(BaseModel):
    title: str
    subtitle: str
    lessonHref: str
    mindmapHref: str
    chapterSlug: str | None = None
    source: Literal["orientation", "fsrs", "fallback"]


class EnginePulsePayload(BaseModel):
    predictionBac: float | None = None
    dueToday: int
    flashcardsDue: int
    actionVerbsDue: int
    documentAnalysisDue: int
    urgentConceptsCount: int
    soonConceptsCount: int
    stableConceptsCount: int
    topPriorityConcept: ProgressConceptPayload | None = None
    topOrientation: OrientationRecommendationPayload | None = None
    dueCardsTotal: int
    source: Literal["backend"]


class OrchestrationPayload(BaseModel):
    priority_action: PriorityActionPayload
    continue_card: ContinueCardPayload
    strategic_chapter: StrategicChapterPayload
    engine_pulse: EnginePulsePayload
    generated_at: str
    source: Literal["backend_orchestrator"]


class DashboardUserPayload(BaseModel):
    id: int | str
    prenom: str | None = None
    filiere: str | None = None
    plan: str | None = None


class DashboardOrchestratorPayload(BaseModel):
    user: DashboardUserPayload
    progress: ProgressPayload
    orientation: OrientationPayload
    week_activity: WeekActivityPayload
    due_cards: DueCardsPayload
    orchestration: OrchestrationPayload
