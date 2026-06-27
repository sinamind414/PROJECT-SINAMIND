# routes/health.py
# Khawarizmi Pro — Endpoint de santé

from datetime import UTC, datetime

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

    now = datetime.now(UTC)
    backup_info = _check_backup_status()

    # Santé métier
    from services.questions import questions_db
    business = {
        "questions_loaded": len(questions_db),
        "openai_configured": s.openai is not None,
        "scheduler_initialized": s.scheduler is not None,
        "tutor_initialized": s.tutor is not None,
        "dual_coding_configured": s.dual_coding is not None,
    }

    # rag_chunks count (si DB disponible)
    if db_ok and s.db_session:
        try:
            async with s.db_session() as db:
                result = await db.execute(text("SELECT COUNT(*) FROM rag_chunks"))
                business["rag_chunks_count"] = result.scalar() or 0
        except Exception:
            business["rag_chunks_count"] = -1  # table inexistante

    return {
        "status": "healthy" if (db_ok and redis_ok) else "degraded",
        "version": cfg.VERSION,
        "database": "connected" if db_ok else "error",
        "redis": "connected" if redis_ok else "error",
        "ai_model": cfg.AI_MODEL_PRIMARY,
        "fallback_active": not db_ok or not redis_ok,
        "backup": backup_info,
        "business": business,
        "environment": cfg.ENVIRONMENT,
        "timestamp": now.isoformat(),
    }


def _check_backup_status():
    import os
    import pathlib

    backup_dir = pathlib.Path(os.environ.get("BACKUP_DIR", "backups"))
    if not backup_dir.exists():
        backup_dir = pathlib.Path(__file__).parent.parent / "backups"
    if not backup_dir.exists():
        return {"status": "not_configured", "last_backup": None}

    backups = sorted(backup_dir.glob("*.sql.gz"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not backups:
        return {"status": "no_backups", "last_backup": None}

    latest = backups[0]
    age_hours = (datetime.now(UTC) - datetime.fromtimestamp(latest.stat().st_mtime, tz=UTC)).total_seconds() / 3600
    return {
        "status": "ok" if age_hours < 30 else "stale",
        "last_backup": latest.name,
        "age_hours": round(age_hours, 1),
        "count": len(backups),
        "directory": str(backup_dir.absolute()),
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

    return {"timestamp": datetime.now(UTC).isoformat(), "stats": get_global_stats()}


@router.get("/api/calibration/stats", tags=["Système"])
async def get_calibration_stats():
    """Statistiques du calibrage Eval — Golden Set ONEC."""
    from services.eval_calibration import get_calibration_stats

    return {"timestamp": datetime.now(UTC).isoformat(), "golden_set": get_calibration_stats()}
