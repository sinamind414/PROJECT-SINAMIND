from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class TunnelEventRequest(BaseModel):
    session_id: str
    type: str
    payload: dict[str, Any] = {}
    client_event_id: Optional[str] = None
    client_ts: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TunnelEventResponse(BaseModel):
    event_id: str


class RecallDueItem(BaseModel):
    recall_item_id: str
    lesson_id: str
    concept_id: Optional[str] = None
    stage: int = 0
    next_review_at: datetime
    last_result: Optional[str] = None


class RecallResultRequest(BaseModel):
    success: bool


class RecallResultResponse(BaseModel):
    recall_item_id: str
    stage: int
    next_review_at: datetime
    last_result: str
