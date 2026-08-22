"""Schémas des exercices de chapitre formatifs."""
from typing import Literal

from pydantic import BaseModel, Field


class ChapterExerciseEvaluateRequest(BaseModel):
    answer: str = Field(min_length=3, max_length=4000)
    language: Literal["ar", "fr"] = "ar"
