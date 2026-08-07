"""
Routes Gems — API de la monnaie interne.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user
from services import gems_service
from services.shop_service import get_shop_catalogue, get_shop_item

router = APIRouter(prefix="/api/gems", tags=["gems"])


class GemsBalance(BaseModel):
    balance: int
    total_earned: int
    total_spent: int


class SpendRequest(BaseModel):
    item_id: str


@router.get("/me", response_model=GemsBalance)
async def get_my_gems(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await gems_service.get_user_gems(db, str(current_user.id))


@router.get("/transactions")
async def get_my_transactions(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await gems_service.get_transactions(db, str(current_user.id))


@router.post("/spend", response_model=GemsBalance)
async def spend_my_gems(body: SpendRequest, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    item = get_shop_item(body.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item introuvable")
    try:
        return await gems_service.spend_gems(db, str(current_user.id), item["cost"], f"shop:{body.item_id}", body.item_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/shop")
async def get_shop():
    return get_shop_catalogue()


@router.get("/leaderboard")
async def gems_leaderboard(db: AsyncSession = Depends(get_db)):
    return await gems_service.get_gems_leaderboard(db)
