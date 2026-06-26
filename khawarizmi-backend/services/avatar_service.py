from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.gamification import UserAvatar

LEVELS = [0, 200, 600, 1200, 2500, 4500]


async def get_user_avatar(user_id: int, db: AsyncSession) -> UserAvatar:
    result = await db.execute(select(UserAvatar).where(UserAvatar.user_id == user_id))
    avatar = result.scalar_one_or_none()

    if not avatar:
        avatar = UserAvatar(user_id=user_id, level=1, xp=0)
        db.add(avatar)
        await db.commit()
        await db.refresh(avatar)

    return avatar


async def add_xp(user_id: int, xp: int, db: AsyncSession) -> dict:
    avatar = await get_user_avatar(user_id, db)
    avatar.xp += xp

    new_level = 1
    for i, threshold in enumerate(LEVELS[1:], 1):
        if avatar.xp >= threshold:
            new_level = i + 1

    old_level = avatar.level
    avatar.level = new_level
    await db.commit()

    return {
        "level": avatar.level,
        "xp": avatar.xp,
        "leveled_up": new_level > old_level,
    }
