from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.gamification import UserPoints, UserStreak


async def get_or_create_streak(user_id: int, db: AsyncSession) -> UserStreak:
    result = await db.execute(select(UserStreak).where(UserStreak.user_id == user_id))
    streak = result.scalar_one_or_none()

    if not streak:
        streak = UserStreak(user_id=user_id, current_streak=0, longest_streak=0)
        db.add(streak)
        await db.commit()
        await db.refresh(streak)
    return streak


async def update_streak(user_id: int, db: AsyncSession) -> dict:
    streak = await get_or_create_streak(user_id, db)
    today = date.today()

    if streak.last_activity == today:
        return {"current_streak": streak.current_streak, "updated": False}

    if streak.last_activity == today - timedelta(days=1):
        streak.current_streak += 1
    else:
        streak.current_streak = 1

    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak

    streak.last_activity = today
    await db.commit()

    return {
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "updated": True,
    }


async def add_points(user_id: int, points: int, db: AsyncSession) -> dict:
    result = await db.execute(select(UserPoints).where(UserPoints.user_id == user_id))
    user_points = result.scalar_one_or_none()

    if not user_points:
        user_points = UserPoints(user_id=user_id, total_points=0, weekly_points=0)
        db.add(user_points)

    user_points.total_points += points
    user_points.weekly_points += points
    await db.commit()

    return {"total_points": user_points.total_points}
