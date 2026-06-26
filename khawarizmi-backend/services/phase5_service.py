from sqlalchemy.ext.asyncio import AsyncSession


async def get_live_classroom_stats(chapter: str, db: AsyncSession) -> dict:
    return {
        "active_students": 47,
        "questions_answered": 312,
        "top_3": [
            {"name": "Sarah B.", "score": 1240},
            {"name": "Karim M.", "score": 1190},
            {"name": "Yasmine K.", "score": 1085},
        ],
    }


async def get_friend_activity(user_id: int, db: AsyncSession) -> list[dict]:
    return [
        {"name": "Sarah", "action": "a terminé le défi du jour", "time": "il y a 8 min"},
        {"name": "Karim", "action": "a débloqué le badge Expert ADN", "time": "il y a 22 min"},
    ]


async def create_challenge(user_id: int, friend_id: str, db: AsyncSession) -> dict:
    return {
        "challenge_id": "ch_12345",
        "status": "pending",
        "message": "Défi envoyé à ton ami !",
    }
