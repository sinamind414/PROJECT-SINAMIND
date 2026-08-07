"""
Routes Streak — API de la série quotidienne.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user
from services.streak_service import get_user_streak, record_activity, use_freeze

router = APIRouter(prefix="/api/streaks", tags=["streaks"])


class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    last_active_date: str | None
    freezes_remaining: int
    can_use_freeze: bool
    status: str


class ActivityResponse(BaseModel):
    streak: StreakResponse


@router.get("/me", response_model=StreakResponse)
async def get_my_streak(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    streak = await get_user_streak(db, str(current_user.id))
    return streak


@router.post("/me/activity", response_model=ActivityResponse)
async def record_my_activity(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    streak = await record_activity(db, str(current_user.id))
    return {"streak": streak}


@router.post("/me/freeze", response_model=StreakResponse)
async def use_my_freeze(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    success = await use_freeze(db, str(current_user.id))
    if not success:
        raise HTTPException(status_code=400, detail="Aucun freeze disponible ou streak déjà actif")
    streak = await get_user_streak(db, str(current_user.id))
    return streak
