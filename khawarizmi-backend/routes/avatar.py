from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db
from routes.gamification import RewardIn, _reject_client_delta
from services.avatar_service import add_xp, get_user_avatar
from services.economy import UnknownRewardAction, delta_for_action

router = APIRouter(prefix="/api/avatar", tags=["Avatar"])


@router.post("/add-xp")
async def add_avatar_xp(
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
    result = await add_xp(current_user["id"], delta, db)
    return result


@router.get("/")
async def get_avatar(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    avatar = await get_user_avatar(current_user["id"], db)
    return avatar
