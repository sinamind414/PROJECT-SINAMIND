from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db
from services.mystery_box_service import create_mystery_box, get_available_boxes, open_mystery_box

router = APIRouter(prefix="/api/mystery-box", tags=["Mystery Box"])


class OpenBoxRequest(BaseModel):
    box_id: str


@router.post("/open")
async def open_box(
    request: OpenBoxRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await open_mystery_box(request.box_id, current_user["id"], db)
    if not result:
        raise HTTPException(status_code=404, detail="Boîte non trouvée")
    return result


@router.post("/create")
async def create_mystery_box_endpoint(
    rarity: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    box = await create_mystery_box(current_user["id"], rarity, db)
    return box


@router.get("/available")
async def list_available_boxes(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    boxes = await get_available_boxes(current_user["id"], db)
    return {"boxes": boxes}
