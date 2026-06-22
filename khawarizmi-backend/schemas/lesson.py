"""Schémas Pydantic pour les Active Lessons."""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class QuickCheck(BaseModel):
    type: Literal["true-false", "mcq", "short-answer"]
    question_ar: str
    options: List[str] = []
    correct_index: Optional[int] = None
    expected_keywords: List[str] = []
    explanation_ar: str = ""


class LessonBlock(BaseModel):
    id: str
    block_type: Literal["summary", "concept", "analogy", "mistake", "bac_link"]
    sort_order: int
    title_ar: str
    body_ar: str
    visual_hint: Optional[str] = None
    quick_check: QuickCheck


class LessonResponse(BaseModel):
    chapter_slug: str
    blocks: List[LessonBlock] = []
    blocks_total: int = 0


class CheckAnswerRequest(BaseModel):
    block_id: str
    answer: str = Field(..., min_length=1)


class CheckAnswerResponse(BaseModel):
    block_id: str
    correct: bool
    explanation_ar: str
    score_percentage: int
    blocks_completed: int
    blocks_total: int
    lesson_completed: bool
