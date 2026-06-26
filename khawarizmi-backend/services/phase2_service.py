import random

from sqlalchemy.ext.asyncio import AsyncSession

MYSTERY_BOX_REWARDS: dict[str, list[dict]] = {
    "common": [
        {"type": "points", "value": 20},
        {"type": "points", "value": 30},
    ],
    "rare": [
        {"type": "points", "value": 75},
        {"type": "badge", "value": "rare_badge_1"},
    ],
    "epic": [
        {"type": "points", "value": 150},
        {"type": "powerup", "value": "double_points_15min"},
    ],
    "legendary": [
        {"type": "points", "value": 300},
        {"type": "badge", "value": "legendary_badge"},
    ],
}


async def open_mystery_box_v2(box_id: str, user_id: int, db: AsyncSession) -> dict:
    rarity = random.choice(list(MYSTERY_BOX_REWARDS.keys()))
    reward = random.choice(MYSTERY_BOX_REWARDS[rarity])

    return {
        "rarity": rarity,
        "reward": reward,
        "message": f"Vous avez obtenu {reward['value']} !",
    }


async def get_social_stats(chapter: str, db: AsyncSession) -> dict:
    return {
        "chapter": chapter,
        "active_users_today": 142,
        "completed_today": 87,
        "top_player": "Sarah B.",
    }
