"""schemas/rubric.py — Barème versionné par question (pas VERB_RULES)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

VerbSlug = Literal[
    "analyse",
    "interpret",
    "deduce",
    "justify",
    "hypothesis",
    "scientific-text",
    "compare",
    "relationship",
    "define",
    "describe",
    "cite",
    "schematiser",
]

CheckKind = Literal[
    "any_of",
    "all_of",
    "forbidden_abs",
    "number_present",
    "cites_keypoint",
    "cites_trend",
    "cites_object",
    "min_length",
    "section_markers",
    "cooccurrence",
]


class RubricIntegrityError(ValueError):
    """Grille invalide — pas de fallback VERB_RULES."""


class GraveRef(BaseModel):
    id: str = ""
    pattern: str | None = None
    message_ar: str = ""
    cap_science: int = 40
    context_any: list[str] = Field(default_factory=list)


class Distractor(BaseModel):
    id: str = ""
    variants: list[str] = Field(default_factory=list)
    message_ar: str = ""


class Criterion(BaseModel):
    id: str
    label_ar: str
    points: float
    check: CheckKind
    variants: list[str] = Field(default_factory=list)
    window_tokens: int | None = None
    min_chars: int | None = None
    required: bool = True


class MethodGraph(BaseModel):
    steps: list[str]
    require_order: bool = True


class CriterionHit(BaseModel):
    id: str
    status: Literal["full", "partial", "absent"]
    points_earned: float
    points_max: float
    label_ar: str = ""


class Diagnosis(BaseModel):
    code: str
    label_ar: str = ""


class GradeResult(BaseModel):
    grader_version: str
    rubric_id: str
    rubric_version: str
    verb_slug: str

    method_points: float
    method_points_max: float
    method_percent: int
    method_label_ar: str
    order_ok: bool | None = None

    science_status: Literal["ok", "error", "not_applicable"]
    science_flags: list[str] = Field(default_factory=list)
    science_capped: bool = False
    caps_applied: list[str] = Field(default_factory=list)

    sanity_code: str
    stuffing_suspected: bool = False

    diagnosis: Diagnosis | None = None
    praise_ar: str = ""
    next_step_ar: str = ""
    phrase_ar: str = ""
    criteria: list[CriterionHit] = Field(default_factory=list)
    overall_training_percent: int = 0
    source: Literal["local_rubric"] = "local_rubric"
    from_cache: bool = False
    cacheable: bool = True


class Rubric(BaseModel):
    rubric_id: str
    version: str
    verb_slug: VerbSlug
    chapter_slug: str
    language: Literal["ar"] = "ar"
    total_points: float
    criteria: list[Criterion]
    method_graph: MethodGraph | None = None
    document_id: str | None = None
    theme_variants: list[str] = Field(default_factory=list)
    theme_min_hits: int = 1
    grave: list[GraveRef] = Field(default_factory=list)
    distractors: list[Distractor] = Field(default_factory=list)
    advice_by_gap: dict[str, str] = Field(default_factory=dict)
    advice_praise: dict[str, str] = Field(default_factory=dict)
    model_answer: str = ""
    source: Literal["teacher_authored"] = "teacher_authored"
    grader_min_version: str = "1.0.0"

    @model_validator(mode="after")
    def _invariants(self) -> "Rubric":
        total = sum(c.points for c in self.criteria)
        if abs(total - self.total_points) >= 1e-6:
            raise RubricIntegrityError(
                f"{self.rubric_id}: sum(criteria.points)={total} "
                f"!= total_points={self.total_points}"
            )
        if self.document_id:
            for c in self.criteria:
                if c.check == "number_present":
                    raise RubricIntegrityError(
                        f"{self.rubric_id}: number_present interdit "
                        f"sur un DA (document_id={self.document_id})"
                    )
        if self.method_graph:
            ids = {c.id for c in self.criteria}
            for step in self.method_graph.steps:
                if step not in ids:
                    raise RubricIntegrityError(
                        f"{self.rubric_id}: method_graph step '{step}' inconnu"
                    )
        return self
