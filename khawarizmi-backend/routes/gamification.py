from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db
from services.gamification_service import add_points, get_or_create_streak, update_streak

router = APIRouter(prefix="/api/gamification", tags=["Gamification"])


@router.post("/streak/update")
async def update_user_streak(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await update_streak(current_user["id"], db)
    return result


@router.post("/points/add")
async def add_user_points(
    points: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await add_points(current_user["id"], points, db)
    return result


@router.get("/streak")
async def get_streak(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    streak = await get_or_create_streak(current_user["id"], db)
    return {
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
    }
