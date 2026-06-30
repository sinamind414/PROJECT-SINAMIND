import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db, get_scheduler
from services.progress_snapshots import get_progress_snapshot, get_week_activity_snapshot

logger = logging.getLogger("khawarizmi.api")
router = APIRouter()


@router.get("/api/progress", tags=["Progression"])
async def get_progression(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    scheduler = get_scheduler()
    snap = await get_progress_snapshot(db, current_user["id"], scheduler)

    if not snap.get("concepts"):
        return {
            "message": "Aucune progression enregistrée",
            "concepts": [],
            "prediction_bac": None,
        }

    return {
        "user_id": current_user["id"],
        "nb_concepts": snap["nb_concepts"],
        "dues_aujourd_hui": snap["dues_aujourd_hui"],
        "prediction_bac": snap["prediction_bac"],
        "concepts": snap["concepts"],
    }


@router.get("/api/week-activity", tags=["Progression"])
async def get_week_activity(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    snap = await get_week_activity_snapshot(db, current_user["id"])
    return {"user_id": current_user["id"], **snap}
