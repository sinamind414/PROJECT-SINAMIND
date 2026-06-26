from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db
from services.phase2_service import get_social_stats, open_mystery_box_v2

router = APIRouter(prefix="/api/phase2", tags=["Phase 2 - Mystery & Social"])


class OpenBoxRequest(BaseModel):
    box_id: str


@router.post("/mystery-box/open")
async def open_mystery_box_endpoint(
    request: OpenBoxRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await open_mystery_box_v2(request.box_id, current_user["id"], db)
    return result


@router.get("/social-stats/{chapter}")
async def social_stats(
    chapter: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stats = await get_social_stats(chapter, db)
    return stats
