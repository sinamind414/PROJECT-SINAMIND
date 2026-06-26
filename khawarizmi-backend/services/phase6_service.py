from sqlalchemy.ext.asyncio import AsyncSession


async def get_gamification_metrics(db: AsyncSession) -> dict:
    return {
        "daily_active_users": 1240,
        "average_session_duration": 18.5,
        "streak_retention_j3": 72,
        "streak_retention_j7": 51,
        "average_clicks_per_session": 27,
        "mystery_box_open_rate": 68,
        "one_more_click_conversion": 84,
    }


async def get_user_engagement(user_id: int, db: AsyncSession) -> dict:
    return {
        "total_sessions": 47,
        "average_session_time": 21,
        "most_played_chapter": "Protéines",
        "favorite_feature": "Mystery Box",
        "current_streak": 14,
    }


async def get_top_performers(limit: int = 10, db: AsyncSession | None = None) -> list[dict]:
    return [
        {"name": "Sarah B.", "points": 8740, "level": 6},
        {"name": "Karim M.", "points": 8120, "level": 6},
        {"name": "Yasmine K.", "points": 7950, "level": 5},
    ][:limit]
