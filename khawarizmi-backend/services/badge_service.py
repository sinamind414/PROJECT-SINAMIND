from sqlalchemy.ext.asyncio import AsyncSession

BADGES: list[dict] = [
    {"id": "methodology_beginner", "name": "Débutant Méthodologie", "rarity": "common"},
    {"id": "proteins_expert", "name": "Expert Protéines", "rarity": "rare"},
    {"id": "streak_7", "name": "Streak 7 jours", "rarity": "epic"},
    {"id": "methodology_master", "name": "Maître Méthodologie", "rarity": "legendary"},
]


async def check_and_award_badges(user_id: int, db: AsyncSession) -> list[dict]:
    return []


async def get_all_badges() -> list[dict]:
    return list(BADGES)
