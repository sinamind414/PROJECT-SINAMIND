"""schemas/document_model.py — Document DA versionné (keypoints, pas « un chiffre »)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Keypoint(BaseModel):
    id: str
    value: float
    unit: str | None = None
    tolerance: float = 0.0
    aliases: list[str] = Field(default_factory=list)
    label_ar: str = ""


class DocumentModel(BaseModel):
    doc_id: str
    version: str = "1.0.0"
    kind: Literal["curve", "table", "schema_text", "text"] = "text"
    keypoints: list[Keypoint] = Field(default_factory=list)
    trend: Literal[
        "increase",
        "decrease",
        "increase_then_plateau",
        "bell",
        "constant",
        "inverse",
        "unknown",
    ] = "unknown"
    trend_variants: list[str] = Field(default_factory=list)
    objects: list[str] = Field(default_factory=list)
