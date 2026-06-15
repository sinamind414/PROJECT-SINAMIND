# routes/health.py
# Khawarizmi Pro — Endpoint de santé

from datetime import datetime, timezone
from fastapi import APIRouter
from sqlalchemy import text

from config import get_settings

router = APIRouter()


def _get_state():
    from main import state
    return state


@router.get("/health", tags=["Système"])
async def health_check():
    s = _get_state()
    cfg = get_settings()
    db_ok = False
    redis_ok = False

    if s.db_session:
        try:
            async with s.db_session() as db:
                await db.execute(text("SELECT 1"))
            db_ok = True
        except Exception:
            pass

    if s.redis:
        try:
            await s.redis.ping()
            redis_ok = True
        except Exception:
            pass

    return {
        "status": "healthy" if (db_ok and redis_ok) else "degraded",
        "version": cfg.VERSION,
        "database": "connected" if db_ok else "error",
        "redis": "connected" if redis_ok else "error",
        "ai_model": cfg.AI_MODEL_PRIMARY,
        "fallback_active": not db_ok or not redis_ok,
        "environment": cfg.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
