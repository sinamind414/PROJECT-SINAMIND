from sqlalchemy.ext.asyncio import AsyncSession

AVATAR_LEVELS: dict[int, dict] = {
    1: {"name": "Cellule", "icon": "🧬", "color": "#67E8F9"},
    2: {"name": "Étudiant", "icon": "👨‍🎓", "color": "#A5B4FC"},
    3: {"name": "Chercheur", "icon": "🔬", "color": "#818CF8"},
    4: {"name": "Assistant", "icon": "🧪", "color": "#6366F1"},
    5: {"name": "Expert", "icon": "🧠", "color": "#4F46E5"},
    6: {"name": "Professeur", "icon": "👨‍🏫", "color": "#4338CA"},
}


async def get_avatar_details(user_id: int, db: AsyncSession) -> dict:
    return {
        "level": 4,
        "xp": 1240,
        "max_xp": 1500,
        "name": "Dr. Ahmed",
        "icon": AVATAR_LEVELS[4]["icon"],
        "color": AVATAR_LEVELS[4]["color"],
    }


async def get_live_stats(chapter: str, db: AsyncSession) -> dict:
    return {
        "active_users": 87,
        "completed_today": 142,
        "top_3": ["Sarah B.", "Karim M.", "Yasmine K."],
    }


async def get_friends_activity(user_id: int, db: AsyncSession) -> list[dict]:
    return [
        {"name": "Sarah", "action": "a débloqué le badge Expert Protéines", "time": "il y a 12 min"},
        {"name": "Karim", "action": "a terminé le chapitre Mitose", "time": "il y a 34 min"},
    ]
