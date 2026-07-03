"""
Gems Service — monnaie interne (gemmes).
"""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.gems import UserGems, GemTransaction


async def get_user_gems(db: AsyncSession, user_id: str) -> dict:
    result = await db.execute(select(UserGems).where(UserGems.user_id == user_id))
    gems = result.scalar_one_or_none()
    if not gems:
        gems = UserGems(user_id=user_id, balance=0, total_earned=0, total_spent=0)
        db.add(gems)
        await db.commit()
        await db.refresh(gems)
    return {
        "balance": gems.balance,
        "total_earned": gems.total_earned,
        "total_spent": gems.total_spent,
    }


async def add_gems(db: AsyncSession, user_id: str, amount: int, reason: str, reference_id: str | None = None) -> dict:
    if amount <= 0:
        raise ValueError("amount must be positive")

    result = await db.execute(select(UserGems).where(UserGems.user_id == user_id))
    gems = result.scalar_one_or_none()

    if not gems:
        gems = UserGems(user_id=user_id, balance=0, total_earned=0, total_spent=0)
        db.add(gems)
        await db.flush()

    gems.balance += amount
    gems.total_earned += amount

    db.add(GemTransaction(user_id=user_id, amount=amount, reason=reason, reference_id=reference_id))
    await db.commit()
    return {"balance": gems.balance, "total_earned": gems.total_earned, "total_spent": gems.total_spent}


async def spend_gems(db: AsyncSession, user_id: str, amount: int, reason: str, reference_id: str | None = None) -> dict:
    if amount <= 0:
        raise ValueError("amount must be positive")

    result = await db.execute(select(UserGems).where(UserGems.user_id == user_id))
    gems = result.scalar_one_or_none()

    if not gems or gems.balance < amount:
        raise ValueError("Solde insuffisant")

    gems.balance -= amount
    gems.total_spent += amount

    db.add(GemTransaction(user_id=user_id, amount=-amount, reason=reason, reference_id=reference_id))
    await db.commit()
    return {"balance": gems.balance, "total_earned": gems.total_earned, "total_spent": gems.total_spent}


async def get_transactions(db: AsyncSession, user_id: str, limit: int = 20) -> list[dict]:
    result = await db.execute(
        select(GemTransaction)
        .where(GemTransaction.user_id == user_id)
        .order_by(GemTransaction.created_at.desc())
        .limit(limit)
    )
    return [
        {
            "amount": tx.amount,
            "reason": tx.reason,
            "reference_id": tx.reference_id,
            "created_at": tx.created_at.isoformat() if tx.created_at else None,
        }
        for tx in result.scalars().all()
    ]


async def get_gems_leaderboard(db: AsyncSession, limit: int = 50) -> list[dict]:
    result = await db.execute(
        select(UserGems)
        .order_by(UserGems.balance.desc())
        .limit(limit)
    )
    return [
        {"user_id": str(g.user_id), "balance": g.balance, "total_earned": g.total_earned}
        for g in result.scalars().all()
    ]
