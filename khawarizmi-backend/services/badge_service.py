from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.gamification import Badge, UserAvatar, UserBadge, UserPoints, UserStreak

BADGES: list[dict[str, Any]] = [
    {
        "id": "methodology_beginner",
        "name": "Débutant Méthodologie",
        "description": "Utilise correctement tes premières méthodes de réponse",
        "rarity": "common",
        "icon": "📘",
    },
    {
        "id": "points_100",
        "name": "100 points",
        "description": "Atteins 100 points cumulés",
        "rarity": "common",
        "icon": "⭐",
    },
    {
        "id": "proteins_expert",
        "name": "Expert Protéines",
        "description": "Progresse fortement sur le chapitre des protéines",
        "rarity": "rare",
        "icon": "🧬",
    },
    {
        "id": "streak_7",
        "name": "Streak 7 jours",
        "description": "Révise 7 jours de suite",
        "rarity": "epic",
        "icon": "🔥",
    },
    {
        "id": "avatar_level_3",
        "name": "Avatar Chercheur",
        "description": "Atteins le niveau avatar 3",
        "rarity": "rare",
        "icon": "🔬",
    },
    {
        "id": "methodology_master",
        "name": "Maître Méthodologie",
        "description": "Maîtrise les réflexes méthodologiques clés",
        "rarity": "legendary",
        "icon": "🏆",
    },
]

BADGE_BY_ID = {badge["id"]: badge for badge in BADGES}


def _serialize_badge(badge: Badge | dict[str, Any], unlocked: bool = False) -> dict[str, Any]:
    if isinstance(badge, dict):
        data = dict(badge)
    else:
        data = {
            "id": badge.id,
            "name": badge.name,
            "description": badge.description,
            "rarity": badge.rarity,
            "icon": badge.icon,
        }
    data["unlocked"] = unlocked
    return data


async def _ensure_badges(db: AsyncSession) -> None:
    for badge_data in BADGES:
        result = await db.execute(select(Badge).where(Badge.id == badge_data["id"]))
        if result.scalar_one_or_none():
            continue
        db.add(
            Badge(
                id=badge_data["id"],
                name=badge_data["name"],
                description=badge_data.get("description"),
                rarity=badge_data.get("rarity"),
                icon=badge_data.get("icon"),
            )
        )
    await db.commit()


async def _unlock_badge(user_id: int, badge_id: str, db: AsyncSession) -> dict[str, Any] | None:
    badge_data = BADGE_BY_ID.get(badge_id)
    if not badge_data:
        return None

    result = await db.execute(select(UserBadge).where(UserBadge.user_id == user_id, UserBadge.badge_id == badge_id))
    if result.scalar_one_or_none():
        return None

    db.add(UserBadge(user_id=user_id, badge_id=badge_id, unlocked_at=date.today()))
    await db.commit()
    return _serialize_badge(badge_data, unlocked=True)


async def check_and_award_badges(user_id: int, db: AsyncSession) -> list[dict]:
    await _ensure_badges(db)
    awarded: list[dict] = []

    points_result = await db.execute(select(UserPoints).where(UserPoints.user_id == user_id))
    points = points_result.scalar_one_or_none()
    if points and points.total_points >= 100:
        badge = await _unlock_badge(user_id, "points_100", db)
        if badge:
            awarded.append(badge)

    streak_result = await db.execute(select(UserStreak).where(UserStreak.user_id == user_id))
    streak = streak_result.scalar_one_or_none()
    if streak and streak.longest_streak >= 7:
        badge = await _unlock_badge(user_id, "streak_7", db)
        if badge:
            awarded.append(badge)

    avatar_result = await db.execute(select(UserAvatar).where(UserAvatar.user_id == user_id))
    avatar = avatar_result.scalar_one_or_none()
    if avatar and avatar.level >= 3:
        badge = await _unlock_badge(user_id, "avatar_level_3", db)
        if badge:
            awarded.append(badge)

    return awarded


async def get_all_badges() -> list[dict]:
    return [_serialize_badge(badge) for badge in BADGES]
