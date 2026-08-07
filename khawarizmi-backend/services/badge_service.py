"""
Badge Service — système de 12 badges secrets.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

BADGES = [
    {"code": "night_owl", "icon": "🌙", "title_ar": "البومة الليلية", "desc_ar": "3 تدريبات بعد 22h"},
    {"code": "perseverant", "icon": "🔥", "title_ar": "المثابر", "desc_ar": "30 يوم متتالي من التدريب"},
    {"code": "scholar", "icon": "🎓", "title_ar": "العالم الصغير", "desc_ar": "جميع الأفعال عند 100%"},
    {"code": "bac_champion", "icon": "🏆", "title_ar": "بطل البكالوريا", "desc_ar": "نجحت في البوس النهائي"},
    {"code": "lightning", "icon": "⚡", "title_ar": "سريع البرق", "desc_ar": "إجابة صحيحة في أقل من 30 ثانية"},
    {"code": "diligent", "icon": "📚", "title_ar": "الطالب المثالي", "desc_ar": "50 تدريبا متتاليا"},
    {"code": "spear", "icon": "🎯", "title_ar": "الرمّاح", "desc_ar": "10 تحديات مربوحة متتالية", "sprint2": True},
    {"code": "weekly_star", "icon": "🌟", "title_ar": "نجم الأسبوع", "desc_ar": "Top 3 ترتيب الأسبوع", "sprint2": True},
    {"code": "lion", "icon": "💪", "title_ar": "الأسد", "desc_ar": "Score parfait (100%) على بوس"},
    {"code": "brain", "icon": "🧠", "title_ar": "العقل", "desc_ar": "5 أفعال صعبة mastered", "sprint2": True},
    {"code": "regional", "icon": "🏠", "title_ar": "ابن المنطقة", "desc_ar": "Top 1 ولايتك", "sprint2": True},
    {"code": "generous", "icon": "🎁", "title_ar": "الكريم", "desc_ar": "ساعدت 3 أصدقاء", "sprint2": True},
]


async def get_user_badges(db: AsyncSession, user_id: str) -> list[dict]:
    from models.badge import UserBadge

    result = await db.execute(
        select(UserBadge.badge_code, UserBadge.unlocked_at)
        .where(UserBadge.user_id == user_id)
    )
    unlocked = {row.badge_code: row.unlocked_at.isoformat() for row in result.all()}

    return [
        {
            **badge,
            "unlocked": badge["code"] in unlocked,
            "unlocked_at": unlocked.get(badge["code"]),
        }
        for badge in BADGES
    ]


async def check_and_unlock_badges(db: AsyncSession, user_id: str, event_type: str, event_data: dict = None) -> list[str]:
    from models.badge import UserBadge

    event_data = event_data or {}
    newly_unlocked = []

    existing = await db.execute(
        select(UserBadge.badge_code).where(UserBadge.user_id == user_id)
    )
    owned = {row.badge_code for row in existing.all()}

    for badge in BADGES:
        code = badge["code"]
        if code in owned or badge.get("sprint2"):
            continue

        if _check_condition(code, event_data):
            db.add(UserBadge(user_id=user_id, badge_code=code))
            newly_unlocked.append(code)

    if newly_unlocked:
        await db.commit()

    return newly_unlocked


def _check_condition(code: str, data: dict) -> bool:
    if code == "night_owl":
        hour = data.get("hour", 0)
        count = data.get("late_sessions", 0)
        return hour >= 22 and count >= 3
    if code == "perseverant":
        return data.get("current_streak", 0) >= 30
    if code == "scholar":
        return data.get("all_verbs_100", False)
    if code == "bac_champion":
        return data.get("boss_score", 0) >= 80
    if code == "lightning":
        return data.get("duration_seconds", 999) < 30 and data.get("score", 0) >= 80
    if code == "diligent":
        return data.get("total_evaluations", 0) >= 50
    if code == "lion":
        return data.get("boss_score", 0) == 100
    return False
