"""
Routes Leaderboard — classements.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user
from database import get_db
from services.leaderboard_service import get_leaderboard, get_user_rank, update_user_stats

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("")
async def leaderboard(
    scope: str = Query("national"),
    wilaya: str | None = Query(None),
    school: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await get_leaderboard(db, scope=scope, wilaya_code=wilaya, school_name=school, limit=limit)


@router.get("/me")
async def my_rank(
    scope: str = Query("national"),
    wilaya: str | None = Query(None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rank = await get_user_rank(db, str(current_user.id), scope=scope, wilaya_code=wilaya)
    return {"rank": rank, "scope": scope}


@router.post("/refresh")
async def refresh_my_stats(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await update_user_stats(db, str(current_user.id))
