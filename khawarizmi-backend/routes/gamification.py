from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, model_validator
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db
from services.economy import UnknownRewardAction, delta_for_action
from services.gamification_service import add_points, get_or_create_streak, update_streak

router = APIRouter(prefix="/api/gamification", tags=["Gamification"])


class RewardIn(BaseModel):
    action: str
    points: int | None = None
    xp: int | None = None

    @model_validator(mode="after")
    def _no_client_delta(self) -> "RewardIn":
        if self.points is not None or self.xp is not None:
            raise ValueError("delta client interdit — envoie action")
        return self


def _reject_client_delta(request: Request) -> None:
    if "points" in request.query_params or "xp" in request.query_params:
        raise HTTPException(400, "delta client interdit — envoie action")


@router.post("/streak/update")
async def update_user_streak(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await update_streak(current_user["id"], db)
    return result


@router.post("/points/add")
async def add_user_points(
    request: Request,
    body: RewardIn,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _reject_client_delta(request)
    try:
        delta = delta_for_action(body.action)
    except UnknownRewardAction:
        raise HTTPException(400, "action inconnue")
    result = await add_points(current_user["id"], delta, db)
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
