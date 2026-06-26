from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db
from services.avatar_service import add_xp, get_user_avatar

router = APIRouter(prefix="/api/avatar", tags=["Avatar"])


@router.post("/add-xp")
async def add_avatar_xp(
    xp: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await add_xp(current_user["id"], xp, db)
    return result


@router.get("/")
async def get_avatar(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    avatar = await get_user_avatar(current_user["id"], db)
    return avatar
