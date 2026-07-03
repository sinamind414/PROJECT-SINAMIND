"""
Routes Badges — API des 12 badges secrets.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import get_db
from services.badge_service import get_user_badges

router = APIRouter(prefix="/api/badges", tags=["badges"])


class BadgeItem(BaseModel):
    code: str
    icon: str
    title_ar: str
    desc_ar: str
    unlocked: bool
    unlocked_at: str | None
    sprint2: bool = False


class BadgesResponse(BaseModel):
    badges: list[BadgeItem]
    unlocked_count: int
    total: int


@router.get("/me", response_model=BadgesResponse)
async def get_my_badges(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    badges = await get_user_badges(db, str(current_user.id))
    unlocked = sum(1 for b in badges if b["unlocked"])
    return {
        "badges": badges,
        "unlocked_count": unlocked,
        "total": len(badges),
    }
