from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db
from services.phase3_service import get_avatar_details, get_friends_activity, get_live_stats

router = APIRouter(prefix="/api/phase3", tags=["Phase 3 - Avatar & Social"])


@router.get("/avatar")
async def get_avatar(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_avatar_details(current_user["id"], db)


@router.get("/live-stats/{chapter}")
async def live_stats(
    chapter: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_live_stats(chapter, db)


@router.get("/friends-activity")
async def friends_activity(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_friends_activity(current_user["id"], db)
