"""
Streak Service — gestion de la série quotidienne d'entraînement.
"""

from datetime import date, timedelta
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


async def get_user_streak(db: AsyncSession, user_id: str) -> dict:
    from models.streak import ActionVerbStreak

    result = await db.execute(
        select(ActionVerbStreak).where(ActionVerbStreak.user_id == user_id)
    )
    streak = result.scalar_one_or_none()

    if not streak:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "last_active_date": None,
            "freezes_remaining": 1,
            "can_use_freeze": False,
            "status": "inactive",
        }

    today = date.today()
    can_use_freeze = (
        streak.freezes_remaining > 0
        and streak.last_active_date is not None
        and streak.last_active_date < today - timedelta(days=1)
    )

    status = "active"
    if streak.last_active_date is None:
        status = "inactive"
    elif streak.last_active_date == today:
        status = "active"
    elif streak.last_active_date == today - timedelta(days=1):
        status = "active"
    else:
        status = "broken"

    return {
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "last_active_date": streak.last_active_date.isoformat() if streak.last_active_date else None,
        "freezes_remaining": streak.freezes_remaining,
        "can_use_freeze": can_use_freeze,
        "status": status,
    }


async def record_activity(db: AsyncSession, user_id: str) -> dict:
    from models.streak import ActionVerbStreak

    today = date.today()
    yesterday = today - timedelta(days=1)

    result = await db.execute(
        select(ActionVerbStreak).where(ActionVerbStreak.user_id == user_id)
    )
    streak = result.scalar_one_or_none()

    if not streak:
        streak = ActionVerbStreak(
            user_id=user_id,
            current_streak=1,
            longest_streak=1,
            last_active_date=today,
            freezes_remaining=1,
            freezes_used_this_week=0,
            week_start_date=today - timedelta(days=today.weekday()),
        )
        db.add(streak)
        await db.commit()
        return await get_user_streak(db, user_id)

    if streak.last_active_date == today:
        return await get_user_streak(db, user_id)

    # Reset weekly freezes if new week
    week_start = today - timedelta(days=today.weekday())
    if streak.week_start_date != week_start:
        streak.freezes_used_this_week = 0
        streak.week_start_date = week_start

    if streak.last_active_date == yesterday:
        streak.current_streak += 1
    else:
        streak.current_streak = 1

    streak.last_active_date = today
    streak.longest_streak = max(streak.longest_streak, streak.current_streak)

    await db.commit()
    return await get_user_streak(db, user_id)


async def use_freeze(db: AsyncSession, user_id: str) -> bool:
    from models.streak import ActionVerbStreak

    today = date.today()

    result = await db.execute(
        select(ActionVerbStreak).where(ActionVerbStreak.user_id == user_id)
    )
    streak = result.scalar_one_or_none()

    if not streak or streak.freezes_remaining <= 0:
        return False

    if streak.last_active_date and streak.last_active_date >= today - timedelta(days=1):
        return False

    streak.freezes_remaining -= 1
    streak.freezes_used_this_week += 1
    streak.last_active_date = yesterday
    streak.current_streak += 1
    streak.longest_streak = max(streak.longest_streak, streak.current_streak)

    await db.commit()
    return True
