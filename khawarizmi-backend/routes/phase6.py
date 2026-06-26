from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db
from services.phase6_service import get_gamification_metrics, get_top_performers, get_user_engagement

router = APIRouter(prefix="/api/phase6", tags=["Phase 6 - Analytics"])


@router.get("/metrics")
async def global_metrics(db: AsyncSession = Depends(get_db)):
    return await get_gamification_metrics(db)


@router.get("/user-engagement")
async def user_engagement(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_user_engagement(current_user["id"], db)


@router.get("/top-performers")
async def top_performers(db: AsyncSession = Depends(get_db)):
    return await get_top_performers(10, db)
