from sqlalchemy.ext.asyncio import AsyncSession


async def open_mystery_box(box_id: str, user_id: int, db: AsyncSession) -> dict | None:
    return {
        "type": "points",
        "value": 50,
        "message": "Félicitations ! +50 points",
    }


async def get_available_boxes(user_id: int, db: AsyncSession) -> list:
    return []


async def create_mystery_box(user_id: int, rarity: str, db: AsyncSession) -> dict:
    return {
        "id": "new-box-id",
        "user_id": user_id,
        "rarity": rarity,
        "opened": False,
    }
