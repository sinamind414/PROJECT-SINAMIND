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


@router.get("/debug/data-foundation", tags=["Debug"])
async def data_foundation_debug():
    """Endpoint de debug pour voir l'état des données canoniques vs legacy."""
    s = _get_state()
    foundation = {"timestamp": "2026-06-20"}
    try:
        if s.tutor and hasattr(s.tutor, "loader"):
            foundation["data"] = s.tutor.loader.get_data_foundation_report()
            foundation["tutor"] = {
                "micro_concepts": len(getattr(s.tutor, "_index_micro_concepts", {})),
            }
    except Exception as e:
        foundation["error"] = str(e)
    return foundation


@router.get("/api/metrics", tags=["Système"])
async def get_metrics():
    """Métriques d'observabilité — cache hit rate, fallback rate, compteurs."""
    from services.metrics import get_global_stats
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stats": get_global_stats()
    }


@router.get("/api/calibration/stats", tags=["Système"])
async def get_calibration_stats():
    """Statistiques du calibrage Eval — Golden Set ONEC."""
    from services.eval_calibration import get_calibration_stats
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "golden_set": get_calibration_stats()
    }
