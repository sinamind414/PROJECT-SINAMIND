"""
Routes Duels — defi 1v1 entre amis.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user
from services import duel_service

router = APIRouter(prefix="/api/duels", tags=["duels"])


class CreateDuelRequest(BaseModel):
    verb_slug: str | None = None


class DuelAnswerRequest(BaseModel):
    score: int


@router.post("")
async def create_duel(body: CreateDuelRequest, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await duel_service.create_duel(db, str(current_user.id), body.verb_slug)


@router.get("/by-token/{share_token}")
async def get_duel_by_token(share_token: str, db: AsyncSession = Depends(get_db)):
    duel = await duel_service.get_duel_by_token(db, share_token)
    if not duel:
        raise HTTPException(status_code=404, detail="Duel introuvable ou expiré")
    return duel


@router.post("/{duel_id}/accept")
async def accept_duel(duel_id: str, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select

    from models.duel import Duel
    result = await db.execute(select(Duel).where(Duel.id == duel_id))
    duel = result.scalar_one_or_none()
    if not duel:
        raise HTTPException(status_code=404, detail="Duel introuvable")
    try:
        return await duel_service.accept_duel(db, str(current_user.id), duel.share_token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{duel_id}/answer")
async def submit_answer(duel_id: str, body: DuelAnswerRequest, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        return await duel_service.submit_duel_answer(db, str(current_user.id), duel_id, body.score)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{duel_id}/status")
async def duel_status(duel_id: str, db: AsyncSession = Depends(get_db)):
    return await duel_service.get_duel_status(db, duel_id)


@router.get("/leaderboard")
async def duel_leaderboard(db: AsyncSession = Depends(get_db)):
    return await duel_service.get_leaderboard(db)
