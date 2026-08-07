"""
Routes Onboarding — API du parcours guidé.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user
from services import onboarding_service

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])


class StepRequest(BaseModel):
    step: int


@router.get("/me")
async def get_status(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await onboarding_service.get_onboarding_status(db, str(current_user.id))


@router.post("/step")
async def mark_onboarding_step(body: StepRequest, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if body.step not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="Step must be 1, 2, or 3")
    return await onboarding_service.mark_step(db, str(current_user.id), body.step)


@router.post("/welcome-gems")
async def claim_welcome_gems(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await onboarding_service.award_welcome_gems(db, str(current_user.id))
