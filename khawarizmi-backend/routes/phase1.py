from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db
from services.phase1_service import calculate_combo, get_next_actions

router = APIRouter(prefix="/api/phase1", tags=["Phase 1 - One More Click"])


class NextActionsRequest(BaseModel):
    last_action: str


class ComboRequest(BaseModel):
    success: bool


@router.post("/next-actions")
async def get_next_actions_endpoint(
    request: NextActionsRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    actions = await get_next_actions(current_user["id"], request.last_action, db)
    return {"actions": actions}


@router.post("/combo")
async def update_combo(
    request: ComboRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await calculate_combo(current_user["id"], request.success, db)
    return result
