from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.phase1 import ComboState

NEXT_ACTIONS = [
    {
        "title": "Continuer sur ce chapitre",
        "description": "Passe au concept suivant",
        "action": "next_lesson",
        "icon": "📖",
        "points": 15,
    },
    {
        "title": "Faire un quiz rapide",
        "description": "Teste tes connaissances",
        "action": "quick_quiz",
        "icon": "📝",
        "points": 25,
    },
    {
        "title": "Défi du jour",
        "description": "Gagne des points bonus",
        "action": "daily_challenge",
        "icon": "🔥",
        "points": 40,
    },
]


async def get_next_actions(user_id: int, last_action: str, db: AsyncSession) -> list[dict]:
    return list(NEXT_ACTIONS)


async def get_or_create_combo(user_id: int, db: AsyncSession) -> ComboState:
    result = await db.execute(select(ComboState).where(ComboState.user_id == user_id))
    combo = result.scalar_one_or_none()
    if not combo:
        combo = ComboState(user_id=user_id, current_combo=0, max_combo=0)
        db.add(combo)
        await db.commit()
        await db.refresh(combo)
    return combo


async def calculate_combo(user_id: int, success: bool, db: AsyncSession) -> dict:
    combo = await get_or_create_combo(user_id, db)

    if success:
        combo.current_combo += 1
        if combo.current_combo > combo.max_combo:
            combo.max_combo = combo.current_combo
        multiplier = min(1 + combo.current_combo // 3, 5)
        points_earned = 10 * multiplier
        await db.commit()
        return {
            "multiplier": multiplier,
            "points_earned": points_earned,
            "combo_count": combo.current_combo,
            "message": f"Combo x{multiplier} !",
        }

    combo.current_combo = 0
    await db.commit()
    return {
        "multiplier": 1,
        "points_earned": 0,
        "combo_count": 0,
        "message": "Combo cassé. Réessaie !",
    }
