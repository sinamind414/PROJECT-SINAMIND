from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db
from services.phase4_service import award_methodology_points, check_methodology_badges

router = APIRouter(prefix="/api/phase4", tags=["Phase 4 - Méthodologie + Gamification"])


class MethodologyActionRequest(BaseModel):
    verb: str
    quality: str


@router.post("/methodology-action")
async def methodology_action(
    request: MethodologyActionRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await award_methodology_points(current_user["id"], request.verb, request.quality, db)
    return result


@router.get("/check-badges")
async def check_badges(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    badges = await check_methodology_badges(current_user["id"], db)
    return {"badges": badges}
