# services/payment_service.py
# Point d'entrée Paiement — centralise la logique métier

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging

logger = logging.getLogger("khawarizmi.payment")


async def activate_premium(checkout_id: str, db: AsyncSession) -> bool:
    result = await db.execute(
        text("SELECT user_id FROM payment_checkouts WHERE checkout_id = :cid"),
        {"cid": checkout_id},
    )
    row = result.fetchone()
    if not row:
        logger.warning("Checkout introuvable : %s", checkout_id)
        return False
    user_id = row[0]
    await db.execute(
        text("UPDATE users SET premium = true, premium_since = NOW() WHERE id = :uid"),
        {"uid": user_id},
    )
    await db.commit()
    logger.info("Premium activé pour user %s", user_id)
    return True


async def get_payment_status(checkout_id: str, db: AsyncSession) -> Optional[str]:
    result = await db.execute(
        text("SELECT status FROM payment_checkouts WHERE checkout_id = :cid"),
        {"cid": checkout_id},
    )
    row = result.fetchone()
    return row[0] if row else None


async def is_premium(user_id: int, db: AsyncSession) -> bool:
    result = await db.execute(
        text("SELECT premium FROM users WHERE id = :uid"),
        {"uid": user_id},
    )
    row = result.fetchone()
    return bool(row[0]) if row else False


async def create_checkout(user_id: int, amount: float, db: AsyncSession) -> Optional[str]:
    import uuid
    checkout_id = str(uuid.uuid4())
    await db.execute(
        text("""
            INSERT INTO payment_checkouts (checkout_id, user_id, amount, status)
            VALUES (:cid, :uid, :amt, 'pending')
        """),
        {"cid": checkout_id, "uid": user_id, "amt": amount},
    )
    await db.commit()
    return checkout_id
