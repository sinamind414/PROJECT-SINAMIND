from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class TunnelEventRequest(BaseModel):
    session_id: str
    type: str
    payload: dict[str, Any] = {}
    client_event_id: str | None = None
    client_ts: datetime | None = None

    model_config = {"from_attributes": True}


class TunnelEventResponse(BaseModel):
    event_id: str


class RecallDueItem(BaseModel):
    recall_item_id: str
    lesson_id: str
    concept_id: str | None = None
    stage: int = 0
    next_review_at: datetime
    last_result: str | None = None


class RecallResultRequest(BaseModel):
    success: bool


class RecallResultResponse(BaseModel):
    recall_item_id: str
    stage: int
    next_review_at: datetime
    last_result: str
