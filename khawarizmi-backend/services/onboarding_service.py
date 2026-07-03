"""
Onboarding Service — parcours guidé nouveaux utilisateurs.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.onboarding import UserOnboarding
from services import gems_service


async def get_onboarding_status(db: AsyncSession, user_id: str) -> dict:
    result = await db.execute(select(UserOnboarding).where(UserOnboarding.user_id == user_id))
    ob = result.scalar_one_or_none()

    if ob and ob.step_3_done:
        return {"completed": True, "step_1_done": True, "step_2_done": True, "step_3_done": True}
    if ob:
        return {"completed": False, "step_1_done": ob.step_1_done, "step_2_done": ob.step_2_done, "step_3_done": ob.step_3_done}

    return {"completed": False, "step_1_done": False, "step_2_done": False, "step_3_done": False}


async def mark_step(db: AsyncSession, user_id: str, step: int) -> dict:
    result = await db.execute(select(UserOnboarding).where(UserOnboarding.user_id == user_id))
    ob = result.scalar_one_or_none()

    if not ob:
        ob = UserOnboarding(user_id=user_id)
        db.add(ob)
        await db.flush()

    if step == 1:
        ob.step_1_done = True
    elif step == 2:
        ob.step_2_done = True
    elif step == 3:
        ob.step_3_done = True
        ob.completed_at = func.now()
    else:
        raise ValueError("step must be 1, 2, or 3")

    await db.commit()
    return await get_onboarding_status(db, user_id)


async def award_welcome_gems(db: AsyncSession, user_id: str) -> dict:
    result = await db.execute(select(UserOnboarding).where(UserOnboarding.user_id == user_id))
    ob = result.scalar_one_or_none()

    if not ob:
        ob = UserOnboarding(user_id=user_id)
        db.add(ob)
        await db.flush()

    if ob.welcome_gems_awarded:
        return {"awarded": False, "reason": "already_awarded"}

    await gems_service.add_gems(db, user_id, 5, "welcome_bonus")
    ob.welcome_gems_awarded = True
    await db.commit()
    return {"awarded": True, "amount": 5}
