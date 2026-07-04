from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import get_db
from services.pulse_service import (
    complete_card,
    get_or_create_today_cards,
    get_streak_summary,
)

router = APIRouter(prefix="/api/pulse", tags=["pulse"])


@router.get("/today")
async def pulse_today(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cards = await get_or_create_today_cards(user["id"], db)
    streak = await get_streak_summary(user["id"], db)
    return {"cards": cards, "streak": streak}


@router.get("/streak")
async def pulse_streak(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_streak_summary(user["id"], db)


@router.post("/card/{card_id}/complete")
async def pulse_complete(
    card_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await complete_card(user["id"], card_id, db)
