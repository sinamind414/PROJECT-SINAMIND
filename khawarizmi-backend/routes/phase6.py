from uuid import uuid4

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db
from services.phase6_service import get_funnel_metrics, get_gamification_metrics, get_top_performers, get_user_engagement, track_event

router = APIRouter(prefix="/api/phase6", tags=["Phase 6 - Analytics"])


class AnalyticsEventRequest(BaseModel):
    session_id: str | None = Field(default=None, max_length=64)
    event_type: str = Field(min_length=1, max_length=80)
    feature: str | None = Field(default=None, max_length=80)
    chapter: str | None = Field(default=None, max_length=100)
    metadata: dict = Field(default_factory=dict)


@router.get("/metrics")
async def global_metrics(db: AsyncSession = Depends(get_db)):
    return await get_gamification_metrics(db)


@router.post("/events")
async def create_analytics_event(
    body: AnalyticsEventRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await track_event(
        db=db,
        user_id=current_user["id"],
        session_id=body.session_id or f"sess_{uuid4().hex[:16]}",
        event_type=body.event_type,
        feature=body.feature,
        chapter=body.chapter,
        metadata=body.metadata,
    )


@router.post("/session/start")
async def start_session(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session_id = f"sess_{uuid4().hex[:16]}"
    return await track_event(
        db=db,
        user_id=current_user["id"],
        session_id=session_id,
        event_type="session_start",
        feature="session",
    )


@router.get("/funnels")
async def funnels(db: AsyncSession = Depends(get_db)):
    return await get_funnel_metrics(db)


@router.get("/user-engagement")
async def user_engagement(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_user_engagement(current_user["id"], db)


@router.get("/top-performers")
async def top_performers(db: AsyncSession = Depends(get_db)):
    return await get_top_performers(10, db)
