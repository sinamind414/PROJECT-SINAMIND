import logging
from datetime import date

from sqlalchemy import text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("khawarizmi.calendar")


def get_phase_label(days_to_bac: int) -> str:
    if days_to_bac > 90:
        return "Phase 1 : Apprentissage progressif (Septembre - Mars)"
    elif days_to_bac > 15:
        return "Phase 2 : Révisions intensives (Avril - Mai)"
    else:
        return "Phase 3 : Sprint final (J-15 avant le BAC)"


def compute_days_to_bac(today: date | None = None) -> tuple[date, int, str]:
    today = today or date.today()
    year = today.year
    if today.month > 6 or (today.month == 6 and today.day > 10):
        year += 1
    bac_date = date(year, 6, 5)
    days_to_bac = (bac_date - today).days
    phase = get_phase_label(days_to_bac)
    return bac_date, days_to_bac, phase


async def get_user_stats(db: AsyncSession, user_id: int) -> dict:
    try:
        result = await db.execute(
            sa_text("""
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE stability > 10.0) as mastered,
                    COALESCE(AVG(stability), 0.0) as avg_stability
                FROM mastery_micro_concepts
                WHERE user_id = :uid
            """),
            {"uid": user_id},
        )
        row = result.fetchone()
        if row:
            return {
                "total": row[0],
                "mastered": row[1],
                "avg_stability": round(row[2] or 0.0, 1),
            }
    except Exception as e:
        logger.error(f"Erreur stats FSRS: {e}")
    return {"total": 0, "mastered": 0, "avg_stability": 0.0}


async def get_calendar_context(db: AsyncSession, user_id: int) -> dict:
    _, days_to_bac, phase = compute_days_to_bac()
    user_stats = await get_user_stats(db, user_id)
    return {
        "days_to_bac": days_to_bac,
        "phase": phase,
        "user_stats": user_stats,
    }
