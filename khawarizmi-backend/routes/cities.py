"""
Routes Cities — API de la carte des verbes d'Algérie.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user
from services import city_service

router = APIRouter(prefix="/api/cities", tags=["cities"])


@router.get("")
async def get_cities(db: AsyncSession = Depends(get_db)):
    return await city_service.get_all_cities(db)


@router.get("/me")
async def get_my_cities(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await city_service.get_all_cities(db, str(current_user.id))


@router.get("/stats")
async def national_stats(db: AsyncSession = Depends(get_db)):
    return await city_service.get_national_stats(db)


@router.post("/{city_id}/unlock")
async def unlock_city(city_id: str, body: dict, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    level = body.get("level", 1)
    if level not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="Level must be 1, 2, or 3")
    return await city_service.unlock_city(db, str(current_user.id), city_id, level)


@router.get("/leaderboard")
async def wilaya_ranking(db: AsyncSession = Depends(get_db)):
    return await city_service.get_wilaya_ranking(db)
