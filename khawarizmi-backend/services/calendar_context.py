import logging
from datetime import date

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
    # S3c : stats via le service unifié (même calcul : total, mastered
    # stability > 10, avg_stability) — plus de SQL mastery ici.
    try:
        from services.fsrs_unified import get_concept_stats

        return await get_concept_stats(db, user_id)
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
