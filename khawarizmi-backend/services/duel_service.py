"""
Duel Service — defi 1v1 entre amis.
"""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.duel import Duel


async def create_duel(db: AsyncSession, host_user_id: str, verb_slug: str | None = None) -> dict:
    if not verb_slug:
        verb_slug = "analyse"

    share_token = uuid.uuid4().hex[:12]
    expires_at = datetime.now(UTC) + timedelta(hours=24)

    duel = Duel(
        verb_slug=verb_slug,
        host_user_id=host_user_id,
        share_token=share_token,
        expires_at=expires_at,
        status="pending",
    )
    db.add(duel)
    await db.commit()
    await db.refresh(duel)

    return {
        "duel_id": str(duel.id),
        "share_token": share_token,
        "verb_slug": verb_slug,
        "expires_at": expires_at.isoformat(),
    }


async def get_duel_by_token(db: AsyncSession, share_token: str) -> dict | None:
    result = await db.execute(select(Duel).where(Duel.share_token == share_token))
    duel = result.scalar_one_or_none()
    if not duel:
        return None
    return {
        "duel_id": str(duel.id),
        "verb_slug": duel.verb_slug,
        "host_user_id": str(duel.host_user_id),
        "status": duel.status,
        "expires_at": duel.expires_at.isoformat() if duel.expires_at else None,
    }


async def accept_duel(db: AsyncSession, guest_user_id: str, share_token: str) -> dict:
    result = await db.execute(select(Duel).where(Duel.share_token == share_token))
    duel = result.scalar_one_or_none()

    if not duel:
        raise ValueError("Duel introuvable")
    if duel.expires_at and duel.expires_at < datetime.now(UTC):
        raise ValueError("Duel expiré")
    if str(duel.host_user_id) == guest_user_id:
        raise ValueError("Tu ne peux pas te défier toi-même")

    duel.guest_user_id = guest_user_id
    duel.status = "in_progress"
    await db.commit()

    return {
        "duel_id": str(duel.id),
        "verb_slug": duel.verb_slug,
        "status": "in_progress",
    }


async def submit_duel_answer(db: AsyncSession, user_id: str, duel_id: str, score: int) -> dict:
    result = await db.execute(select(Duel).where(Duel.id == duel_id))
    duel = result.scalar_one_or_none()

    if not duel:
        raise ValueError("Duel introuvable")

    now = datetime.now(UTC)
    is_host = str(duel.host_user_id) == user_id

    if is_host:
        duel.host_score = score
        duel.host_completed_at = now
    else:
        duel.guest_score = score
        duel.guest_completed_at = now

    both_submitted = duel.host_score is not None and duel.guest_score is not None

    if both_submitted:
        duel.status = "completed"
        if (duel.guest_score or 0) > (duel.host_score or 0):
            duel.winner_user_id = duel.guest_user_id
        else:
            duel.winner_user_id = duel.host_user_id

    await db.commit()

    return {
        "score": score,
        "both_submitted": both_submitted,
        "winner_id": str(duel.winner_user_id) if duel.winner_user_id else None,
        "host_score": duel.host_score,
        "guest_score": duel.guest_score,
        "status": duel.status,
    }


async def get_duel_status(db: AsyncSession, duel_id: str) -> dict:
    result = await db.execute(select(Duel).where(Duel.id == duel_id))
    duel = result.scalar_one_or_none()
    if not duel:
        return {"status": "not_found"}

    return {
        "status": duel.status,
        "host_score": duel.host_score,
        "guest_score": duel.guest_score,
        "winner_id": str(duel.winner_user_id) if duel.winner_user_id else None,
        "both_submitted": duel.host_score is not None and duel.guest_score is not None,
    }


async def get_leaderboard(db: AsyncSession, limit: int = 20) -> list[dict]:
    from sqlalchemy import func

    result = await db.execute(
        select(
            Duel.winner_user_id,
            func.count(Duel.id).label("wins")
        )
        .where(Duel.status == "completed")
        .where(Duel.winner_user_id.isnot(None))
        .group_by(Duel.winner_user_id)
        .order_by(func.count(Duel.id).desc())
        .limit(limit)
    )

    return [
        {"user_id": str(row.winner_user_id), "wins": row.wins}
        for row in result.all()
    ]
