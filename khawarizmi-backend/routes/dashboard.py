import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db, get_scheduler
from services.dashboard_orchestrator import build_dashboard_orchestrator

logger = logging.getLogger("khawarizmi.api")
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/orchestrator")
async def get_dashboard_orchestrator(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    scheduler = get_scheduler()
    payload = await build_dashboard_orchestrator(db, current_user, scheduler)
    logger.info(
        "Dashboard orchestrator: user=%s recs=%s due_today=%s",
        current_user["id"],
        len(payload.get("orientation", {}).get("recommendations", [])),
        payload.get("progress", {}).get("dues_aujourd_hui", 0),
    )
    return payload
