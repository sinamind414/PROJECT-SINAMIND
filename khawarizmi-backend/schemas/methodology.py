"""
Schémas Pydantic pour le Methodology Evaluator V2
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class VerbInfo(BaseModel):
    arabic: str = Field(..., description="Verbe en arabe")
    french: str = Field("", description="Traduction en français")
    type: str = Field("simple", description="simple ou complex")
    max_score: int = Field(10, description="Score maximal")
    definition: str = Field("", description="Définition complète")
    criteria: list[str] = Field(default_factory=list)
    common_mistakes: list[str] = Field(default_factory=list)


class StructureResult(BaseModel):
    structure_score: int = Field(0, ge=0, le=16)
    has_intro: bool = False
    has_development: bool = False
    has_conclusion: bool = False
    details: str = ""


class DocumentUsageResult(BaseModel):
    documents_used: int = 0
    total_documents: int = 0
    usage_quality: str = "none"
    details: list[dict] = Field(default_factory=list)
    feedback: str = ""


class FeedbackResult(BaseModel):
    verb: str = ""
    verb_french: str = ""
    task_type: str = "simple"
    score: int = 0
    max_score: int = 10
    message: str = ""
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendation: str = ""
    criteria: list[str] = Field(default_factory=list)
    common_mistakes: list[str] = Field(default_factory=list)


class MethodologyEvaluationResult(BaseModel):
    verb: str = ""
    verb_info: VerbInfo = Field(default_factory=VerbInfo)
    task_type: str = "simple"
    structure: StructureResult = Field(default_factory=StructureResult)
    document_usage: DocumentUsageResult = Field(default_factory=DocumentUsageResult)
    score: int = 0
    max_score: int = 10
    feedback: FeedbackResult = Field(default_factory=FeedbackResult)


class ErrorProfile(BaseModel):
    id: str
    name: str
    description: str = ""
    examples: list[str] = Field(default_factory=list)
    recommendation: str = ""
    severity: str = "medium"


class DiagnosticResult(BaseModel):
    level: str = "beginner"
    level_label: str = "Débutant"
    score_moyen: float = 0.0
    error_profiles: list[ErrorProfile] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class MethodologyFlashcard(BaseModel):
    card_id: str
    type: str = "verb_action"
    front: str
    back: str
    difficulty: str = "medium"
    category: str = "methodology"
    related_verb: str = ""


class MethodologyMindmap(BaseModel):
    id: str
    title: str
    description: str = ""
    nodes: list[dict] = Field(default_factory=list)
    links: list[dict] = Field(default_factory=list)
