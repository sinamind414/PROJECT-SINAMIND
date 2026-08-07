"""schemas/evaluation_v2.py — Contrats stricts de l'évaluation v2 (audit P0-4.1).

Trois vues du même résultat :
- Internal : contient tout (dont llm_raw pour le debug interne).
- Public   : jamais llm_raw / prompt brut / copie élève.
- Audit    : hash-only + métadonnées (pour correction_audit).
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

SourceV2 = Literal[
    "local", "llm", "llm_recovered", "llm_v2", "llm_retried",
    "sanity", "llm_error", "cached_evaluation",
]

DominantErrorCode = Literal[
    "scientific_error", "methodology_error", "off_topic", "partial_correct",
    "all_correct", "insufficient", "gibberish", "too_short", "empty",
    "not_arabic", "repeated_chars", "server_error", "unknown",
]


class HighlightV2(BaseModel):
    start: int
    end: int
    type: str
    message_ar: str = ""


class UnmatchedCriterionV2(BaseModel):
    criterion: str
    why_ar: str = ""
    from_model_answer: str = ""


class RemediationV2(BaseModel):
    page: int | None = None
    lesson_title: str | None = None
    advice_ar: str | None = None


class EvaluationResultV2Internal(BaseModel):
    """Contrat interne complet — peut contenir llm_raw (debug)."""
    source: SourceV2
    score: int
    score_max: int
    percentage: int
    highlights: list[HighlightV2] = Field(default_factory=list)
    matched_criteria: list[str] = Field(default_factory=list)
    unmatched_criteria: list[UnmatchedCriterionV2] = Field(default_factory=list)
    feedback_ar: str = ""
    advice_ar: str = ""
    confidence: float = 0.5
    sanity_code: str = "ok"
    dominant_error_code: DominantErrorCode = "unknown"
    missing: list[dict[str, Any]] = Field(default_factory=list)
    success: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    remediation: RemediationV2 | None = None
    provider: str = "unknown"
    model: str = "unknown"
    finish_reason: str = "unknown"
    parse_status: str = "not_called"
    attempts: int = 1
    prompt_hash: str | None = None
    student_answer_hash: str | None = None
    llm_raw_hash: str | None = None
    llm_raw: str | None = None  # INTERNE : ne jamais exposer publiquement


class EvaluationResultV2Public(BaseModel):
    """Vue publique — llm_raw structurellement absent (jamais dans une réponse API)."""
    source: SourceV2
    score: int
    score_max: int
    percentage: int
    highlights: list[HighlightV2] = Field(default_factory=list)
    matched_criteria: list[str] = Field(default_factory=list)
    unmatched_criteria: list[UnmatchedCriterionV2] = Field(default_factory=list)
    feedback_ar: str = ""
    advice_ar: str = ""
    confidence: float = 0.5
    sanity_code: str = "ok"
    dominant_error_code: DominantErrorCode = "unknown"
    missing: list[dict[str, Any]] = Field(default_factory=list)
    success: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    remediation: RemediationV2 | None = None
    provider: str = "unknown"
    model: str = "unknown"
    finish_reason: str = "unknown"
    parse_status: str = "not_called"
    attempts: int = 1
    prompt_hash: str | None = None
    student_answer_hash: str | None = None
    llm_raw_hash: str | None = None

    @classmethod
    def from_internal(cls, internal: EvaluationResultV2Internal) -> EvaluationResultV2Public:
        data = internal.model_dump(exclude={"llm_raw"})
        return cls(**data)


class EvaluationResultV2Audit(BaseModel):
    """Vue audit — hash-only + métadonnées (jamais de contenu)."""
    user_id: int | None = None
    session_id: str | None = None
    question_hash: str | None = None
    student_answer_hash: str | None = None
    prompt_hash: str | None = None
    verb_slug: str
    sanity_code: str
    source: SourceV2
    provider: str
    model: str
    finish_reason: str
    score: int
    score_max: int
    percentage: int
    confidence: float
    parse_status: str
    attempts: int
    error_message_hash: str | None = None


class CorrectionCacheEntry(BaseModel):
    """Entrée du cache de correction (audit C2 / P0-4.3)."""
    key: str
    result: EvaluationResultV2Public
    created_at: str
