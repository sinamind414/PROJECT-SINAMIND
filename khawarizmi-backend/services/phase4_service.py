from sqlalchemy.ext.asyncio import AsyncSession

METHODOLOGY_BADGES: dict[str, dict] = {
    "methodology_beginner": {
        "name": "Débutant Méthodologie",
        "description": "Utilise correctement 10 verbes d'action",
        "rarity": "common",
        "points": 50,
    },
    "structure_master": {
        "name": "Maître de la Structure",
        "description": "Obtiens 80% sur Introduction / Développement / Conclusion",
        "rarity": "rare",
        "points": 150,
    },
    "methodology_expert": {
        "name": "Expert Méthodologie",
        "description": "Réussis 50 réponses méthodologiques",
        "rarity": "epic",
        "points": 300,
    },
    "bac_champion": {
        "name": "Champion du Bac",
        "description": "Atteins le niveau Expert en méthodologie",
        "rarity": "legendary",
        "points": 500,
    },
}

POINTS_MAP: dict[str, int] = {
    "excellent": 30,
    "good": 15,
    "average": 8,
    "poor": 3,
}


async def check_methodology_badges(user_id: int, db: AsyncSession) -> list:
    return []


async def award_methodology_points(user_id: int, verb: str, quality: str, db: AsyncSession) -> dict:
    points = POINTS_MAP.get(quality, 5)

    return {
        "points": points,
        "message": f"+{points} points pour une réponse {quality} sur le verbe {verb}",
    }
