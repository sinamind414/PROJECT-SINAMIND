from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db
from services.phase5_service import create_challenge, get_friend_activity, get_live_classroom_stats

router = APIRouter(prefix="/api/phase5", tags=["Phase 5 - Social & Live"])


@router.get("/live-stats/{chapter}")
async def live_stats(
    chapter: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_live_classroom_stats(chapter, db)


@router.get("/friends-activity")
async def friends_activity(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_friend_activity(current_user["id"], db)


@router.post("/challenge/{friend_id}")
async def send_challenge(
    friend_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_challenge(current_user["id"], friend_id, db)
