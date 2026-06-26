import random
import uuid
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.gamification import MysteryBox

VALID_RARITIES = ("common", "rare", "epic", "legendary")

REWARDS: dict[str, list[dict[str, Any]]] = {
    "common": [
        {"type": "points", "value": 20, "message": "Félicitations ! +20 points"},
        {"type": "points", "value": 30, "message": "Félicitations ! +30 points"},
    ],
    "rare": [
        {"type": "points", "value": 75, "message": "Rare ! +75 points"},
        {"type": "badge", "value": "rare_badge_1", "message": "Badge rare débloqué"},
    ],
    "epic": [
        {"type": "points", "value": 150, "message": "Épique ! +150 points"},
        {"type": "powerup", "value": "double_points_15min", "message": "Power-up : double points 15 min"},
    ],
    "legendary": [
        {"type": "points", "value": 300, "message": "Légendaire ! +300 points"},
        {"type": "badge", "value": "legendary_badge", "message": "Badge légendaire débloqué"},
    ],
}


def _normalize_rarity(rarity: str) -> str:
    return rarity if rarity in VALID_RARITIES else "common"


def _pick_reward(rarity: str) -> dict[str, Any]:
    return dict(random.choice(REWARDS[_normalize_rarity(rarity)]))


def _serialize_box(box: MysteryBox) -> dict[str, Any]:
    return {
        "id": box.id,
        "user_id": box.user_id,
        "rarity": box.rarity or "common",
        "opened": bool(box.opened),
        "content_type": box.content_type,
        "content_value": box.content_value,
        "created_at": box.created_at.isoformat() if box.created_at else None,
    }


async def open_mystery_box(box_id: str, user_id: int, db: AsyncSession) -> dict | None:
    result = await db.execute(
        select(MysteryBox).where(
            MysteryBox.id == box_id,
            MysteryBox.user_id == user_id,
            MysteryBox.opened.is_(False),
        )
    )
    box = result.scalar_one_or_none()
    if not box:
        return None

    reward = box.content_value or _pick_reward(box.rarity or "common")
    box.opened = True
    box.content_type = reward.get("type", box.content_type)
    box.content_value = reward
    await db.commit()

    return {
        "box_id": box.id,
        "rarity": box.rarity or "common",
        "type": reward.get("type", "points"),
        "value": reward.get("value", 0),
        "message": reward.get("message", f"Récompense obtenue : {reward.get('value', '')}"),
    }


async def get_available_boxes(user_id: int, db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(MysteryBox)
        .where(MysteryBox.user_id == user_id, MysteryBox.opened.is_(False))
        .order_by(MysteryBox.created_at.desc())
    )
    boxes = result.scalars().all()
    return [_serialize_box(box) for box in boxes]


async def create_mystery_box(user_id: int, rarity: str, db: AsyncSession) -> dict:
    normalized_rarity = _normalize_rarity(rarity)
    reward = _pick_reward(normalized_rarity)
    box = MysteryBox(
        id=str(uuid.uuid4()),
        user_id=user_id,
        rarity=normalized_rarity,
        opened=False,
        content_type=reward["type"],
        content_value=reward,
        created_at=date.today(),
    )
    db.add(box)
    await db.commit()
    await db.refresh(box)
    return _serialize_box(box)
