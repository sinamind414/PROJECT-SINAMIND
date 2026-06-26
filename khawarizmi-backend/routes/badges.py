from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db
from services.badge_service import check_and_award_badges, get_all_badges

router = APIRouter(prefix="/api/badges", tags=["Badges"])


@router.get("/")
async def list_badges(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    badges = await get_all_badges()
    return {"badges": badges}


@router.post("/check")
async def check_badges(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    awarded = await check_and_award_badges(current_user["id"], db)
    return {"awarded": awarded}
